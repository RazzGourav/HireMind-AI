"""Reasoning — Explainability & Recruiter Reasoning Engine.

Provides feature attribution, evidence collection, requirement alignment,
strength/concern detection, candidate comparison, interview recommendations,
and explanation validation.
"""

from hiremind.reasoning.comparison_engine import ComparisonEngine
from hiremind.reasoning.concern_detector import ConcernDetector
from hiremind.reasoning.evidence_collector import EvidenceCollector
from hiremind.reasoning.explanation_builder import ReasoningExplanationBuilder
from hiremind.reasoning.feature_attribution import FeatureAttributionEngine
from hiremind.reasoning.recommendation_engine import RecommendationEngine
from hiremind.reasoning.requirement_alignment import RequirementAlignmentEngine
from hiremind.reasoning.strength_detector import StrengthDetector
from hiremind.reasoning.validator import ExplanationValidator

__all__ = [
    "ComparisonEngine",
    "ConcernDetector",
    "EvidenceCollector",
    "ExplanationValidator",
    "FeatureAttributionEngine",
    "ReasoningExplanationBuilder",
    "RecommendationEngine",
    "RequirementAlignmentEngine",
    "StrengthDetector",
]
