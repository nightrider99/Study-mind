from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user_id
from app.database.connection import get_supabase
from app.schemas.note import NoteCreate, NoteUpdate, NoteOut

router = APIRouter()

@router.get("", response_model=list[NoteOut])
def list_notes(user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = (
        sb.table("notes").select("*").eq("user_id", user_id)
        .order("updated_at", desc=True).execute()
    )
    return res.data

@router.post("", response_model=NoteOut, status_code=201)
def create_note(body: NoteCreate, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = sb.table("notes").insert({"user_id": user_id, **body.model_dump()}).execute()
    return res.data[0]

@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: str, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = sb.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return res.data[0]

@router.patch("/{note_id}", response_model=NoteOut)
def update_note(note_id: str, body: NoteUpdate, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty patch")
    res = (
        sb.table("notes").update(patch)
        .eq("id", note_id).eq("user_id", user_id).execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return res.data[0]

@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: str, user_id: str = Depends(get_current_user_id)):
    sb = get_supabase()
    res = sb.table("notes").delete().eq("id", note_id).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
