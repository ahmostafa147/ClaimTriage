"""Metrics tracking for extraction and routing performance."""
import time
from collections import defaultdict, deque
from typing import Any
import numpy as np


class MetricsTracker:
    """Track performance metrics for the pipeline."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.extraction_times = deque(maxlen=window_size)
        self.routing_times = deque(maxlen=window_size)
        self.queue_sizes = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.low_confidence_counts = defaultdict(int)

    def record_extraction_time(self, duration_seconds: float) -> None:
        """Record extraction duration."""
        self.extraction_times.append(duration_seconds)

    def record_routing_time(self, duration_seconds: float) -> None:
        """Record routing duration."""
        self.routing_times.append(duration_seconds)

    def update_queue_size(self, route: str, size: int) -> None:
        """Update queue size for a route."""
        self.queue_sizes[route] = size

    def increment_queue_size(self, route: str) -> None:
        """Increment queue size for a route."""
        self.queue_sizes[route] += 1

    def record_error(self, error_type: str) -> None:
        """Record an error."""
        self.error_counts[error_type] += 1

    def record_low_confidence(self, field: str) -> None:
        """Record low confidence field."""
        self.low_confidence_counts[field] += 1

    def get_extraction_stats(self) -> dict[str, float]:
        """Get extraction time statistics."""
        if not self.extraction_times:
            return {"p50": 0.0, "p95": 0.0, "mean": 0.0, "count": 0}

        times = list(self.extraction_times)
        return {
            "p50": float(np.percentile(times, 50)),
            "p95": float(np.percentile(times, 95)),
            "mean": float(np.mean(times)),
            "count": len(times)
        }

    def get_routing_stats(self) -> dict[str, float]:
        """Get routing time statistics."""
        if not self.routing_times:
            return {"p50": 0.0, "p95": 0.0, "mean": 0.0, "count": 0}

        times = list(self.routing_times)
        return {
            "p50": float(np.percentile(times, 50)),
            "p95": float(np.percentile(times, 95)),
            "mean": float(np.mean(times)),
            "count": len(times)
        }

    def get_queue_sizes(self) -> dict[str, int]:
        """Get current queue sizes."""
        return dict(self.queue_sizes)

    def get_error_summary(self) -> dict[str, int]:
        """Get error summary."""
        return dict(self.error_counts)

    def get_low_confidence_summary(self) -> dict[str, int]:
        """Get low confidence field summary."""
        return dict(self.low_confidence_counts)

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
        return {
            "extraction": self.get_extraction_stats(),
            "routing": self.get_routing_stats(),
            "queues": self.get_queue_sizes(),
            "errors": self.get_error_summary(),
            "low_confidence": self.get_low_confidence_summary()
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.extraction_times.clear()
        self.routing_times.clear()
        self.queue_sizes.clear()
        self.error_counts.clear()
        self.low_confidence_counts.clear()


class Timer:
    """Simple context manager for timing operations."""

    def __init__(self):
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start_time

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return self.elapsed if self.elapsed is not None else 0.0
