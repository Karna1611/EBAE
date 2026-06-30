import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.review import ReviewStatus, ReviewReason
from app.models.evaluation import EvaluationLabel


class ReviewResolveRequest(BaseModel):
    reviewer: str = Field(..., min_length=1)
    override_label: EvaluationLabel
    reviewer_note: str | None = None


class ReviewItemRead(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    evaluation_id: uuid.UUID
    reason: ReviewReason
    status: ReviewStatus
    reviewer: str | None
    override_label: str | None
    reviewer_note: str | None
    created_at: datetime
    resolved_at: datetime | None
    rubric_concept: str | None = None
    student_name: str | None = None

    model_config = {"from_attributes": True}
