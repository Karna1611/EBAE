import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base


class ReviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"


class ReviewReason(str, enum.Enum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    NLI_LLM_CONFLICT = "NLI_LLM_CONFLICT"
    CONTRADICTORY_LABEL = "CONTRADICTORY_LABEL"
    STUDENT_APPEAL = "STUDENT_APPEAL"


class ReviewQueueItem(Base):
    __tablename__ = "review_queue"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rubric_evaluations.id", ondelete="CASCADE"), nullable=False)
    reason: Mapped[ReviewReason] = mapped_column(SAEnum(ReviewReason), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(SAEnum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING)
    reviewer: Mapped[str] = mapped_column(String(200), nullable=True)
    override_label: Mapped[str] = mapped_column(String(50), nullable=True)
    reviewer_note: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="review_items")
