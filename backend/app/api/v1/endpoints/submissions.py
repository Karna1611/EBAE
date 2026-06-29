import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.submission import SubmissionCreate, SubmissionRead, SubmissionResult
from app.schemas.evaluation import EvaluationRead
from app.services.submission_service import SubmissionService
from app.services.question_service import QuestionService

router = APIRouter()


@router.post(
    "/{question_id}/submit",
    response_model=SubmissionResult,
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer(
    question_id: uuid.UUID,
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 06 — Student submits answer.
    Runs the full evaluation pipeline and returns results.
    """
    question = await QuestionService.get(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        submission = await SubmissionService.create_and_evaluate(db, question_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")

    result = await SubmissionService.get_submission_with_evaluations(db, submission.id)

    return SubmissionResult(
        submission=SubmissionRead.model_validate(result["submission"]),
        evaluations=[
            {
                "rubric_id": str(e.rubric_id),
                "final_label": e.final_label.value,
                "score_awarded": e.score_awarded,
                "evidence": e.evidence_text,
                "reasoning": e.llm_reasoning,
                "method": e.method_used.value,
                "confidence": e.llm_confidence or e.nli_confidence,
                "flagged": e.flagged_for_review,
            }
            for e in result["evaluations"]
        ],
        score=result["score"],
        max_score=result["max_score"],
        percentage=result["percentage"],
        feedback=result["feedback"],
    )


@router.get("/{question_id}/submissions", response_model=list[SubmissionRead])
async def list_submissions(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await SubmissionService.list_for_question(db, question_id)


@router.get("/submission/{submission_id}", response_model=SubmissionResult)
async def get_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await SubmissionService.get_submission_with_evaluations(db, submission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Submission not found")

    return SubmissionResult(
        submission=SubmissionRead.model_validate(result["submission"]),
        evaluations=[
            {
                "rubric_id": str(e.rubric_id),
                "final_label": e.final_label.value,
                "score_awarded": e.score_awarded,
                "evidence": e.evidence_text,
                "reasoning": e.llm_reasoning,
                "method": e.method_used.value,
                "confidence": e.llm_confidence or e.nli_confidence,
                "flagged": e.flagged_for_review,
            }
            for e in result["evaluations"]
        ],
        score=result["score"],
        max_score=result["max_score"],
        percentage=result["percentage"],
        feedback=result["feedback"],
    )
