"""
Phase B Core — Evaluation Pipeline Orchestrator
Steps 06-16 wired together.
"""
import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.submission import Submission, SubmissionStatus
from app.models.evaluation import RubricEvaluation, EvaluationLabel, EvaluationMethod
from app.models.review import ReviewQueueItem, ReviewReason, ReviewStatus
from app.models.rubric import Rubric, RubricVersion, RubricVersionStatus
from app.models.question import Question
from app.services.preprocessing import preprocess_answer, extract_evidence
from app.services.nli_service import classify
from app.services.llm_judge_service import judge
from app.services.feedback_service import generate_feedback
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Label to score mapping
LABEL_SCORES = {
    EvaluationLabel.PRESENT: 1.0,
    EvaluationLabel.PARTIAL: 0.5,
    EvaluationLabel.ABSENT: 0.0,
    EvaluationLabel.CONTRADICTORY: 0.0,
}

# Flags that trigger human review
REVIEW_TRIGGERS = {
    "low_confidence": 0.65,
    "contradictory": True,
}


async def run_evaluation_pipeline(
    db: AsyncSession,
    submission_id: uuid.UUID,
) -> Submission:
    """
    Main pipeline: Steps 07-16
    Runs the full evaluation for a submission.
    """
    # Load submission
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise ValueError(f"Submission {submission_id} not found")

    # Update status to PROCESSING
    submission.status = SubmissionStatus.PROCESSING
    await db.flush()

    try:
        # Load question
        q_result = await db.execute(select(Question).where(Question.id == submission.question_id))
        question = q_result.scalar_one()

        # Load rubric version with rubrics
        rv_result = await db.execute(
            select(RubricVersion)
            .options(selectinload(RubricVersion.rubrics))
            .where(RubricVersion.id == submission.rubric_version_id)
        )
        rubric_version = rv_result.scalar_one()

        # Step 07 — Preprocess answer
        preprocessed = preprocess_answer(submission.raw_answer)
        submission.preprocessed_answer = preprocessed

        rubric_results = []
        total_score = 0.0
        total_weight = sum(r.weight for r in rubric_version.rubrics)

        # Steps 08-12 — Loop over each rubric
        for rubric in rubric_version.rubrics:
            eval_result = await _evaluate_rubric(
                db=db,
                submission=submission,
                rubric=rubric,
                answer=preprocessed,
            )
            total_score += eval_result.score_awarded * rubric.weight
            rubric_results.append({
                "concept": rubric.concept,
                "label": eval_result.final_label.value,
                "reasoning": eval_result.llm_reasoning or "",
                "score": eval_result.score_awarded,
            })

        # Step 14 — Mark allocation
        max_score = float(question.max_mark)
        if total_weight > 0:
            final_score = round((total_score / total_weight) * max_score, 2)
        else:
            final_score = 0.0

        # Step 15 — Feedback generation
        feedback = await generate_feedback(
            question_text=question.text,
            score=final_score,
            max_score=max_score,
            rubric_results=rubric_results,
        )

        # Step 16 — Store results
        submission.final_score = final_score
        submission.max_score = max_score
        submission.feedback = feedback
        submission.status = SubmissionStatus.COMPLETE
        submission.completed_at = datetime.utcnow()

        await db.flush()
        await db.refresh(submission)
        return submission

    except Exception as e:
        logger.error(f"Pipeline error for submission {submission_id}: {e}")
        submission.status = SubmissionStatus.FAILED
        await db.flush()
        raise


async def _evaluate_rubric(
    db: AsyncSession,
    submission: Submission,
    rubric: Rubric,
    answer: str,
) -> RubricEvaluation:
    """
    Steps 08-12 for a single rubric.
    """
    # Step 08/09 — Evidence retrieval and extraction
    evidence = extract_evidence(answer, rubric.description)

    # Step 10 — NLI Classification
    nli_result = classify(premise=evidence, hypothesis=rubric.description)

    # Determine if LLM judge is needed
    needs_llm = (
        nli_result.confidence < settings.NLI_CONFIDENCE_THRESHOLD
        or nli_result.predicted_label == "CONTRADICTORY"
    )

    # Step 11 — LLM Judge (if needed)
    llm_label = None
    llm_reasoning = None
    llm_confidence = None
    method = EvaluationMethod.NLI_ONLY

    if needs_llm:
        llm_result = await judge(
            rubric_concept=rubric.concept,
            rubric_description=rubric.description,
            student_answer=answer,
            evidence=evidence,
            nli_entailment=nli_result.entailment,
            nli_neutral=nli_result.neutral,
            nli_contradiction=nli_result.contradiction,
        )
        llm_label = EvaluationLabel(llm_result.label)
        llm_reasoning = llm_result.reasoning
        llm_confidence = llm_result.confidence
        method = EvaluationMethod.LLM_JUDGE

    # Step 12 — Confidence scoring and final label
    if method == EvaluationMethod.LLM_JUDGE:
        final_label = llm_label
        final_confidence = llm_confidence
    else:
        final_label = EvaluationLabel(nli_result.predicted_label)
        final_confidence = nli_result.confidence

    score = LABEL_SCORES.get(final_label, 0.0)

    # Determine if flagged for review
    flagged = (
        final_confidence < REVIEW_TRIGGERS["low_confidence"]
        or final_label == EvaluationLabel.CONTRADICTORY
        or (llm_label and nli_result.predicted_label != llm_label.value)
    )

    # Create evaluation record
    evaluation = RubricEvaluation(
        submission_id=submission.id,
        rubric_id=rubric.id,
        evidence_text=evidence,
        nli_entailment=nli_result.entailment,
        nli_neutral=nli_result.neutral,
        nli_contradiction=nli_result.contradiction,
        nli_confidence=nli_result.confidence,
        nli_label=EvaluationLabel(nli_result.predicted_label),
        llm_label=llm_label,
        llm_reasoning=llm_reasoning,
        llm_confidence=llm_confidence,
        final_label=final_label,
        method_used=method,
        score_awarded=score,
        flagged_for_review=flagged,
    )
    db.add(evaluation)
    await db.flush()

    # Step 13 — Add to review queue if flagged
    if flagged:
        reason = _determine_review_reason(
            nli_label=nli_result.predicted_label,
            llm_label=llm_label.value if llm_label else None,
            final_label=final_label.value,
            confidence=final_confidence,
        )
        review_item = ReviewQueueItem(
            submission_id=submission.id,
            evaluation_id=evaluation.id,
            reason=reason,
            status=ReviewStatus.PENDING,
        )
        db.add(review_item)
        await db.flush()

    return evaluation


def _determine_review_reason(
    nli_label: str,
    llm_label: str | None,
    final_label: str,
    confidence: float,
) -> ReviewReason:
    if final_label == "CONTRADICTORY":
        return ReviewReason.CONTRADICTORY_LABEL
    if llm_label and nli_label != llm_label:
        return ReviewReason.NLI_LLM_CONFLICT
    return ReviewReason.LOW_CONFIDENCE
