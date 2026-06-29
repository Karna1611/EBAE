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
    """
    premise_lower = premise.lower()
    hypothesis_words = hypothesis.lower().split()
    
    # Count matching words
    matches = sum(1 for w in hypothesis_words if len(w) > 3 and w in premise_lower)
    ratio = matches / max(len(hypothesis_words), 1)

    if ratio >= 0.4:
        return NLIResult(entailment=0.75, neutral=0.15, contradiction=0.10, predicted_label="PRESENT", confidence=0.75)
    elif ratio >= 0.2:
        return NLIResult(entailment=0.45, neutral=0.40, contradiction=0.15, predicted_label="ABSENT", confidence=0.45)
    else:
        return NLIResult(entailment=0.10, neutral=0.70, contradiction=0.20, predicted_label="ABSENT", confidence=0.70)


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
