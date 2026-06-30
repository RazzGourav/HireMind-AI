"""Pydantic schemas for Request and Response objects."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class JDParsingResponse(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    negative_requirements: list[str] = Field(default_factory=list)


class RankingRequest(BaseModel):
    top_k: int = 100
    max_notice_days: int | None = 90
    include_explanations: bool = True


class CopilotRequest(BaseModel):
    query: str


class CopilotResponse(BaseModel):
    answer: str
    structured_data: dict[str, Any] | None = None
