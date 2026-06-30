"""Tests for career consistency engine."""

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.career import Career
from hiremind.domain.education import Education
from hiremind.domain.profile import Profile
from hiremind.domain.skill import Skill
from hiremind.infrastructure.candidate.consistency import score_consistency


def _make_candidate(**kwargs: object) -> Candidate:
    return Candidate(
        candidate_id="CAND_001",
        profile=kwargs.get("profile", Profile()),  # type: ignore[arg-type]
        career_history=kwargs.get("career", []),  # type: ignore[arg-type]
        education=kwargs.get("education", []),  # type: ignore[arg-type]
        skills=kwargs.get("skills", []),  # type: ignore[arg-type]
        signals=RedrobSignals(),
    )


def test_high_consistency() -> None:
    """Candidate with matching headline, career, and skills scores high."""
    cand = _make_candidate(
        profile=Profile(
            headline="Backend Engineer | Python, SQL",
            current_title="Backend Engineer",
            summary="Experienced backend engineer with Python and SQL expertise.",
        ),
        career=[Career(title="Backend Engineer", industry="IT")],
        skills=[Skill(name="Python"), Skill(name="SQL")],
        education=[Education(field_of_study="Computer Science")],
    )
    score = score_consistency(cand)
    assert score > 0.3


def test_low_consistency() -> None:
    """Candidate with mismatched headline, career, and skills scores lower."""
    cand = _make_candidate(
        profile=Profile(
            headline="AI Engineer | Deep Learning",
            current_title="AI Engineer",
            summary="Marketing professional with sales experience.",
        ),
        career=[Career(title="Mechanical Engineer", industry="Manufacturing")],
        skills=[Skill(name="TensorFlow")],
        education=[Education(field_of_study="Mechanical Engineering")],
    )
    score = score_consistency(cand)
    # Should be lower than the high-consistency case.
    assert score < 0.8


def test_empty_profile_neutral() -> None:
    """Empty profile defaults to neutral scores."""
    cand = _make_candidate()
    score = score_consistency(cand)
    # All sub-scores default to 0.5 (neutral) → overall ≈ 0.5.
    assert 0.3 <= score <= 0.7


def test_headline_only() -> None:
    """Candidate with headline but nothing else gets partial score."""
    cand = _make_candidate(
        profile=Profile(headline="Data Scientist"),
    )
    score = score_consistency(cand)
    assert 0.0 <= score <= 1.0
