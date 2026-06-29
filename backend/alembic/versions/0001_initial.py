"""Initial schema: questions, master_answers, rubric_versions, rubrics

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ── questions ──
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("subject", sa.String(100), nullable=False),
        sa.Column("difficulty", sa.Enum("GCSE", "AS_LEVEL", "A_LEVEL", "UNDERGRADUATE", "OTHER", name="difficultylevel"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("max_mark", sa.Integer, nullable=False),
        sa.Column("created_by", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("NOW()")),
    )

    # ── master_answers ──
    op.create_table(
        "master_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_by", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_master_answers_question_id", "master_answers", ["question_id"])

    # ── rubric_versions ──
    op.create_table(
        "rubric_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("master_answer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("master_answers.id"), nullable=True),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "APPROVED", "DEPRECATED", name="rubricversionstatus"), nullable=False, server_default="DRAFT"),
        sa.Column("approved_by", sa.String(200), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_rubric_versions_question_id", "rubric_versions", ["question_id"])
    op.create_index("ix_rubric_versions_status", "rubric_versions", ["status"])

    # ── rubrics ──
    op.create_table(
        "rubrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("rubric_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rubric_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("concept", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("weight", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("keywords", sa.Text, nullable=True),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("DRAFT", "APPROVED", "REJECTED", name="rubricstatus"), nullable=False, server_default="DRAFT"),
    )
    op.create_index("ix_rubrics_rubric_version_id", "rubrics", ["rubric_version_id"])


def downgrade() -> None:
    op.drop_table("rubrics")
    op.drop_table("rubric_versions")
    op.drop_table("master_answers")
    op.drop_table("questions")
    op.execute("DROP TYPE IF EXISTS rubricstatus")
    op.execute("DROP TYPE IF EXISTS rubricversionstatus")
    op.execute("DROP TYPE IF EXISTS difficultylevel")
