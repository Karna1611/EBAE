"""
Step 11 — LLM Judge Service

Called when NLI confidence < threshold or for high-stakes evaluations.
Uses Claude to provide nuanced judgment with reasoning.
"""
import asyncio
import json
import logging
import anthropic
from dataclasses import dataclass
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

JUDGE_PROMPT = """You are an expert examiner evaluating a student's answer against a specific rubric concept.

Rubric concept: "{concept}"
Rubric description: "{description}"

Student's full answer:
"{answer}"

Relevant evidence extracted:
"{evidence}"

NLI model scores (for reference):
- Entailment (PRESENT): {nli_entailment:.2f}
- Neutral (ABSENT): {nli_neutral:.2f}  
- Contradiction: {nli_contradiction:.2f}

Your task: Evaluate whether the student's answer satisfies this rubric concept.

Labels:
- PRESENT: Student clearly and correctly addresses this concept
- PARTIAL: Student partially addresses it or is vague/incomplete
- ABSENT: Student does not mention this concept at all
- CONTRADICTORY: Student states something that directly contradicts this concept

Return ONLY a valid JSON object, no markdown:
{{"label": "PRESENT|PARTIAL|ABSENT|CONTRADICTORY", "reasoning": "one clear sentence explaining your decision", "confidence": 0.0}}"""


@dataclass
class LLMJudgeResult:
    label: str
    reasoning: str
    confidence: float


async def judge(
    rubric_concept: str,
    rubric_description: str,
    student_answer: str,
    evidence: str,
    nli_entailment: float,
    nli_neutral: float,
    nli_contradiction: float,
) -> LLMJudgeResult:
    """
    Use Claude as LLM judge for nuanced evaluation.
    """
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = JUDGE_PROMPT.format(
        concept=rubric_concept,
        description=rubric_description,
        answer=student_answer[:2000],
        evidence=evidence[:1000],
        nli_entailment=nli_entailment,
        nli_neutral=nli_neutral,
        nli_contradiction=nli_contradiction,
    )

    retryable = (anthropic.APITimeoutError, anthropic.APIConnectionError, anthropic.RateLimitError)
    backoff = [1, 2, 4]
    last_error: Exception | None = None

    for attempt, delay in enumerate(backoff, 1):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            return LLMJudgeResult(
                label=data.get("label", "ABSENT"),
                reasoning=data.get("reasoning", ""),
                confidence=float(data.get("confidence", 0.5)),
            )
        except retryable as e:
            last_error = e
            logger.warning(f"LLM judge attempt {attempt}/{len(backoff)} failed ({type(e).__name__}): {e}")
            if attempt < len(backoff):
                await asyncio.sleep(delay)
        except Exception as e:
            logger.error(f"LLM judge non-retryable error: {e}")
            return LLMJudgeResult(label="PARTIAL", reasoning=f"Judge unavailable: {e}", confidence=0.0)

    # All retries exhausted — return PARTIAL so the score isn't silently zeroed
    # and confidence=0.0 ensures this gets flagged for human review
    logger.error(f"LLM judge failed after {len(backoff)} attempts: {last_error}")
    return LLMJudgeResult(label="PARTIAL", reasoning="LLM judge unavailable after retries — flagged for human review", confidence=0.0)
