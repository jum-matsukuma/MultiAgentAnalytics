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

    def __post_init__(self) -> None:
        if not (0.0 < self.correlation_threshold <= 1.0):
            raise ValueError("correlation_threshold must be in (0, 1]")
        if not (0.0 < self.high_cardinality_threshold <= 1.0):
            raise ValueError("high_cardinality_threshold must be in (0, 1]")
