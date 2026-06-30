from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    proficiency: str | None = None
    endorsements: int = Field(default=0, ge=0)
    duration_months: int | None = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("skill name cannot be empty")
        return name
