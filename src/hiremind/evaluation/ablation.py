"""Ablation study configuration and execution logic."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class AblationConfig:
    """Configuration overrides for a specific ablation run."""

    name: str
    description: str

    # Overrides
    disable_behavior: bool = False
    disable_ontology: bool = False
    disable_knowledge_graph: bool = False
    embeddings_only: bool = False
    rule_based_only: bool = False


# Standard set of ablation experiments
ABLATION_EXPERIMENTS = [
    AblationConfig(
        name="Baseline",
        description="Full hybrid model with all systems active.",
    ),
    AblationConfig(
        name="No Behavior",
        description="Behavioral signals (GitHub, recruiter response) removed.",
        disable_behavior=True,
    ),
    AblationConfig(
        name="No Ontology",
        description="Semantic ontology expansion disabled during retrieval.",
        disable_ontology=True,
    ),
    AblationConfig(
        name="No Knowledge Graph",
        description="Knowledge Graph features (depth, diversity) removed from ranking.",
        disable_knowledge_graph=True,
    ),
    AblationConfig(
        name="Embeddings Only",
        description="Dense vector retrieval only, no structured filters or graph ranking.",
        embeddings_only=True,
    ),
    AblationConfig(
        name="Rule-Based Only",
        description="Structured filters and boolean ranking only, no dense embeddings.",
        rule_based_only=True,
    ),
]


class AblationRunner:
    """Executes a series of ablation studies and compiles the results."""

    def __init__(self) -> None:
        self.results: dict[str, dict[str, Any]] = {}
        self.baseline_metrics: dict[str, Any] = {}

    def record_run(self, config: AblationConfig, metrics: dict[str, Any]) -> None:
        """Record the metrics for a specific ablation run."""
        if config.name == "Baseline":
            self.baseline_metrics = copy.deepcopy(metrics)

        self.results[config.name] = {
            "description": config.description,
            "metrics": copy.deepcopy(metrics),
            "deltas": self._compute_deltas(metrics),
        }

    def _compute_deltas(self, metrics: dict[str, Any]) -> dict[str, float]:
        """Compute the difference between these metrics and the baseline."""
        if not self.baseline_metrics:
            return {}

        deltas = {}
        for key in ["ndcg_at_10", "mean_average_precision", "recall_at_100", "mrr"]:
            baseline_val = self.baseline_metrics.get(key, 0.0)
            current_val = metrics.get(key, 0.0)
            deltas[key] = round(current_val - baseline_val, 4)

        return deltas

    def generate_report(self, output_path: str = "outputs/ablation.json") -> dict[str, Any]:
        """Generate the comprehensive ablation report."""
        if output_path:
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2)

        return self.results
