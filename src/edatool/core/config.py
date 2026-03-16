"""Configuration for edatool."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProfileConfig:
    """Configuration for profiling."""

    stats: bool = True
    correlation: bool = True
    quality_check: bool = True
    correlation_threshold: float = 0.8
    max_sample_values: int = 5
    high_cardinality_threshold: float = 0.95
