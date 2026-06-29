import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.submission import Submission, SubmissionStatus
from app.models.evaluation import RubricEvaluation, EvaluationLabel
from app.models.rubric import Rubric
from app.services.question_service import QuestionService

router = APIRouter()


@router.get("/question/{question_id}")
async def get_question_analytics(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Step 17 — Analytics and reporting for a question."""
    question = await QuestionService.get(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Total submissions
    sub_result = await db.execute(
        select(func.count(Submission.id))
        .where(
            Submission.question_id == question_id,
            Submission.status == SubmissionStatus.COMPLETE,
        )
    )
    total_submissions = sub_result.scalar() or 0

    # Average score
    score_result = await db.execute(
        select(func.avg(Submission.final_score), func.max(Submission.final_score), func.min(Submission.final_score))
        .where(
            Submission.question_id == question_id,
            Submission.status == SubmissionStatus.COMPLETE,
        )
    )
    avg_score, max_score, min_score = score_result.one()

    # Per-rubric label distribution
    rubric_result = await db.execute(
        select(Rubric.concept, RubricEvaluation.final_label, func.count())
        .join(RubricEvaluation, RubricEvaluation.rubric_id == Rubric.id)
        .join(Submission, Submission.id == RubricEvaluation.submission_id)
        .where(Submission.question_id == question_id)
        .group_by(Rubric.concept, RubricEvaluation.final_label)
    )
    rows = rubric_result.all()

    # Build per-rubric stats
    rubric_stats = {}
    for concept, label, count in rows:
        if concept not in rubric_stats:
            rubric_stats[concept] = {"PRESENT": 0, "PARTIAL": 0, "ABSENT": 0, "CONTRADICTORY": 0}
        rubric_stats[concept][label.value] += count

    # LLM escalation rate
    llm_result = await db.execute(
        select(func.count(RubricEvaluation.id))
        .join(Submission, Submission.id == RubricEvaluation.submission_id)
        .where(
            Submission.question_id == question_id,
            RubricEvaluation.method_used == "LLM_JUDGE",
        )
    )
    llm_count = llm_result.scalar() or 0

    total_evals_result = await db.execute(
        select(func.count(RubricEvaluation.id))
        .join(Submission, Submission.id == RubricEvaluation.submission_id)
        .where(Submission.question_id == question_id)
    )
    total_evals = total_evals_result.scalar() or 1

    return {
        "question_id": str(question_id),
        "question_text": question.text,
        "total_submissions": total_submissions,
        "average_score": round(float(avg_score or 0), 2),
        "max_score_achieved": round(float(max_score or 0), 2),
        "min_score_achieved": round(float(min_score or 0), 2),
        "llm_escalation_rate": round(llm_count / total_evals * 100, 1),
        "rubric_breakdown": rubric_stats,
    }
