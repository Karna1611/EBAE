import uuid
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
import anthropic

from app.models.rubric import Rubric, RubricVersion, RubricVersionStatus, RubricStatus
from app.models.question import Question
from app.models.master_answer import MasterAnswer
from app.schemas.rubric import RubricCreate, RubricUpdate
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


RUBRIC_GENERATION_PROMPT = """You are an expert examiner. Your task is to decompose a model answer into discrete, atomic rubric concepts for use in automated marking.

Each rubric concept must:
- Represent exactly ONE independently assessable idea
- Be written as a clear, testable statement (not a question)
- Be specific enough that a classifier can determine if a student answer addresses it

Return ONLY a valid JSON array. No markdown, no explanation, no preamble.

Each object in the array:
{{
  "concept": "short name (2-5 words)",
  "description": "one clear, assessable statement the student must make",
  "weight": 1.0,
  "keywords": ["keyword1", "keyword2"]
}}

Question: {question}

Model answer: {master_answer}

Respond with the JSON array only."""


class RubricService:

    @staticmethod
    async def generate_with_ai(
        db: AsyncSession,
        question: Question,
        master_answer: MasterAnswer,
    ) -> RubricVersion:
        """Step 03: Use Claude to decompose master answer into atomic rubric concepts."""
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        prompt = RUBRIC_GENERATION_PROMPT.format(
            question=question.text,
            master_answer=master_answer.content,
        )

        logger.info(f"Generating rubrics for question {question.id}")
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()
        # Strip any accidental markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            rubric_data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude rubric response: {e}\nRaw: {raw}")
            raise ValueError(f"Claude returned invalid JSON: {e}")

        # Get next version number for this question
        result = await db.execute(
            select(RubricVersion)
            .where(RubricVersion.question_id == question.id)
            .order_by(RubricVersion.version.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        next_version = (latest.version + 1) if latest else 1

        # Create the version record (DRAFT)
        rv = RubricVersion(
            question_id=question.id,
            master_answer_id=master_answer.id,
            version=next_version,
            status=RubricVersionStatus.DRAFT,
        )
        db.add(rv)
        await db.flush()

        # Create individual rubric records
        for i, item in enumerate(rubric_data):
            keywords = item.get("keywords", [])
            rubric = Rubric(
                rubric_version_id=rv.id,
                concept=item["concept"],
                description=item["description"],
                weight=float(item.get("weight", 1.0)),
                keywords=json.dumps(keywords) if keywords else None,
                order_index=i,
                status=RubricStatus.DRAFT,
            )
            db.add(rubric)

        await db.flush()
        await db.refresh(rv)

        # Reload with rubrics
        result = await db.execute(
            select(RubricVersion)
            .options(selectinload(RubricVersion.rubrics))
            .where(RubricVersion.id == rv.id)
        )
        return result.scalar_one()

    @staticmethod
    async def get_version(
        db: AsyncSession, version_id: uuid.UUID
    ) -> RubricVersion | None:
        result = await db.execute(
            select(RubricVersion)
            .options(selectinload(RubricVersion.rubrics))
            .where(RubricVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_version(
        db: AsyncSession, question_id: uuid.UUID
    ) -> RubricVersion | None:
        result = await db.execute(
            select(RubricVersion)
            .options(selectinload(RubricVersion.rubrics))
            .where(
                RubricVersion.question_id == question_id,
                RubricVersion.status == RubricVersionStatus.APPROVED,
            )
            .order_by(RubricVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_versions(
        db: AsyncSession, question_id: uuid.UUID
    ) -> list[RubricVersion]:
        result = await db.execute(
            select(RubricVersion)
            .options(selectinload(RubricVersion.rubrics))
            .where(RubricVersion.question_id == question_id)
            .order_by(RubricVersion.version.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def approve_version(
        db: AsyncSession, version_id: uuid.UUID, approved_by: str
    ) -> RubricVersion | None:
        """Step 04: Human approves rubric version. DRAFT -> APPROVED."""
        rv = await RubricService.get_version(db, version_id)
        if not rv:
            return None
        if rv.status != RubricVersionStatus.DRAFT:
            raise ValueError(f"Cannot approve a version with status {rv.status}")

        # Deprecate any previously approved versions for this question
        await db.execute(
            update(RubricVersion)
            .where(
                RubricVersion.question_id == rv.question_id,
                RubricVersion.status == RubricVersionStatus.APPROVED,
            )
            .values(status=RubricVersionStatus.DEPRECATED)
        )

        # Approve all DRAFT rubrics in this version
        await db.execute(
            update(Rubric)
            .where(
                Rubric.rubric_version_id == version_id,
                Rubric.status == RubricStatus.DRAFT,
            )
            .values(status=RubricStatus.APPROVED)
        )

        rv.status = RubricVersionStatus.APPROVED
        rv.approved_by = approved_by
        rv.approved_at = datetime.utcnow()

        await db.flush()
        await db.refresh(rv)
        return rv

    @staticmethod
    async def update_rubric(
        db: AsyncSession, rubric_id: uuid.UUID, data: RubricUpdate
    ) -> Rubric | None:
        result = await db.execute(select(Rubric).where(Rubric.id == rubric_id))
        rubric = result.scalar_one_or_none()
        if not rubric:
            return None
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(rubric, field, value)
        await db.flush()
        await db.refresh(rubric)
        return rubric

    @staticmethod
    async def delete_rubric(db: AsyncSession, rubric_id: uuid.UUID) -> bool:
        result = await db.execute(select(Rubric).where(Rubric.id == rubric_id))
        rubric = result.scalar_one_or_none()
        if not rubric:
            return False
        await db.delete(rubric)
        return True
