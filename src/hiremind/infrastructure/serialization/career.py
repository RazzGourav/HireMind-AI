from pydantic import BaseModel, ConfigDict, Field, field_validator

from hiremind.infrastructure.serialization.validators import validate_iso_date


class CareerRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    duration_months: int | None = Field(default=None, ge=0)
    is_current: bool | None = None
    industry: str | None = None
    company_size: str | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, value: str | None) -> str | None:
        return validate_iso_date(value)
