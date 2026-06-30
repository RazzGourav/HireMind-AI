"""Pydantic schemas for Candidate models."""

from __future__ import annotations

from pydantic import BaseModel


class CandidateProfileSchema(BaseModel):
    current_title: str | None = None
    headline: str | None = None
    summary: str | None = None
    country: str | None = None
    total_experience_months: int = 0
    notice_period_days: int | None = None


class CandidateSkillSchema(BaseModel):
    name: str
    endorsements: int = 0


class CandidateSchema(BaseModel):
    candidate_id: str
    profile: CandidateProfileSchema
    skills: list[CandidateSkillSchema]
    # Other raw fields can be added here
