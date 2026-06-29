import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base


class RubricVersionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    DEPRECATED = "DEPRECATED"


class RubricStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RubricVersion(Base):
    """A versioned set of rubrics for a question. One APPROVED version is active at a time."""
    __tablename__ = "rubric_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    master_answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("master_answers.id"), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[RubricVersionStatus] = mapped_column(
        SAEnum(RubricVersionStatus), nullable=False, default=RubricVersionStatus.DRAFT
    )
    approved_by: Mapped[str] = mapped_column(String(200), nullable=True)
    approved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    question: Mapped["Question"] = relationship("Question", back_populates="rubric_versions")
    master_answer: Mapped["MasterAnswer"] = relationship(
        "MasterAnswer", back_populates="rubric_versions"
    )
    rubrics: Mapped[list["Rubric"]] = relationship(
        "Rubric", back_populates="rubric_version", cascade="all, delete-orphan",
        order_by="Rubric.order_index"
    )


class Rubric(Base):
    """A single atomic rubric concept within a RubricVersion."""
    __tablename__ = "rubrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rubric_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rubric_versions.id", ondelete="CASCADE"), nullable=False
    )
    concept: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    keywords: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array as text
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[RubricStatus] = mapped_column(
        SAEnum(RubricStatus), nullable=False, default=RubricStatus.DRAFT
    )

    # Relationships
    rubric_version: Mapped["RubricVersion"] = relationship(
        "RubricVersion", back_populates="rubrics"
    )
