import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base


class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    REVIEW = "REVIEW"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    rubric_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rubric_versions.id"), nullable=False)
    student_name: Mapped[str] = mapped_column(String(200), nullable=False)
    student_id: Mapped[str] = mapped_column(String(100), nullable=True)
    raw_answer: Mapped[str] = mapped_column(Text, nullable=False)
    preprocessed_answer: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(SAEnum(SubmissionStatus), nullable=False, default=SubmissionStatus.PENDING)
    final_score: Mapped[float] = mapped_column(nullable=True)
    max_score: Mapped[float] = mapped_column(nullable=True)
    feedback: Mapped[str] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    evaluations: Mapped[list["RubricEvaluation"]] = relationship("RubricEvaluation", back_populates="submission", cascade="all, delete-orphan")
    review_items: Mapped[list["ReviewQueueItem"]] = relationship("ReviewQueueItem", back_populates="submission", cascade="all, delete-orphan")
