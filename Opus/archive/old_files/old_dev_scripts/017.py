"""
import logging
import time
from typing import Dict, List

logger = logging.getLogger(__name__)

# ============================================================================
# MODULE 17: PERFORMANCE PROFILER
# (Extracted from 010.py)
# ============================================================================
class PerformanceProfiler:
    """Tracks generation performance."""
    def __init__(self):
        self.timings = {} # operation: [times]
        self.memory_usage = []

    def start_timer(self, operation: str):
        """Start a timer for a specific operation."""
        self.timings.setdefault(operation, []).append(time.perf_counter())

    def end_timer(self, operation: str):
        """End the timer for a specific operation and record duration."""
        if operation in self.timings and self.timings[operation]:
            start = self.timings[operation].pop()
            duration = time.perf_counter() - start
            # Store completed durations in a separate list
            self.timings.setdefault(f"{operation}_history", []).append(duration)

    def record_memory(self, usage_mb: float):
        """Record a memory usage snapshot."""
        self.memory_usage.append(usage_mb)

    def get_performance_stats(self) -> Dict:
        """Get summarized performance statistics."""
        stats = {}
        for op, data in self.timings.items():
            if op.endswith("_history"):
                op_name = op.replace("_history", "")
                stats[op_name] = {
                    'avg_time': sum(data) / len(data) if data else 0,
                    'total_time': sum(data),
                    'calls': len(data)
                }
        if self.memory_usage:
            stats['avg_memory_mb'] = sum(self.memory_usage) / len(self.memory_usage)
            stats['max_memory_mb'] = max(self.memory_usage)
        return stats

# Global instance
profiler = PerformanceProfiler()