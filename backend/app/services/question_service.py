import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionService:

    @staticmethod
    async def create(db: AsyncSession, data: QuestionCreate) -> Question:
        q = Question(**data.model_dump())
        db.add(q)
        await db.flush()
        await db.refresh(q)
        return q

    @staticmethod
    async def get(db: AsyncSession, question_id: uuid.UUID) -> Question | None:
        result = await db.execute(select(Question).where(Question.id == question_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession, limit: int = 50, offset: int = 0) -> list[Question]:
        result = await db.execute(
            select(Question).order_by(Question.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession, question_id: uuid.UUID, data: QuestionUpdate
    ) -> Question | None:
        q = await QuestionService.get(db, question_id)
        if not q:
            return None
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(q, field, value)
        await db.flush()
        await db.refresh(q)
        return q

    @staticmethod
    async def delete(db: AsyncSession, question_id: uuid.UUID) -> bool:
        q = await QuestionService.get(db, question_id)
        if not q:
            return False
        await db.delete(q)
        return True
