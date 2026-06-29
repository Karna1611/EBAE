import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.review import ReviewQueueItem, ReviewStatus
from app.models.evaluation import RubricEvaluation, EvaluationMethod
from app.schemas.review import ReviewResolveRequest
from app.services.evaluation_pipeline import LABEL_SCORES


class ReviewService:

    @staticmethod
    async def list_pending(db: AsyncSession) -> list[ReviewQueueItem]:
        result = await db.execute(
            select(ReviewQueueItem)
            .where(ReviewQueueItem.status == ReviewStatus.PENDING)
            .order_by(ReviewQueueItem.created_at.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def resolve(
        db: AsyncSession,
        item_id: uuid.UUID,
        data: ReviewResolveRequest,
    ) -> ReviewQueueItem | None:
        result = await db.execute(
            select(ReviewQueueItem).where(ReviewQueueItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return None

        # Update the evaluation with the override
        eval_result = await db.execute(
            select(RubricEvaluation).where(RubricEvaluation.id == item.evaluation_id)
        )
        evaluation = eval_result.scalar_one_or_none()
        if evaluation:
            from app.models.evaluation import EvaluationLabel
            override_label = EvaluationLabel(data.override_label)
            evaluation.final_label = override_label
            evaluation.method_used = EvaluationMethod.HUMAN_OVERRIDE
            evaluation.score_awarded = LABEL_SCORES.get(override_label, 0.0)
            evaluation.flagged_for_review = False

        # Resolve review item
        item.status = ReviewStatus.RESOLVED
        item.reviewer = data.reviewer
        item.override_label = data.override_label.value
        item.reviewer_note = data.reviewer_note
        item.resolved_at = datetime.utcnow()

        await db.flush()
        await db.refresh(item)
        return item
