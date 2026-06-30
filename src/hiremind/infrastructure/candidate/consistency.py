"""Career Consistency Engine — scores alignment between headline, career, and skills."""

from hiremind.domain.candidate import Candidate


def score_consistency(candidate: Candidate) -> float:
    """Score how consistent a candidate's profile is (0.0–1.0).

    Compares:
        - Headline vs career titles (30%)
        - Headline vs skills (30%)
        - Summary vs skills (20%)
        - Education field vs career domain (20%)

    Higher score = more consistent / trustworthy profile.
    """
    headline_career = _headline_vs_career(candidate)
    headline_skills = _headline_vs_skills(candidate)
    summary_skills = _summary_vs_skills(candidate)
    education_career = _education_vs_career(candidate)

    raw = (
        0.30 * headline_career
        + 0.30 * headline_skills
        + 0.20 * summary_skills
        + 0.20 * education_career
    )
    return round(min(raw, 1.0), 3)


def _tokenize(text: str | None) -> set[str]:
    """Simple word tokenisation with stopword removal."""
    if not text:
        return set()
    stopwords = frozenset(
        {
            "the",
            "a",
            "an",
            "and",
            "or",
            "in",
            "at",
            "of",
            "to",
            "for",
            "with",
            "on",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "by",
            "from",
            "as",
            "i",
            "my",
            "me",
            "we",
            "our",
            "have",
            "has",
            "had",
            "that",
            "this",
            "it",
            "its",
            "not",
            "but",
            "do",
            "does",
            "did",
            "will",
            "would",
            "can",
            "could",
            "should",
            "shall",
            "may",
            "might",
            "am",
            "been",
            "being",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
        }
    )
    tokens = set(text.lower().split())
    return tokens - stopwords


def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _headline_vs_career(candidate: Candidate) -> float:
    """Compare headline tokens with career title tokens."""
    headline_tokens = _tokenize(candidate.profile.headline)
    if not headline_tokens:
        # No headline → assume neutral (0.5).
        return 0.5

    career_tokens: set[str] = set()
    for job in candidate.career_history:
        career_tokens.update(_tokenize(job.title))

    if not career_tokens:
        return 0.5

    return min(_jaccard(headline_tokens, career_tokens) * 3.0, 1.0)


def _headline_vs_skills(candidate: Candidate) -> float:
    """Compare headline tokens with skill names."""
    headline_tokens = _tokenize(candidate.profile.headline)
    if not headline_tokens:
        return 0.5

    skill_tokens: set[str] = set()
    for skill in candidate.skills:
        skill_tokens.update(_tokenize(skill.name))

    if not skill_tokens:
        return 0.5

    return min(_jaccard(headline_tokens, skill_tokens) * 4.0, 1.0)


def _summary_vs_skills(candidate: Candidate) -> float:
    """Compare summary tokens with skill names."""
    summary_tokens = _tokenize(candidate.profile.summary)
    if not summary_tokens:
        return 0.5

    skill_tokens: set[str] = set()
    for skill in candidate.skills:
        skill_tokens.update(_tokenize(skill.name))

    if not skill_tokens:
        return 0.5

    return min(_jaccard(summary_tokens, skill_tokens) * 5.0, 1.0)


def _education_vs_career(candidate: Candidate) -> float:
    """Compare education field with career domain."""
    if not candidate.education:
        return 0.5

    edu_tokens: set[str] = set()
    for edu in candidate.education:
        edu_tokens.update(_tokenize(edu.field_of_study))
        edu_tokens.update(_tokenize(edu.degree))

    career_tokens: set[str] = set()
    for job in candidate.career_history:
        career_tokens.update(_tokenize(job.title))
        career_tokens.update(_tokenize(job.industry))

    if not edu_tokens or not career_tokens:
        return 0.5

    return min(_jaccard(edu_tokens, career_tokens) * 4.0, 1.0)
