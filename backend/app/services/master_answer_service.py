import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.master_answer import MasterAnswer
from app.schemas.master_answer import MasterAnswerCreate


class MasterAnswerService:

    @staticmethod
    async def create(
        db: AsyncSession, question_id: uuid.UUID, data: MasterAnswerCreate
    ) -> MasterAnswer:
        # Deactivate any existing active answers for this question
        await db.execute(
            update(MasterAnswer)
            .where(MasterAnswer.question_id == question_id, MasterAnswer.is_active == True)
            .values(is_active=False)
        )
        # Get next version number
        result = await db.execute(
            select(MasterAnswer)
            .where(MasterAnswer.question_id == question_id)
            .order_by(MasterAnswer.version.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        next_version = (latest.version + 1) if latest else 1

        ma = MasterAnswer(
            question_id=question_id,
            version=next_version,
            is_active=True,
            **data.model_dump(),
        )
        db.add(ma)
        await db.flush()
        await db.refresh(ma)
        return ma

    @staticmethod
    async def get_active(db: AsyncSession, question_id: uuid.UUID) -> MasterAnswer | None:
        result = await db.execute(
            select(MasterAnswer)
            .where(
                MasterAnswer.question_id == question_id,
                MasterAnswer.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_for_question(
        db: AsyncSession, question_id: uuid.UUID
    ) -> list[MasterAnswer]:
        result = await db.execute(
            select(MasterAnswer)
            .where(MasterAnswer.question_id == question_id)
            .order_by(MasterAnswer.version.desc())
        )
        return list(result.scalars().all())
