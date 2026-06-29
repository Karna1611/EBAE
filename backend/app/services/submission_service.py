import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.submission import Submission, SubmissionStatus
from app.models.evaluation import RubricEvaluation
from app.models.rubric import RubricVersion, RubricVersionStatus
from app.schemas.submission import SubmissionCreate
from app.services.evaluation_pipeline import run_evaluation_pipeline


class SubmissionService:

    @staticmethod
    async def create_and_evaluate(
        db: AsyncSession,
        question_id: uuid.UUID,
        data: SubmissionCreate,
    ) -> Submission:
        """
        Step 06 — Accept student submission, fetch active rubric version,
        then run the full evaluation pipeline.
        """
        # Get active rubric version for this question
        result = await db.execute(
            select(RubricVersion)
            .where(
                RubricVersion.question_id == question_id,
                RubricVersion.status == RubricVersionStatus.APPROVED,
            )
            .order_by(RubricVersion.version.desc())
            .limit(1)
        )
        rubric_version = result.scalar_one_or_none()
        if not rubric_version:
            raise ValueError("No approved rubric version found for this question")

        # Create submission record
        submission = Submission(
            question_id=question_id,
            rubric_version_id=rubric_version.id,
            student_name=data.student_name,
            student_id=data.student_id,
            raw_answer=data.answer,
            status=SubmissionStatus.PENDING,
        )
        db.add(submission)
        await db.flush()
        await db.refresh(submission)

        # Run pipeline (inline — for async API)
        submission = await run_evaluation_pipeline(db, submission.id)
        return submission

    @staticmethod
    async def get_submission_with_evaluations(
        db: AsyncSession,
        submission_id: uuid.UUID,
    ) -> dict | None:
        result = await db.execute(
            select(Submission)
            .options(selectinload(Submission.evaluations))
            .where(Submission.id == submission_id)
        )
        submission = result.scalar_one_or_none()
        if not submission:
            return None

        return {
            "submission": submission,
            "evaluations": submission.evaluations,
            "score": submission.final_score or 0.0,
            "max_score": submission.max_score or 0.0,
            "percentage": round((submission.final_score or 0) / (submission.max_score or 1) * 100, 1),
            "feedback": submission.feedback,
        }

    @staticmethod
    async def list_for_question(
        db: AsyncSession,
        question_id: uuid.UUID,
    ) -> list[Submission]:
        result = await db.execute(
            select(Submission)
            .where(Submission.question_id == question_id)
            .order_by(Submission.submitted_at.desc())
        )
        return list(result.scalars().all())
