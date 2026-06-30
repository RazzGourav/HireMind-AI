"""Unit tests for the StructuredFilterEngine."""

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.profile import Profile
from hiremind.domain.requirement import ExperienceRequirement, ParsedRequirements
from hiremind.domain.skill import Skill
from hiremind.retrieval.filter_engine import StructuredFilterEngine


def _make_candidate(
    cid: str,
    years_exp: float,
    notice_days: int,
    work_mode: str,
    skills_list: list[str],
) -> Candidate:
    return Candidate(
        candidate_id=cid,
        profile=Profile(total_experience_months=int(years_exp * 12)),
        career_history=[],
        education=[],
        skills=[Skill(name=name) for name in skills_list],
        signals=RedrobSignals(
            notice_period_days=notice_days,
            preferred_work_mode=work_mode,
            willing_to_relocate=False,
        ),
    )


def test_experience_filter() -> None:
    engine = StructuredFilterEngine()
    cand = _make_candidate(
        "CAND_1", years_exp=5.0, notice_days=30, work_mode="remote", skills_list=[]
    )

    reqs = ParsedRequirements(experience=ExperienceRequirement(min_years=3, max_years=6))
    assert engine.filter_candidate(cand, requirements=reqs) is True

    reqs_fail = ParsedRequirements(experience=ExperienceRequirement(min_years=6))
    assert engine.filter_candidate(cand, requirements=reqs_fail) is False


def test_notice_period_filter() -> None:
    engine = StructuredFilterEngine()
    cand = _make_candidate(
        "CAND_1", years_exp=5.0, notice_days=120, work_mode="remote", skills_list=[]
    )

    # Should filter out because notice period (120) > max_notice_days (90)
    assert engine.filter_candidate(cand, max_notice_days=90) is False
    assert engine.filter_candidate(cand, max_notice_days=150) is True


def test_work_mode_filter() -> None:
    engine = StructuredFilterEngine()
    cand = _make_candidate(
        "CAND_1", years_exp=5.0, notice_days=30, work_mode="onsite", skills_list=[]
    )

    # Onsite is not in allowed work modes (remote/hybrid)
    assert engine.filter_candidate(cand, allowed_work_modes=["remote", "hybrid"]) is False
    assert engine.filter_candidate(cand, allowed_work_modes=["onsite"]) is True


def test_mandatory_skills_filter() -> None:
    engine = StructuredFilterEngine()
    cand = _make_candidate(
        "CAND_1",
        years_exp=5.0,
        notice_days=30,
        work_mode="remote",
        skills_list=["Python", "FastAPI"],
    )

    assert engine.filter_candidate(cand, mandatory_skills=["Python"]) is True
    assert engine.filter_candidate(cand, mandatory_skills=["Go"]) is False
