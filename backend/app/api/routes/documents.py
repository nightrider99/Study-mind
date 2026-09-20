from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.security import get_current_user_id
from app.database.connection import get_supabase
from app.schemas.document import DocumentOut
from app.services.embedding_service import embed_documents, to_pgvector
from app.services.pdf_service import chunk_text, parse_pdf

router = APIRouter()

ALLOWED_MIME = {"application/pdf"}
MAX_BYTES = 20 * 1024 * 1024   # 20 MB — comfortably under Supabase free-tier limits
CHUNK_INSERT_BATCH = 50


@router.get("", response_model=list[DocumentOut])
def list_documents(user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = (
        sb.table("documents").select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only PDF supported")
    data = await file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty file")
    if len(data) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Max 20 MB")

    sb = get_supabase()

    # 1) Row first so we have the id for the storage path.
    doc = (
        sb.table("documents")
        .insert(
            {
                "user_id": user_id,
                "filename": file.filename or "document.pdf",
                "mime_type": file.content_type,
                "size_bytes": len(data),
                "status": "processing",
            }
        )
        .execute()
        .data[0]
    )
    doc_id = doc["id"]
    storage_path = f"{user_id}/{doc_id}.pdf"

    # 2) Upload to Supabase Storage.
    try:
        sb.storage.from_(settings.supabase_storage_bucket).upload(
            storage_path,
            data,
            {"content-type": "application/pdf", "upsert": "true"},
        )
        sb.table("documents").update({"storage_path": storage_path}).eq("id", doc_id).execute()
    except Exception as e:
        sb.table("documents").update({"status": "failed", "error": f"upload: {e}"}).eq("id", doc_id).execute()
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Storage upload failed: {e}")

    # 3) Parse -> chunk -> embed -> insert.
    #    Synchronous for MVP. If upload latency becomes annoying, move this
    #    block behind FastAPI BackgroundTasks or a worker.
    try:
        parsed = parse_pdf(data)
        if not parsed.text.strip():
            raise ValueError("No extractable text (scanned PDFs need OCR)")

        chunks = chunk_text(
            parsed.text,
            settings.chunk_size_words,
            settings.chunk_overlap_words,
        )
        embeddings = embed_documents(chunks)
        if len(embeddings) != len(chunks):
            raise RuntimeError("Embedding count mismatch")

        rows = [
            {
                "document_id": doc_id,
                "user_id": user_id,
                "content": c,
                "chunk_index": i,
                "token_count": int(len(c.split()) * 4 / 3),
                "embedding": to_pgvector(emb),
            }
            for i, (c, emb) in enumerate(zip(chunks, embeddings))
        ]
        for i in range(0, len(rows), CHUNK_INSERT_BATCH):
            sb.table("chunks").insert(rows[i : i + CHUNK_INSERT_BATCH]).execute()

        sb.table("documents").update(
            {"status": "ready", "page_count": parsed.page_count, "error": None}
        ).eq("id", doc_id).execute()
    except Exception as e:
        sb.table("documents").update({"status": "failed", "error": str(e)}).eq("id", doc_id).execute()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Processing failed: {e}")

    return sb.table("documents").select("*").eq("id", doc_id).execute().data[0]


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = (
        sb.table("documents").select("*")
        .eq("id", doc_id).eq("user_id", user_id).execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return res.data[0]


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = (
        sb.table("documents").select("storage_path")
        .eq("id", doc_id).eq("user_id", user_id).execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    path = res.data[0]["storage_path"]
    if path:
        try:
            sb.storage.from_(settings.supabase_storage_bucket).remove([path])
        except Exception:
            pass  # orphaned file is not fatal; chunks cascade below

    # chunks cascade via FK
    sb.table("documents").delete().eq("id", doc_id).eq("user_id", user_id).execute()

from app.services.progress_service import log_event
log_event(user_id, "doc_upload", doc_id, None)
