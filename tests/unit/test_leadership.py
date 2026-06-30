"""Tests for leadership detector."""

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.career import Career
from hiremind.domain.profile import Profile
from hiremind.infrastructure.candidate.leadership import score_leadership


def _make_candidate(**kwargs: object) -> Candidate:
    return Candidate(
        candidate_id="CAND_001",
        profile=kwargs.get("profile", Profile()),  # type: ignore[arg-type]
        career_history=kwargs.get("career", []),  # type: ignore[arg-type]
        education=[],
        skills=[],
        signals=RedrobSignals(),
    )


def test_leadership_with_verbs() -> None:
    """Career descriptions with leadership verbs score higher."""
    cand = _make_candidate(
        career=[
            Career(
                title="Engineer",
                description="Led a team of 5 engineers. Mentored junior developers. Coordinated cross-team efforts.",
            )
        ]
    )
    score = score_leadership(cand)
    assert score > 0.2


def test_leadership_with_senior_title() -> None:
    """Senior/lead titles contribute to leadership score."""
    cand = _make_candidate(
        profile=Profile(current_title="Staff Engineer"),
        career=[Career(title="Staff Engineer")],
    )
    score = score_leadership(cand)
    assert score > 0.1


def test_leadership_with_manager_title() -> None:
    """Manager titles score high."""
    cand = _make_candidate(
        profile=Profile(current_title="Engineering Manager"),
        career=[Career(title="Engineering Manager", description="Managed 12 engineers.")],
    )
    score = score_leadership(cand)
    assert score > 0.3


def test_leadership_junior_no_desc() -> None:
    """Junior candidate with no descriptions gets low leadership."""
    cand = _make_candidate(
        profile=Profile(current_title="Junior Developer"),
        career=[Career(title="Junior Developer")],
    )
    score = score_leadership(cand)
    assert score < 0.3


def test_leadership_empty() -> None:
    """Empty candidate gets zero leadership."""
    cand = _make_candidate()
    score = score_leadership(cand)
    assert score == 0.0
