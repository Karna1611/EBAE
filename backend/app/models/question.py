import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base


class DifficultyLevel(str, enum.Enum):
    GCSE = "GCSE"
    AS_LEVEL = "AS_LEVEL"
    A_LEVEL = "A_LEVEL"
    UNDERGRADUATE = "UNDERGRADUATE"
    OTHER = "OTHER"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SAEnum(DifficultyLevel), nullable=False, default=DifficultyLevel.A_LEVEL
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    max_mark: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    created_by: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    master_answers: Mapped[list["MasterAnswer"]] = relationship(
        "MasterAnswer", back_populates="question", cascade="all, delete-orphan"
    )
    rubric_versions: Mapped[list["RubricVersion"]] = relationship(
        "RubricVersion", back_populates="question", cascade="all, delete-orphan"
    )
