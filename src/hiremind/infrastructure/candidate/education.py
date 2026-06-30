"""Education Intelligence — tier scoring and field relevance analysis."""

from hiremind.domain.education import Education

_TIER_SCORES: dict[str, float] = {
    "tier_1": 1.0,
    "tier_2": 0.7,
    "tier_3": 0.4,
    "tier_4": 0.2,
}

_RELEVANT_FIELDS = frozenset(
    {
        "computer science",
        "cs",
        "information technology",
        "it",
        "artificial intelligence",
        "machine learning",
        "data science",
        "software engineering",
        "electrical engineering",
        "electronics",
        "mathematics",
        "statistics",
        "applied mathematics",
        "computational",
        "informatics",
    }
)

_DEGREE_WEIGHTS: dict[str, float] = {
    "ph.d": 1.0,
    "phd": 1.0,
    "doctorate": 1.0,
    "m.s": 0.8,
    "m.tech": 0.8,
    "m.e": 0.8,
    "master": 0.8,
    "mba": 0.7,
    "b.tech": 0.5,
    "b.e": 0.5,
    "b.s": 0.5,
    "bachelor": 0.5,
    "b.sc": 0.5,
}


def analyze_education(education_list: list[Education]) -> float:
    """Score a candidate's education (0.0–1.0).

    Combines:
        - Institution tier (40%)
        - Field relevance to AI/ML/CS (40%)
        - Degree level (20%)
    """
    if not education_list:
        return 0.0

    tier_score = _best_tier(education_list)
    field_score = _field_relevance(education_list)
    degree_score = _degree_level(education_list)

    return round(0.4 * tier_score + 0.4 * field_score + 0.2 * degree_score, 3)


def _best_tier(education_list: list[Education]) -> float:
    """Return the best tier score among all education entries."""
    best = 0.0
    for edu in education_list:
        tier = (edu.tier or "").lower().strip()
        score = _TIER_SCORES.get(tier, 0.1)
        best = max(best, score)
    return best


def _field_relevance(education_list: list[Education]) -> float:
    """Score field relevance to AI/ML/CS."""
    for edu in education_list:
        field = (edu.field_of_study or "").lower()
        if any(rf in field for rf in _RELEVANT_FIELDS):
            return 1.0
    return 0.2  # Unrelated field.


def _degree_level(education_list: list[Education]) -> float:
    """Score based on highest degree level."""
    best = 0.0
    for edu in education_list:
        degree = (edu.degree or "").lower()
        for key, weight in _DEGREE_WEIGHTS.items():
            if key in degree:
                best = max(best, weight)
                break
    return best
