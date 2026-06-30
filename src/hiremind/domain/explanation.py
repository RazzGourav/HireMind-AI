"""Immutable domain models for the Explainability & Reasoning layer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AlignmentStatus(Enum):
    """Classification of how a JD requirement aligns with candidate skills."""

    MATCHED = "matched"
    PARTIAL = "partial"
    MISSING = "missing"


class ConcernSeverity(Enum):
    """Severity level for detected concerns."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class ScoreAttribution:
    """A single component's contribution to the final score."""

    component: str
    label: str
    raw_score: float
    weight: float
    weighted_contribution: float
    percentage_of_final: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "component": self.component,
            "label": self.label,
            "raw_score": round(self.raw_score, 4),
            "weight": round(self.weight, 4),
            "weighted_contribution": round(self.weighted_contribution, 4),
            "percentage_of_final": round(self.percentage_of_final, 2),
        }


@dataclass(frozen=True, slots=True)
class RequirementAlignment:
    """Alignment result for a single JD requirement against a candidate."""

    requirement_id: str
    requirement_name: str
    required: bool
    status: AlignmentStatus
    matched_skill: str | None = None
    evidence: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "requirement_id": self.requirement_id,
            "requirement_name": self.requirement_name,
            "required": self.required,
            "status": self.status.value,
            "matched_skill": self.matched_skill,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class Strength:
    """A detected strength of a candidate."""

    label: str
    description: str
    evidence: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "description": self.description,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class Concern:
    """A detected concern about a candidate."""

    label: str
    severity: ConcernSeverity
    description: str
    evidence: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "severity": self.severity.value,
            "description": self.description,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class CandidateExplanation:
    """Complete explanation for a candidate's ranking decision."""

    candidate_id: str
    final_score: float
    attributions: tuple[ScoreAttribution, ...] = ()
    requirement_alignments: tuple[RequirementAlignment, ...] = ()
    strengths: tuple[Strength, ...] = ()
    concerns: tuple[Concern, ...] = ()
    recruiter_summary: str = ""
    recommendation: str = ""
    recommendation_confidence: float = 0.0
    recommendation_rationale: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "final_score": round(self.final_score, 2),
            "score_attributions": [a.to_dict() for a in self.attributions],
            "requirement_alignments": [r.to_dict() for r in self.requirement_alignments],
            "strengths": [s.to_dict() for s in self.strengths],
            "concerns": [c.to_dict() for c in self.concerns],
            "recruiter_summary": self.recruiter_summary,
            "interview_recommendation": {
                "recommendation": self.recommendation,
                "confidence": round(self.recommendation_confidence, 2),
                "rationale": self.recommendation_rationale,
            },
        }


@dataclass(frozen=True, slots=True)
class DimensionComparison:
    """Comparison of a single scoring dimension between two candidates."""

    dimension: str
    candidate_a_score: float
    candidate_b_score: float
    winner: str
    delta: float

    def to_dict(self) -> dict[str, object]:
        return {
            "dimension": self.dimension,
            "candidate_a_score": round(self.candidate_a_score, 2),
            "candidate_b_score": round(self.candidate_b_score, 2),
            "winner": self.winner,
            "delta": round(self.delta, 2),
        }


@dataclass(frozen=True, slots=True)
class CandidateComparison:
    """Structured head-to-head comparison of two candidates."""

    candidate_a_id: str
    candidate_b_id: str
    overall_winner: str
    dimensions: tuple[DimensionComparison, ...] = ()
    a_unique_strengths: tuple[str, ...] = ()
    b_unique_strengths: tuple[str, ...] = ()
    a_unique_concerns: tuple[str, ...] = ()
    b_unique_concerns: tuple[str, ...] = ()
    summary: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_a_id": self.candidate_a_id,
            "candidate_b_id": self.candidate_b_id,
            "overall_winner": self.overall_winner,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "candidate_a_unique_strengths": list(self.a_unique_strengths),
            "candidate_b_unique_strengths": list(self.b_unique_strengths),
            "candidate_a_unique_concerns": list(self.a_unique_concerns),
            "candidate_b_unique_concerns": list(self.b_unique_concerns),
            "summary": self.summary,
        }
