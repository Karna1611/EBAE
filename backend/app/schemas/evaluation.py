import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.evaluation import EvaluationLabel, EvaluationMethod


class EvaluationRead(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    rubric_id: uuid.UUID
    evidence_text: str | None
    nli_entailment: float | None
    nli_neutral: float | None
    nli_contradiction: float | None
    nli_confidence: float | None
    nli_label: EvaluationLabel | None
    llm_label: EvaluationLabel | None
    llm_reasoning: str | None
    llm_confidence: float | None
    final_label: EvaluationLabel
    method_used: EvaluationMethod
    score_awarded: float
    flagged_for_review: bool
    created_at: datetime

    model_config = {"from_attributes": True}
