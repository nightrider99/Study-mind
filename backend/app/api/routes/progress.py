from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user_id
from app.schemas.progress import ProgressSummary, TimelineOut
from app.services.progress_service import get_summary, get_timeline

router = APIRouter()


@router.get("/summary", response_model=ProgressSummary)
def summary(user_id: str = Depends(get_current_user_id)):
    return get_summary(user_id)


@router.get("/timeline", response_model=TimelineOut)
def timeline(
    days: int = Query(default=30, ge=7, le=180),
    user_id: str = Depends(get_current_user_id),
):
    return {"days": get_timeline(user_id, days)}
