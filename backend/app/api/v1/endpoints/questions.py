import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionRead
from app.services.question_service import QuestionService

router = APIRouter()


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(data: QuestionCreate, db: AsyncSession = Depends(get_db)):
    """Step 01 — Create a question."""
    return await QuestionService.create(db, data)


@router.get("/", response_model=list[QuestionRead])
async def list_questions(
    limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    return await QuestionService.list_all(db, limit, offset)


@router.get("/{question_id}", response_model=QuestionRead)
async def get_question(question_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    q = await QuestionService.get(db, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@router.patch("/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: uuid.UUID, data: QuestionUpdate, db: AsyncSession = Depends(get_db)
):
    q = await QuestionService.update(db, question_id, data)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await QuestionService.delete(db, question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
