"""Memory profiling utilities for benchmarking."""

from __future__ import annotations

import gc
import tracemalloc
from collections.abc import Generator
from contextlib import contextmanager


class MemoryTracker:
    """Tracks peak memory usage during benchmarking phases using tracemalloc."""

    def __init__(self) -> None:
        self.measurements: dict[str, dict[str, float]] = {}

    @contextmanager
    def measure(self, phase_name: str) -> Generator[None, None, None]:
        """Context manager to measure peak memory usage of a code block."""
        # Force garbage collection before tracking to get a clean baseline
        gc.collect()

        if not tracemalloc.is_tracing():
            tracemalloc.start()

        start_current, start_peak = tracemalloc.get_traced_memory()

        try:
            yield
        finally:
            end_current, end_peak = tracemalloc.get_traced_memory()

            # Record delta in MB
            baseline_mb = start_current / (1024 * 1024)
            peak_mb = end_peak / (1024 * 1024)
            delta_peak_mb = (end_peak - start_current) / (1024 * 1024)

            self.measurements[phase_name] = {
                "baseline_mb": round(baseline_mb, 2),
                "peak_mb": round(peak_mb, 2),
                "delta_peak_mb": round(delta_peak_mb, 2),
            }

    def stop_tracing(self) -> None:
        """Stop tracemalloc if running."""
        if tracemalloc.is_tracing():
            tracemalloc.stop()

    def get_measurements(self) -> dict[str, dict[str, float]]:
        """Get all memory measurements."""
        return self.measurements
