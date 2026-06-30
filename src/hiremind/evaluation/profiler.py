"""System Profiler for benchmarking end-to-end performance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hiremind.evaluation.latency import LatencyTracker
from hiremind.evaluation.memory import MemoryTracker


class SystemProfiler:
    """Combines latency and memory tracking to profile system performance."""

    def __init__(self) -> None:
        self.latency = LatencyTracker()
        self.memory = MemoryTracker()
        self.candidate_count: int = 0

    def set_candidate_count(self, count: int) -> None:
        """Set the number of candidates processed for throughput calculations."""
        self.candidate_count = count

    def generate_report(self, output_path: str = "outputs/profiling.json") -> dict[str, Any]:
        """Generate a combined JSON profiling report."""
        self.memory.stop_tracing()

        latencies = self.latency.get_all_latencies_ms()
        memory_stats = self.memory.get_measurements()

        total_latency_ms = self.latency.get_total_latency_ms()
        total_latency_sec = total_latency_ms / 1000.0

        throughput = 0.0
        if total_latency_sec > 0 and self.candidate_count > 0:
            throughput = self.candidate_count / total_latency_sec

        # Extract specific benchmark KPIs if available
        retrieval_latency_ms = latencies.get("retrieval", 0.0)
        ranking_latency_ms = latencies.get("ranking", 0.0)

        peak_mem_mb = 0.0
        if memory_stats:
            peak_mem_mb = max(stat.get("peak_mb", 0.0) for stat in memory_stats.values())

        report = {
            "summary": {
                "total_candidates": self.candidate_count,
                "total_latency_ms": round(total_latency_ms, 2),
                "throughput_candidates_per_sec": round(throughput, 2),
                "peak_memory_mb": round(peak_mem_mb, 2),
                "retrieval_latency_ms": retrieval_latency_ms,
                "ranking_latency_ms": ranking_latency_ms,
            },
            "latencies_ms": latencies,
            "memory_usage": memory_stats,
        }

        if output_path:
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

        return report
