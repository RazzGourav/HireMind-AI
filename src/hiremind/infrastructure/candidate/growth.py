"""Growth Potential Analyzer — scores candidate learning trajectory."""

from hiremind.domain.candidate import Candidate

# AI/ML related skill keywords (case-insensitive matching).
_AI_ML_KEYWORDS = frozenset(
    {
        "machine learning",
        "deep learning",
        "nlp",
        "ai",
        "neural",
        "transformer",
        "bert",
        "gpt",
        "llm",
        "embedding",
        "retrieval",
        "faiss",
        "vector",
        "pytorch",
        "tensorflow",
        "hugging face",
        "fine-tuning",
        "lora",
        "qlora",
        "rag",
        "langchain",
        "computer vision",
        "recommendation",
        "ranking",
    }
)


def score_growth(candidate: Candidate) -> float:
    """Score a candidate's growth potential (0.0–1.0).

    Signals:
        - Recent AI/ML skill acquisition (25%)
        - Career transitions toward tech/ML (25%)
        - GitHub activity (20%)
        - Skill diversity & count (15%)
        - Education recency (15%)
    """
    recent_score = _score_recent_ai_skills(candidate)
    transition_score = _score_career_transition(candidate)
    github_score = _score_github(candidate)
    diversity_score = _score_skill_diversity(candidate)
    education_score = _score_education_recency(candidate)

    raw = (
        0.25 * recent_score
        + 0.25 * transition_score
        + 0.20 * github_score
        + 0.15 * diversity_score
        + 0.15 * education_score
    )
    return round(min(raw, 1.0), 3)


def _score_recent_ai_skills(candidate: Candidate) -> float:
    """Score based on recently acquired AI/ML skills."""
    if not candidate.skills:
        return 0.0

    recent_ai = 0
    total_ai = 0

    for skill in candidate.skills:
        lowered = skill.name.lower()
        is_ai = any(kw in lowered for kw in _AI_ML_KEYWORDS)
        if is_ai:
            total_ai += 1
            # Recent = less than 24 months duration (recently acquired).
            if skill.duration_months is not None and skill.duration_months <= 24:
                recent_ai += 1
            elif skill.duration_months is None:
                # No duration = could be recent.
                recent_ai += 0.5

    if total_ai == 0:
        return 0.0

    return min(recent_ai / 3.0, 1.0)


def _score_career_transition(candidate: Candidate) -> float:
    """Score based on career transition toward AI/ML roles."""
    if len(candidate.career_history) < 2:
        return 0.0

    titles = [(job.title or "").lower() for job in candidate.career_history]

    # Check if recent titles are more AI/ML oriented than older titles.
    early_ai = sum(1 for t in titles[len(titles) // 2 :] if _is_ai_title(t))
    recent_ai = sum(1 for t in titles[: len(titles) // 2 + 1] if _is_ai_title(t))

    if recent_ai > early_ai:
        return min((recent_ai - early_ai) / 2.0, 1.0)
    return 0.0


def _is_ai_title(title: str) -> bool:
    """Check if a title suggests AI/ML role."""
    ai_keywords = {"ml", "machine learning", "ai", "data scien", "nlp", "deep learning"}
    return any(kw in title for kw in ai_keywords)


def _score_github(candidate: Candidate) -> float:
    """Score based on GitHub activity signal."""
    score = candidate.signals.github_activity_score
    if score is not None and score > 0:
        return min(score, 1.0)
    if candidate.signals.has_github:
        return 0.3  # Has account but no activity score.
    return 0.0


def _score_skill_diversity(candidate: Candidate) -> float:
    """Score based on breadth of skill portfolio."""
    count = len(candidate.skills)
    if count == 0:
        return 0.0
    # 15+ skills = max diversity score.
    return min(count / 15.0, 1.0)


def _score_education_recency(candidate: Candidate) -> float:
    """Score based on education recency."""
    if not candidate.education:
        return 0.0

    max_year = 0
    for edu in candidate.education:
        if edu.graduation_year and edu.graduation_year > max_year:
            max_year = edu.graduation_year

    if max_year == 0:
        return 0.0

    # Recent graduation (within 5 years of 2025) → high score.
    recency = max(0, max_year - 2020) / 5.0
    return min(recency, 1.0)
