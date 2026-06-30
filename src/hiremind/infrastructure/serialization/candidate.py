from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hiremind.infrastructure.serialization.career import CareerRecord
from hiremind.infrastructure.serialization.education import EducationRecord
from hiremind.infrastructure.serialization.profile import ProfileRecord
from hiremind.infrastructure.serialization.signals import RedrobSignalsRecord
from hiremind.infrastructure.serialization.skill import SkillRecord


class CandidateRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    candidate_id: str = Field(min_length=1)
    profile: ProfileRecord = Field(default_factory=ProfileRecord)
    career_history: list[CareerRecord] = Field(default_factory=list)
    education: list[EducationRecord] = Field(default_factory=list)
    skills: list[SkillRecord] = Field(default_factory=list)
    signals: RedrobSignalsRecord = Field(default_factory=RedrobSignalsRecord)

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        if "candidate_id" not in normalized and "id" in normalized:
            normalized["candidate_id"] = normalized["id"]
        if "career_history" not in normalized and "career" in normalized:
            normalized["career_history"] = normalized["career"]
        if "signals" not in normalized and "redrob_signals" in normalized:
            normalized["signals"] = normalized["redrob_signals"]
        return normalized
