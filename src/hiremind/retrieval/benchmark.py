"""Retrieval Benchmark — performance benchmarks tracking latency and throughput."""

import gc
import os
import time
from typing import Any

import numpy as np

from hiremind.domain.jd import JobDescription
from hiremind.domain.requirement import ExperienceRequirement, ParsedRequirements
from hiremind.retrieval.retrieval_service import RetrievalService


class RetrievalBenchmarkSuite:
    """Tracks latency, throughput, memory usage, and build statistics for retrieval."""

    def __init__(self, service: RetrievalService) -> None:
        self.service = service

    def run_benchmark(self, iterations: int = 50) -> dict[str, Any]:
        """Run multiple query executions and measure throughput / latency stats."""
        # Clean collection beforehand
        gc.collect()

        jd = JobDescription(
            raw_text="Required Python machine learning engineer",
            cleaned_text="Required Python machine learning engineer",
        )
        reqs = ParsedRequirements(experience=ExperienceRequirement(min_years=2))

        latencies = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.service.retrieve_candidates(jd, reqs, k=100)
            elapsed = time.perf_counter() - start
            latencies.append(elapsed * 1000.0)  # ms

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)

        # Throughput = queries per second
        throughput = 1000.0 / avg_latency if avg_latency > 0 else 0.0

        # Memory usage via process lookup
        mem_mb = 0.0
        try:
            import psutil

            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / (1024 * 1024)
        except ImportError:
            pass

        return {
            "average_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "p99_latency_ms": round(p99_latency, 2),
            "throughput_qps": round(throughput, 2),
            "memory_usage_mb": round(mem_mb, 2),
        }
