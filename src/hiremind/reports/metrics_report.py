"""Generates a cohesive human-readable Markdown performance report."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class PerformanceReporter:
    """Combines metrics, profiling, and ablation data into a Markdown report."""

    def __init__(
        self,
        metrics: dict[str, Any],
        profiling: dict[str, Any],
        ablation: dict[str, Any],
        error_analysis: dict[str, Any],
    ) -> None:
        self.metrics = metrics
        self.profiling = profiling
        self.ablation = ablation
        self.error_analysis = error_analysis

    def generate(self, output_path: str = "outputs/performance.md") -> str:
        """Render the Markdown report and write to disk."""
        lines = [
            "# HireMind Evaluation & Benchmarking Report",
            "",
            "## 1. Core Ranking Metrics",
            "| Metric | Value |",
            "|---|---|",
            f"| **NDCG@10** | {self.metrics.get('ndcg_at_10', 0):.4f} |",
            f"| **NDCG@50** | {self.metrics.get('ndcg_at_50', 0):.4f} |",
            f"| **MAP** | {self.metrics.get('mean_average_precision', 0):.4f} |",
            f"| **Precision@10** | {self.metrics.get('precision_at_10', 0):.4f} |",
            f"| **Recall@100** | {self.metrics.get('recall_at_100', 0):.4f} |",
            f"| **MRR** | {self.metrics.get('mrr', 0):.4f} |",
            f"| **Candidate Diversity** | {self.metrics.get('diversity_at_10', 0):.4f} |",
            "",
            "## 2. System Profiling & Latency",
            "| Benchmark | Value |",
            "|---|---|",
        ]

        summary = self.profiling.get("summary", {})
        lines.extend(
            [
                f"| **Total Candidates Processed** | {summary.get('total_candidates', 0):,} |",
                f"| **Total Pipeline Latency** | {summary.get('total_latency_ms', 0):.2f} ms |",
                f"| **Retrieval Latency** | {summary.get('retrieval_latency_ms', 0):.2f} ms |",
                f"| **Ranking Latency** | {summary.get('ranking_latency_ms', 0):.2f} ms |",
                f"| **Throughput** | {summary.get('throughput_candidates_per_sec', 0):.2f} cand/sec |",
                f"| **Peak Memory Usage** | {summary.get('peak_memory_mb', 0):.2f} MB |",
                "",
            ]
        )

        lines.extend(
            [
                "## 3. Ablation Study",
                "Impact of removing specific subsystems compared to baseline:",
                "",
                "| Experiment | NDCG@10 Delta | MAP Delta |",
                "|---|---|---|",
            ]
        )

        for name, data in self.ablation.items():
            if name == "Baseline":
                lines.append(f"| **{name}** | (Baseline) | (Baseline) |")
            else:
                deltas = data.get("deltas", {})
                ndcg_d = deltas.get("ndcg_at_10", 0)
                map_d = deltas.get("mean_average_precision", 0)
                lines.append(f"| {name} | {ndcg_d:+.4f} | {map_d:+.4f} |")

        lines.extend(
            [
                "",
                "## 4. Error Analysis Summary",
                f"- **Total Highly Relevant Misses:** {self.error_analysis.get('total_misses', 0)}",
                f"- **Retrieval Failures:** {self.error_analysis.get('retrieval_misses', 0)}",
                f"- **Ranking Failures:** {self.error_analysis.get('ranking_misses', 0)}",
                "",
                "> Note: See `error_analysis.json` for full candidate-level breakdown.",
            ]
        )

        report_md = "\n".join(lines)

        if output_path:
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                f.write(report_md)

        return report_md
