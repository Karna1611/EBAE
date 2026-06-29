"""
Step 15 — Feedback Generation Service

Uses Claude to synthesise per-rubric labels into coherent student feedback.
"""
import logging
import anthropic
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

FEEDBACK_PROMPT = """You are a supportive teacher writing feedback for a student.

Question: "{question}"
Student scored: {score}/{max_score} marks

Rubric results:
{rubric_summary}

Write 3-4 sentences of constructive feedback:
1. Acknowledge what the student got right
2. Point out what was incomplete or missing
3. Give one specific improvement suggestion

Be encouraging, specific, and match the language to the subject level.
Write in plain prose, no bullet points."""


async def generate_feedback(
    question_text: str,
    score: float,
    max_score: float,
    rubric_results: list[dict],
) -> str:
    """Generate student-facing feedback from rubric evaluation results."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    rubric_summary = "\n".join([
        f"- {r['concept']}: {r['label']} — {r['reasoning']}"
        for r in rubric_results
    ])

    prompt = FEEDBACK_PROMPT.format(
        question=question_text,
        score=score,
        max_score=max_score,
        rubric_summary=rubric_summary,
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        logger.error(f"Feedback generation error: {e}")
        return f"Score: {score}/{max_score}. Please review the rubric breakdown for details."
