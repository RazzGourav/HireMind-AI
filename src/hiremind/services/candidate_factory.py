from dataclasses import asdict
from typing import Any

from pydantic import ValidationError

from hiremind.domain import Candidate, Career, Education, Profile, RedrobSignals, Skill
from hiremind.infrastructure.serialization import CandidateRecord


class CandidateFactory:
    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> Candidate:
        record = CandidateRecord.model_validate(payload)
        return cls.from_record(record)

    @staticmethod
    def from_record(record: CandidateRecord) -> Candidate:
        return Candidate(
            candidate_id=record.candidate_id,
            profile=Profile(
                current_title=record.profile.current_title,
                headline=record.profile.headline,
                summary=record.profile.summary,
                country=record.profile.country,
                current_company=record.profile.current_company,
                current_company_size=record.profile.current_company_size,
                current_industry=record.profile.current_industry,
                total_experience_months=record.profile.total_experience_months,
                notice_period_days=record.profile.notice_period_days,
                open_to_work=record.profile.open_to_work,
            ),
            career_history=[
                Career(
                    company=item.company,
                    title=item.title,
                    start_date=item.start_date,
                    end_date=item.end_date,
                    description=item.description,
                    duration_months=item.duration_months,
                    is_current=item.is_current,
                    industry=item.industry,
                    company_size=item.company_size,
                )
                for item in record.career_history
            ],
            education=[
                Education(
                    institution=item.institution,
                    degree=item.degree,
                    field_of_study=item.field_of_study,
                    tier=item.tier,
                    graduation_year=item.graduation_year,
                )
                for item in record.education
            ],
            skills=[
                Skill(
                    name=item.name,
                    proficiency=item.proficiency,
                    endorsements=item.endorsements,
                    duration_months=item.duration_months,
                )
                for item in record.skills
            ],
            signals=RedrobSignals(
                github_activity_score=record.signals.github_activity_score,
                recruiter_response_score=record.signals.recruiter_response_score,
                has_github=record.signals.has_github,
                open_to_work=record.signals.open_to_work,
                notice_period_days=record.signals.notice_period_days,
                preferred_work_mode=record.signals.preferred_work_mode,
                willing_to_relocate=record.signals.willing_to_relocate,
            ),
        )

    @staticmethod
    def to_raw(candidate: Candidate) -> dict[str, Any]:
        return asdict(candidate)


def format_validation_errors(error: ValidationError) -> list[str]:
    messages: list[str] = []
    for item in error.errors():
        path = ".".join(str(part) for part in item["loc"])
        messages.append(f"{path}: {item['msg']}")
    return messages
