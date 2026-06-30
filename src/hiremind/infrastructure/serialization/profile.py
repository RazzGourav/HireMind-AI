from pydantic import BaseModel, ConfigDict, Field


class ProfileRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    current_title: str | None = None
    headline: str | None = None
    summary: str | None = None
    country: str | None = None
    current_company: str | None = None
    current_company_size: str | None = None
    current_industry: str | None = None
    total_experience_months: int = Field(default=0, ge=0)
    notice_period_days: int | None = Field(default=None, ge=0)
    open_to_work: bool | None = None
