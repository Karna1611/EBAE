import re


def preprocess_answer(text: str) -> str:
    """
    Step 07 — Clean and normalise student answer before evaluation.
    """
    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    # Normalise whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def segment_sentences(text: str) -> list[str]:
    """Split answer into sentences for evidence retrieval."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def extract_evidence(answer: str, rubric_description: str) -> str:
    """
    Step 08/09 — For short answers return full text.
    For long answers find most relevant passage using keyword overlap.
    """
    if len(answer) <= 800:
        return answer

    sentences = segment_sentences(answer)
    rubric_words = set(rubric_description.lower().split())

    scored = []
    for s in sentences:
        s_words = set(s.lower().split())
        overlap = len(rubric_words & s_words)
        scored.append((overlap, s))

    scored.sort(reverse=True)
    top = [s for _, s in scored[:3]]
    return " ".join(top) if top else answer[:800]