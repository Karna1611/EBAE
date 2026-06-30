"""
Step 10 — NLI Classification Service

Uses cross-encoder/nli-deberta-v3-base for fast first-pass classification.
Falls back to a rule-based mock when the model is not available (dev mode).
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# NLI label mapping from model output
NLI_LABEL_MAP = {
    "entailment": "PRESENT",
    "neutral": "ABSENT",
    "contradiction": "CONTRADICTORY",
}


@dataclass
class NLIResult:
    entailment: float
    neutral: float
    contradiction: float
    predicted_label: str  # PRESENT | ABSENT | CONTRADICTORY
    confidence: float


def _mock_nli(premise: str, hypothesis: str) -> NLIResult:
    """
    Rule-based mock NLI for development when model is not loaded.
    Checks keyword overlap between premise and hypothesis.
    Returns high confidence for clear cases so only genuinely ambiguous
    rubrics escalate to the LLM judge (~20% escalation vs 100% previously).
    """
    premise_lower = premise.lower()
    hypothesis_words = hypothesis.lower().split()

    matches = sum(1 for w in hypothesis_words if len(w) > 3 and w in premise_lower)
    ratio = matches / max(len(hypothesis_words), 1)

    if ratio >= 0.4:
        # Clear overlap — confident PRESENT, stays in NLI
        return NLIResult(entailment=0.92, neutral=0.05, contradiction=0.03, predicted_label="PRESENT", confidence=0.92)
    elif ratio < 0.15:
        # Very little overlap — confident ABSENT, stays in NLI
        return NLIResult(entailment=0.05, neutral=0.88, contradiction=0.07, predicted_label="ABSENT", confidence=0.88)
    else:
        # Ambiguous middle zone — low confidence, escalates to LLM judge
        return NLIResult(entailment=0.38, neutral=0.38, contradiction=0.24, predicted_label="ABSENT", confidence=0.52)


# Try to load the real NLI model
_pipeline = None

def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    try:
        from transformers import pipeline
        logger.info("Loading DeBERTa NLI model...")
        _pipeline = pipeline(
            "zero-shot-classification",
            model="cross-encoder/nli-deberta-v3-base",
            device=-1,  # CPU
        )
        logger.info("NLI model loaded successfully")
        return _pipeline
    except Exception as e:
        logger.warning(f"NLI model not available, using mock: {e}")
        return None


def classify(premise: str, hypothesis: str) -> NLIResult:
    """
    Classify whether the premise (evidence) entails the hypothesis (rubric).
    Returns NLIResult with probability distribution and predicted label.
    """
    pipe = _get_pipeline()
    
    if pipe is None:
        logger.debug("Using mock NLI classifier")
        return _mock_nli(premise, hypothesis)

    try:
        result = pipe(
            premise,
            candidate_labels=[hypothesis],
            hypothesis_template="{}",
        )
        # For cross-encoder NLI, use the scores directly
        scores = result.get("scores", [0.33, 0.33, 0.34])
        labels = result.get("labels", ["entailment", "neutral", "contradiction"])
        
        score_map = dict(zip(labels, scores))
        entailment = score_map.get("entailment", 0.33)
        neutral = score_map.get("neutral", 0.33)
        contradiction = score_map.get("contradiction", 0.34)
        
        max_score = max(entailment, neutral, contradiction)
        if entailment == max_score:
            label = "PRESENT"
        elif contradiction == max_score:
            label = "CONTRADICTORY"
        else:
            label = "ABSENT"

        return NLIResult(
            entailment=entailment,
            neutral=neutral,
            contradiction=contradiction,
            predicted_label=label,
            confidence=max_score,
        )
    except Exception as e:
        logger.error(f"NLI classification error: {e}")
        return _mock_nli(premise, hypothesis)
