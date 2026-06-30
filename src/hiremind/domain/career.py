from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Career:
    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    duration_months: int | None = None
    is_current: bool | None = None
    industry: str | None = None
    company_size: str | None = None
