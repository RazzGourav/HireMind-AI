"""Tests for growth potential analyzer."""

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.education import Education
from hiremind.domain.profile import Profile
from hiremind.domain.skill import Skill
from hiremind.infrastructure.candidate.growth import score_growth


def _make_candidate(**kwargs: object) -> Candidate:
    """Build a minimal candidate for testing."""
    return Candidate(
        candidate_id=str(kwargs.get("cid", "CAND_001")),
        profile=kwargs.get("profile", Profile()),  # type: ignore[arg-type]
        career_history=kwargs.get("career", []),  # type: ignore[arg-type]
        education=kwargs.get("education", []),  # type: ignore[arg-type]
        skills=kwargs.get("skills", []),  # type: ignore[arg-type]
        signals=kwargs.get("signals", RedrobSignals()),  # type: ignore[arg-type]
    )


def test_growth_with_recent_ai_skills() -> None:
    """Candidate with recent AI skills scores higher."""
    cand = _make_candidate(
        skills=[
            Skill(name="Machine Learning", duration_months=12),
            Skill(name="PyTorch", duration_months=6),
            Skill(name="NLP", duration_months=18),
        ],
    )
    score = score_growth(cand)
    assert score > 0.0


def test_growth_with_github() -> None:
    """Candidate with GitHub activity gets a growth boost."""
    cand = _make_candidate(
        signals=RedrobSignals(github_activity_score=0.8, has_github=True),
    )
    score = score_growth(cand)
    assert score > 0.0


def test_growth_empty_candidate() -> None:
    """Empty candidate gets near-zero growth score."""
    cand = _make_candidate()
    score = score_growth(cand)
    assert score >= 0.0
    assert score <= 0.5  # Mostly defaults.


def test_growth_diverse_skills() -> None:
    """Candidate with many skills gets diversity bonus."""
    skills = [Skill(name=f"Skill_{i}") for i in range(20)]
    cand = _make_candidate(skills=skills)
    score = score_growth(cand)
    assert score > 0.0


def test_growth_recent_education() -> None:
    """Recent graduation contributes to growth score."""
    cand = _make_candidate(
        education=[Education(graduation_year=2024, field_of_study="CS")],
    )
    score = score_growth(cand)
    assert score > 0.0
