import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.question import DifficultyLevel


class QuestionCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    difficulty: DifficultyLevel = DifficultyLevel.A_LEVEL
    text: str = Field(..., min_length=10)
    max_mark: int = Field(..., ge=1, le=100)
    created_by: str | None = None


class QuestionUpdate(BaseModel):
    subject: str | None = None
    difficulty: DifficultyLevel | None = None
    text: str | None = None
    max_mark: int | None = Field(None, ge=1, le=100)


class QuestionRead(BaseModel):
    id: uuid.UUID
    subject: str
    difficulty: DifficultyLevel
    text: str
    max_mark: int
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
