from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RedrobSignalsRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    github_activity_score: float | None = Field(default=None, ge=-1, le=100)
    recruiter_response_score: float | None = Field(default=None, ge=-1, le=1)
    has_github: bool | None = None
    open_to_work: bool | None = None
    notice_period_days: int | None = None
    preferred_work_mode: str | None = None
    willing_to_relocate: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def map_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        mapped = dict(value)
        # Map recruiter_response_rate -> recruiter_response_score
        if "recruiter_response_score" not in mapped and "recruiter_response_rate" in mapped:
            mapped["recruiter_response_score"] = mapped["recruiter_response_rate"]

        # Map open_to_work_flag -> open_to_work
        if "open_to_work" not in mapped and "open_to_work_flag" in mapped:
            mapped["open_to_work"] = mapped["open_to_work_flag"]

        # Determine has_github
        if "has_github" not in mapped:
            git_score = mapped.get("github_activity_score", -1)
            mapped["has_github"] = git_score > 0

        return mapped
