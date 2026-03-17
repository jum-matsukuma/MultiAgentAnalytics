"""Basic statistics module for edatool."""

from __future__ import annotations

from typing import Any

import polars as pl

from edatool.core.dtypes import is_numeric
from edatool.core.types import ColumnStats, DataSummary


def _column_stats(
    df: pl.DataFrame, col_name: str, max_sample_values: int
) -> ColumnStats:
    series = df[col_name]
    dtype = series.dtype
    total = len(series)
    null_count = series.null_count()
    null_percent = (null_count / total * 100) if total > 0 else 0.0
    unique_count = series.n_unique()

    # Sample the first N non-null values
    non_null = series.drop_nulls()
    sample_values: list[Any] = non_null.head(max_sample_values).to_list()

    stats = ColumnStats(
        name=col_name,
        dtype=str(dtype),
        count=total,
        null_count=null_count,
        null_percent=round(null_percent, 4),
        unique_count=unique_count,
        sample_values=sample_values,
    )

    if is_numeric(dtype) and len(non_null) > 0:
        stats.mean = non_null.mean()
        stats.std = non_null.std()
        stats.min = non_null.min()
        stats.max = non_null.max()
        stats.median = non_null.median()
        stats.q25 = non_null.quantile(0.25, interpolation="nearest")
        stats.q75 = non_null.quantile(0.75, interpolation="nearest")

    return stats


def summarize(df: pl.DataFrame, max_sample_values: int = 5) -> DataSummary:
    """Compute lightweight dataset summary.

    Args:
        df: Input Polars DataFrame.
        max_sample_values: Number of non-null sample values to include per column.

    Returns:
        DataSummary with shape, memory estimate, and per-column statistics.
    """
    columns = [
        _column_stats(df, col, max_sample_values) for col in df.columns
    ]
    return DataSummary(
        shape=(df.height, df.width),
        columns=columns,
        memory_bytes=df.estimated_size(),
    )
