"""Pydantic schemas for Ranking and Reasoning outputs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class StrengthSchema(BaseModel):
    label: str
    description: str


class ConcernSchema(BaseModel):
    label: str
    severity: str
    description: str


class CandidateExplanationSchema(BaseModel):
    candidate_id: str
    final_score: float
    recommendation: str
    recruiter_summary: str
    strengths: list[StrengthSchema]
    concerns: list[ConcernSchema]


class RankedCandidateSchema(BaseModel):
    candidate_id: str
    rank: int
    final_score: float
    recommendation: str
    technical_score: float
    career_score: float
    behavior_score: float
    knowledge_score: float
    risk_penalty: float
    explanation: CandidateExplanationSchema | None = None
    profile_summary: dict[str, Any] | None = None


class RankingResponse(BaseModel):
    total_candidates_retrieved: int
    retrieval_latency_ms: float
    ranking_latency_ms: float
    results: list[RankedCandidateSchema]


class CompareRequest(BaseModel):
    candidate_a_id: str
    candidate_b_id: str


class ComparisonResponse(BaseModel):
    winner: str
    dimensions: list[dict[str, Any]]
    a_unique_strengths: list[str]
    b_unique_strengths: list[str]
    a_unique_concerns: list[str]
    b_unique_concerns: list[str]
