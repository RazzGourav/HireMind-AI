from dataclasses import dataclass

from hiremind.domain.career import Career
from hiremind.domain.education import Education
from hiremind.domain.profile import Profile
from hiremind.domain.skill import Skill


@dataclass(frozen=True, slots=True)
class RedrobSignals:
    github_activity_score: float | None = None
    recruiter_response_score: float | None = None
    has_github: bool | None = None
    open_to_work: bool | None = None
    notice_period_days: int | None = None
    preferred_work_mode: str | None = None
    willing_to_relocate: bool | None = None


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    profile: Profile
    career_history: list[Career]
    education: list[Education]
    skills: list[Skill]
    signals: RedrobSignals
