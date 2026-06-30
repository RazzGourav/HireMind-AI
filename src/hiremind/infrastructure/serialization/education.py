from pydantic import BaseModel, ConfigDict, Field


class EducationRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    tier: str | None = None
    graduation_year: int | None = Field(default=None, ge=1900, le=2100)
