import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class MasterAnswerCreate(BaseModel):
    content: str = Field(..., min_length=20)
    created_by: str | None = None


class MasterAnswerRead(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    version: int
    content: str
    is_active: bool
    created_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
