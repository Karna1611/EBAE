import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base


class EvaluationLabel(str, enum.Enum):
    PRESENT = "PRESENT"
    PARTIAL = "PARTIAL"
    ABSENT = "ABSENT"
    CONTRADICTORY = "CONTRADICTORY"


class EvaluationMethod(str, enum.Enum):
    NLI_ONLY = "NLI_ONLY"
    LLM_JUDGE = "LLM_JUDGE"
    HUMAN_OVERRIDE = "HUMAN_OVERRIDE"


class RubricEvaluation(Base):
    __tablename__ = "rubric_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    rubric_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rubrics.id"), nullable=False)

    # Evidence
    evidence_text: Mapped[str] = mapped_column(Text, nullable=True)

    # NLI outputs
    nli_entailment: Mapped[float] = mapped_column(Float, nullable=True)
    nli_neutral: Mapped[float] = mapped_column(Float, nullable=True)
    nli_contradiction: Mapped[float] = mapped_column(Float, nullable=True)
    nli_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    nli_label: Mapped[EvaluationLabel] = mapped_column(SAEnum(EvaluationLabel), nullable=True)

    # LLM Judge outputs
    llm_label: Mapped[EvaluationLabel] = mapped_column(SAEnum(EvaluationLabel), nullable=True)
    llm_reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    llm_confidence: Mapped[float] = mapped_column(Float, nullable=True)

    # Final decision
    final_label: Mapped[EvaluationLabel] = mapped_column(SAEnum(EvaluationLabel), nullable=False, default=EvaluationLabel.ABSENT)
    method_used: Mapped[EvaluationMethod] = mapped_column(SAEnum(EvaluationMethod), nullable=False, default=EvaluationMethod.NLI_ONLY)
    score_awarded: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    flagged_for_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="evaluations")
