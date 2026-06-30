"""Leadership Detector — scores candidates on leadership signals."""

import re

from hiremind.domain.candidate import Candidate

# Leadership verbs in career descriptions.
_LEADERSHIP_VERBS: list[str] = [
    "mentored",
    "managed",
    "led",
    "owned",
    "architected",
    "coordinated",
    "directed",
    "supervised",
    "trained",
    "coached",
    "oversaw",
    "spearheaded",
    "guided",
    "established",
    "founded",
    "initiated",
]

_VERB_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(v) for v in _LEADERSHIP_VERBS) + r")\b",
    re.IGNORECASE,
)

# Leadership title keywords (presence in any title).
_TITLE_KEYWORDS: dict[str, float] = {
    "director": 1.0,
    "vp": 1.0,
    "vice president": 1.0,
    "head": 0.9,
    "principal": 0.8,
    "staff": 0.7,
    "lead": 0.7,
    "senior": 0.5,
    "manager": 0.8,
    "architect": 0.6,
}

# Team-size / people-management indicators.
_TEAM_PATTERN = re.compile(
    r"\b(?:team\s+of\s+\d+|managed\s+\d+|leading\s+\d+|\d+\s+(?:engineers?|developers?|members?))\b",
    re.IGNORECASE,
)


def score_leadership(candidate: Candidate) -> float:
    """Score a candidate's leadership signals (0.0–1.0).

    Combines:
        - Leadership verbs in career descriptions (40%)
        - Leadership title keywords (40%)
        - Team-management indicators (20%)
    """
    verb_score = _score_verbs(candidate)
    title_score = _score_titles(candidate)
    team_score = _score_team_management(candidate)

    raw = 0.4 * verb_score + 0.4 * title_score + 0.2 * team_score
    return round(min(raw, 1.0), 3)


def _score_verbs(candidate: Candidate) -> float:
    """Score based on leadership verbs in career descriptions."""
    text = " ".join((job.description or "") for job in candidate.career_history)
    if not text:
        return 0.0

    matches = len(_VERB_PATTERN.findall(text))
    # 4+ leadership verbs → max score.
    return min(matches / 4.0, 1.0)


def _score_titles(candidate: Candidate) -> float:
    """Score based on leadership keywords in job titles."""
    all_titles: list[str] = []
    if candidate.profile.current_title:
        all_titles.append(candidate.profile.current_title)
    for job in candidate.career_history:
        if job.title:
            all_titles.append(job.title)

    if not all_titles:
        return 0.0

    best_score = 0.0
    for title in all_titles:
        lowered = title.lower()
        for keyword, weight in _TITLE_KEYWORDS.items():
            if keyword in lowered:
                best_score = max(best_score, weight)

    return best_score


def _score_team_management(candidate: Candidate) -> float:
    """Score based on team-size indicators in descriptions."""
    text = " ".join((job.description or "") for job in candidate.career_history)
    if not text:
        return 0.0

    matches = len(_TEAM_PATTERN.findall(text))
    return min(matches / 2.0, 1.0)
