import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.review import ReviewItemRead, ReviewResolveRequest
from app.services.review_service import ReviewService

router = APIRouter()


@router.get("/", response_model=list[ReviewItemRead])
async def list_review_queue(db: AsyncSession = Depends(get_db)):
    """Step 13 — Get all pending items in the human review queue."""
    return await ReviewService.list_pending(db)


@router.post("/{item_id}/resolve", response_model=ReviewItemRead)
async def resolve_review_item(
    item_id: uuid.UUID,
    data: ReviewResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Step 13 — Teacher resolves a flagged evaluation with an override label."""
    item = await ReviewService.resolve(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")
    return item
