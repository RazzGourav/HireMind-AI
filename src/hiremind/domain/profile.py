from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Profile:
    current_title: str | None = None
    headline: str | None = None
    summary: str | None = None
    country: str | None = None
    current_company: str | None = None
    current_company_size: str | None = None
    current_industry: str | None = None
    total_experience_months: int = 0
    notice_period_days: int | None = None
    open_to_work: bool | None = None

    @property
    def experience_years(self) -> float:
        return round(self.total_experience_months / 12, 2)
