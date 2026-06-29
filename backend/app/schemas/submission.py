import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.submission import SubmissionStatus


class SubmissionCreate(BaseModel):
    student_name: str = Field(..., min_length=1, max_length=200)
    student_id: str | None = None
    answer: str = Field(..., min_length=5)


class SubmissionRead(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    rubric_version_id: uuid.UUID
    student_name: str
    student_id: str | None
    raw_answer: str
    status: SubmissionStatus
    final_score: float | None
    max_score: float | None
    feedback: str | None
    submitted_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class SubmissionResult(BaseModel):
    submission: SubmissionRead
    evaluations: list[dict]
    score: float
    max_score: float
    percentage: float
    feedback: str | None
