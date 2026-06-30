"""Ranking Service — orchestrator for hybrid candidate ranking and explainability."""

import json
import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from hiremind.domain.candidate_features import CandidateFeatures
from hiremind.domain.explanation import CandidateExplanation
from hiremind.domain.requirement import ParsedRequirements
from hiremind.domain.retrieval_result import RetrievalResult
from hiremind.ranking.behavior_ranker import BehaviorRanker
from hiremind.ranking.calibration import ScoreCalibrator
from hiremind.ranking.career_ranker import CareerRanker
from hiremind.ranking.explanation_builder import ExplanationBuilder
from hiremind.ranking.graph_ranker import GraphRanker
from hiremind.ranking.risk_engine import RiskEngine
from hiremind.ranking.score_fusion import ScoreFusionEngine
from hiremind.ranking.technical_ranker import TechnicalRanker
from hiremind.reasoning.comparison_engine import ComparisonEngine
from hiremind.reasoning.explanation_builder import ReasoningExplanationBuilder


class RankingService:
    """Evaluates retrieved candidates using subscore engines and produces calibrated, explained rankings."""

    def __init__(self, artifacts_dir: str | Path = "artifacts", max_notice_days: int = 90) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Subscore rankers
        self.tech_ranker = TechnicalRanker()
        self.career_ranker = CareerRanker()
        self.behavior_ranker = BehaviorRanker()
        self.graph_ranker = GraphRanker()
        self.risk_engine = RiskEngine()

        # Score components
        self.fusion = ScoreFusionEngine()
        self.calibrator = ScoreCalibrator()
        self.explainer = ExplanationBuilder()

        # Reasoning layer (Milestone 8)
        self.reasoning_builder = ReasoningExplanationBuilder(max_notice_days=max_notice_days)
        self.comparison_engine = ComparisonEngine()

        # Stores for output generation
        self._explanations: list[CandidateExplanation] = []
        self._recommendations: list[dict[str, object]] = []

    @property
    def ranking_model_path(self) -> Path:
        return self.artifacts_dir / "ranking_model.pkl"

    def rank_retrieved(
        self,
        retrieved: list[RetrievalResult],
        candidate_store: Any,
        features: list[CandidateFeatures],
        requirements: ParsedRequirements,
        max_notice_days: int = 90,
    ) -> list[dict[str, object]]:
        """Run the end-to-end scoring, risk assessment, fusion and calibration for candidates."""
        id_to_feat = {f.candidate_id: f for f in features}

        candidate_records = []
        self._explanations = []
        self._recommendations = []

        for item in retrieved:
            cid = item.candidate_id
            cand = candidate_store.get(cid)
            feat = id_to_feat.get(cid)

            if not cand or not feat:
                continue

            # Calculate subscores
            tech = self.tech_ranker.score(cand, feat, requirements)
            career = self.career_ranker.score(cand, feat)
            behavior = self.behavior_ranker.score(cand, feat)
            graph = self.graph_ranker.score(cand, feat, requirements)

            # Growth and Leadership directly from feature store
            growth = feat.growth_score if hasattr(feat, "growth_score") else 0.0
            leadership = feat.leadership_score if hasattr(feat, "leadership_score") else 0.0

            # Calculate risk penalty
            penalty = self.risk_engine.calculate_penalty(
                cand, feat, requirements, max_notice_days=max_notice_days
            )

            # Fuse scores
            final_raw, components = self.fusion.fuse(
                tech, career, behavior, graph, growth, leadership, penalty
            )

            record = {
                "candidate_id": cid,
                "final_score": final_raw,
                "technical_score": tech * 100.0,
                "career_score": career * 100.0,
                "behavior_score": behavior * 100.0,
                "knowledge_score": graph * 100.0,
                "growth_score": growth * 100.0,
                "leadership_score": leadership * 100.0,
                "risk_penalty": penalty * 100.0,
                "components": components,
            }
            candidate_records.append(record)

        # Calibrate and sort deterministically
        sorted_records = self.calibrator.rank_candidates(candidate_records)

        # Build explanations with rank context
        for rank_idx, rec in enumerate(sorted_records):
            rank = rank_idx + 1
            cid = rec["candidate_id"]
            cand = candidate_store.get(cid)
            feat = id_to_feat.get(cid)
            components = rec["components"]
            final_calibrated = rec["final_score"]

            # Build legacy explanation (backward compatible)
            explanation_text = self.explainer.build_explanation(cid, components)

            # Build full reasoning explanation
            candidate_explanation = self.reasoning_builder.build(
                candidate=cand,
                features=feat,
                requirements=requirements,
                components=components,
                final_score=final_calibrated,
                rank=rank,
            )
            self._explanations.append(candidate_explanation)

            # Store recommendation
            self._recommendations.append(
                {
                    "candidate_id": cid,
                    "recommendation": candidate_explanation.recommendation,
                    "confidence": candidate_explanation.recommendation_confidence,
                    "rationale": candidate_explanation.recommendation_rationale,
                }
            )

            # Update record
            rec["explanation"] = explanation_text
            rec["recruiter_summary"] = candidate_explanation.recruiter_summary
            rec["recommendation"] = candidate_explanation.recommendation
            del rec["components"]

        return sorted_records

    def save_model(self) -> Path:
        """Serialize scoring parameters to disk."""
        with self.ranking_model_path.open("wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
        return self.ranking_model_path

    def save_top_preview(
        self, records: list[dict[str, object]], path: str = "outputs/top100_preview.csv"
    ) -> None:
        """Save the top 100 candidates preview to CSV."""
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        top_100 = records[:100]
        rows = []
        for rec in top_100:
            rows.append(
                {
                    "candidate_id": rec["candidate_id"],
                    "final_score": rec["final_score"],
                    "technical_score": rec["technical_score"],
                    "career_score": rec["career_score"],
                    "behavior_score": rec["behavior_score"],
                    "knowledge_score": rec["knowledge_score"],
                    "risk_penalty": rec["risk_penalty"],
                    "recommendation": rec.get("recommendation", ""),
                }
            )

        df = pd.DataFrame(rows)
        df.to_csv(out_path, index=False)

    def save_explanations(self, path: str = "outputs/candidate_explanations.json") -> None:
        """Save full candidate explanations to JSON."""
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        data = [exp.to_dict() for exp in self._explanations]
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_recommendations(self, path: str = "outputs/interview_recommendations.json") -> None:
        """Save interview recommendations to JSON."""
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(self._recommendations, f, indent=2, ensure_ascii=False)

    def save_comparison(
        self,
        records: list[dict[str, object]],
        path: str = "outputs/candidate_comparison.json",
    ) -> None:
        """Compare the top 2 ranked candidates and save the comparison."""
        if len(self._explanations) < 2 or len(records) < 2:
            return

        # Find top 2 explanations matching top 2 records
        id_to_exp = {e.candidate_id: e for e in self._explanations}
        exp_a = id_to_exp.get(str(records[0]["candidate_id"]))
        exp_b = id_to_exp.get(str(records[1]["candidate_id"]))

        if not exp_a or not exp_b:
            return

        comparison = self.comparison_engine.compare(exp_a, exp_b, records[0], records[1])

        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(comparison.to_dict(), f, indent=2, ensure_ascii=False)
