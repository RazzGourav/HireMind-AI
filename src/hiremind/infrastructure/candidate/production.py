"""Production Evidence Engine — scores candidates on production experience."""

import re

from hiremind.domain.candidate import Candidate

# Production verbs ranked by strength (higher weight = stronger signal).
_PRODUCTION_VERBS: list[tuple[str, float]] = [
    ("shipped", 1.0),
    ("deployed", 1.0),
    ("scaled", 0.95),
    ("owned", 0.9),
    ("architected", 0.9),
    ("optimized", 0.85),
    ("migrated", 0.85),
    ("automated", 0.8),
    ("built", 0.8),
    ("designed", 0.8),
    ("implemented", 0.75),
    ("developed", 0.7),
    ("maintained", 0.65),
    ("integrated", 0.65),
    ("refactored", 0.7),
    ("improved", 0.6),
    ("contributed", 0.5),
    ("worked on", 0.3),
    ("assisted", 0.2),
    ("learned", 0.1),
    ("studied", 0.1),
]

# Compile patterns for fast matching.
_VERB_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    (re.compile(rf"\b{re.escape(verb)}\b", re.IGNORECASE), weight)
    for verb, weight in _PRODUCTION_VERBS
]

# Production-context keywords that amplify the score.
_PRODUCTION_CONTEXT = re.compile(
    r"\b(?:production|prod|live|real[\s-]*time|scale|performance|"
    r"latency|throughput|pipeline|infrastructure|system|service|api|"
    r"million|billion|concurrent|availability|uptime|sla)\b",
    re.IGNORECASE,
)


def score_production(candidate: Candidate) -> float:
    """Score a candidate's production experience (0.0–1.0).

    Scans career descriptions for production verbs and context keywords.
    Weights stronger verbs (shipped, deployed) higher than weaker ones (learned).
    """
    all_text = _collect_career_text(candidate)
    if not all_text:
        return 0.0

    verb_score = _score_verbs(all_text)
    context_score = _score_context(all_text)

    # Blend: 70% verb strength + 30% production context.
    raw = 0.7 * verb_score + 0.3 * context_score
    return round(min(raw, 1.0), 3)


def _collect_career_text(candidate: Candidate) -> str:
    """Concatenate all career description text."""
    parts: list[str] = []
    for job in candidate.career_history:
        if job.description:
            parts.append(job.description)
    if candidate.profile.summary:
        parts.append(candidate.profile.summary)
    return " ".join(parts)


def _score_verbs(text: str) -> float:
    """Score based on production verb matches, weighted by verb strength."""
    if not text:
        return 0.0

    total_weight = 0.0
    matches = 0

    for pattern, weight in _VERB_PATTERNS:
        count = len(pattern.findall(text))
        if count > 0:
            total_weight += weight * min(count, 3)  # Cap per-verb at 3.
            matches += min(count, 3)

    if matches == 0:
        return 0.0

    # Average weight of matched verbs, normalised.
    avg_weight = total_weight / matches
    # More unique verbs → higher score (diversity bonus).
    diversity = min(matches / 8.0, 1.0)
    return avg_weight * 0.6 + diversity * 0.4


def _score_context(text: str) -> float:
    """Score based on production-context keyword density."""
    if not text:
        return 0.0

    matches = len(_PRODUCTION_CONTEXT.findall(text))
    # Normalise: 5+ context keywords = max score.
    return min(matches / 5.0, 1.0)
