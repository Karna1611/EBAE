"""
Celery tasks for async rubric generation.
Used when generation should not block the API response.
"""
import uuid
import logging
from app.tasks.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.generate_rubrics_async")
def generate_rubrics_async(self, question_id: str, master_answer_id: str) -> dict:
    """
    Async rubric generation task.
    Kicks off in the background after question+master answer are created.
    """
    import asyncio
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import get_settings
    from app.db.session import sync_engine
    from sqlalchemy.orm import Session

    settings = get_settings()
    logger.info(f"Starting async rubric generation: question={question_id}")

    # For Celery we use a sync session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    with SessionLocal() as session:
        try:
            from sqlalchemy import select
            from app.models.question import Question
            from app.models.master_answer import MasterAnswer

            q = session.get(Question, uuid.UUID(question_id))
            ma = session.get(MasterAnswer, uuid.UUID(master_answer_id))

            if not q or not ma:
                return {"status": "error", "detail": "Question or master answer not found"}

            # Import sync rubric service for Celery context
            import json
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            from app.services.rubric_service import RUBRIC_GENERATION_PROMPT
            prompt = RUBRIC_GENERATION_PROMPT.format(
                question=q.text, master_answer=ma.content
            )

            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            rubric_data = json.loads(raw)

            from app.models.rubric import RubricVersion, Rubric, RubricVersionStatus, RubricStatus

            result = session.execute(
                select(RubricVersion)
                .where(RubricVersion.question_id == q.id)
                .order_by(RubricVersion.version.desc())
                .limit(1)
            )
            latest = result.scalar_one_or_none()
            next_version = (latest.version + 1) if latest else 1

            rv = RubricVersion(
                question_id=q.id,
                master_answer_id=ma.id,
                version=next_version,
                status=RubricVersionStatus.DRAFT,
            )
            session.add(rv)
            session.flush()

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
                session.add(rubric)

            session.commit()
            logger.info(f"Generated {len(rubric_data)} rubrics → version {rv.id}")
            return {"status": "success", "rubric_version_id": str(rv.id), "count": len(rubric_data)}

        except Exception as e:
            session.rollback()
            logger.error(f"Rubric generation failed: {e}")
            return {"status": "error", "detail": str(e)}
