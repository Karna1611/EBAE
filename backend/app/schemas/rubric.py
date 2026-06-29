import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.rubric import RubricStatus, RubricVersionStatus


class RubricCreate(BaseModel):
    concept: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=5)
    weight: float = Field(1.0, ge=0.1, le=10.0)
    keywords: str | None = None
    order_index: int = 0


class RubricUpdate(BaseModel):
    concept: str | None = None
    description: str | None = None
    weight: float | None = Field(None, ge=0.1, le=10.0)
    keywords: str | None = None
    order_index: int | None = None
    status: RubricStatus | None = None


class RubricRead(BaseModel):
    id: uuid.UUID
    concept: str
    description: str
    weight: float
    keywords: str | None
    order_index: int
    status: RubricStatus

    model_config = {"from_attributes": True}


class RubricVersionRead(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    version: int
    status: RubricVersionStatus
    approved_by: str | None
    approved_at: datetime | None
    created_at: datetime
    rubrics: list[RubricRead] = []

    model_config = {"from_attributes": True}


class RubricGenerateRequest(BaseModel):
    """Request to AI-generate rubrics from a master answer."""
    question_id: uuid.UUID
    master_answer_id: uuid.UUID


class RubricApproveRequest(BaseModel):
    approved_by: str = Field(..., min_length=1)
