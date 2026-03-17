"""Profiler orchestrator for edatool.

Combines stats, correlation, and quality analyses into a single ProfileReport.
"""

from __future__ import annotations

import polars as pl

from edatool.core.config import ProfileConfig
from edatool.core.types import ProfileReport
from edatool.analysis.stats import summarize
from edatool.analysis.correlation import correlations
from edatool.analysis.quality import quality_check


def profile(
    df: pl.DataFrame,
    config: ProfileConfig | None = None,
) -> ProfileReport:
    """Run full profiling on a DataFrame.

    Args:
        df: Input Polars DataFrame.
        config: Optional ProfileConfig controlling which analyses to run and
                their parameters.  Defaults to ProfileConfig() (all analyses
                enabled with default settings).

    Returns:
        ProfileReport combining summary, correlations, and quality results
        according to the supplied configuration.
    """
    if config is None:
        config = ProfileConfig()

    summary = summarize(df, max_sample_values=config.max_sample_values)

    corr_result = None
    if config.correlation:
        corr_result = correlations(df, threshold=config.correlation_threshold)

    quality_result = None
    if config.quality_check:
        quality_result = quality_check(
            df,
            high_cardinality_threshold=config.high_cardinality_threshold,
        )

    return ProfileReport(
        summary=summary,
        correlations=corr_result,
        quality=quality_result,
    )
