"""Latency timing utilities for benchmarking."""

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager


class LatencyTracker:
    """Tracks latency for multiple named phases during benchmarking."""

    def __init__(self) -> None:
        self.timings: dict[str, float] = {}

    @contextmanager
    def measure(self, phase_name: str) -> Generator[None, None, None]:
        """Context manager to measure execution time of a code block."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.timings[phase_name] = self.timings.get(phase_name, 0.0) + elapsed

    def get_latency_ms(self, phase_name: str) -> float:
        """Get latency in milliseconds for a specific phase."""
        return self.timings.get(phase_name, 0.0) * 1000.0

    def get_all_latencies_ms(self) -> dict[str, float]:
        """Get all latencies in milliseconds."""
        return {k: round(v * 1000.0, 2) for k, v in self.timings.items()}

    def get_total_latency_ms(self) -> float:
        """Get total latency across all tracked phases in milliseconds."""
        return sum(self.timings.values()) * 1000.0
