import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.master_answer import MasterAnswerCreate, MasterAnswerRead
from app.services.master_answer_service import MasterAnswerService
from app.services.question_service import QuestionService

router = APIRouter()


@router.post(
    "/{question_id}/master-answer",
    response_model=MasterAnswerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_master_answer(
    question_id: uuid.UUID,
    data: MasterAnswerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Step 02 — Create or update master answer for a question."""
    q = await QuestionService.get(db, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return await MasterAnswerService.create(db, question_id, data)


@router.get("/{question_id}/master-answer", response_model=MasterAnswerRead)
async def get_active_master_answer(
    question_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    ma = await MasterAnswerService.get_active(db, question_id)
    if not ma:
        raise HTTPException(status_code=404, detail="No active master answer found")
    return ma


@router.get(
    "/{question_id}/master-answer/history", response_model=list[MasterAnswerRead]
)
async def get_master_answer_history(
    question_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await MasterAnswerService.list_for_question(db, question_id)
