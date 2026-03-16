"""Correlation analysis module for edatool."""

from __future__ import annotations

import math

import polars as pl

from edatool.core.types import CorrelationResult

_NUMERIC_DTYPES = (
    pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64,
)


def _is_numeric(dtype: pl.DataType) -> bool:
    return isinstance(dtype, _NUMERIC_DTYPES)


def correlations(
    df: pl.DataFrame,
    target: str | None = None,
    threshold: float = 0.8,
) -> CorrelationResult:
    """Compute Pearson correlation matrix for numeric columns.

    Args:
        df: Input Polars DataFrame.
        target: Optional target column to sort high pairs by.
        threshold: Absolute correlation threshold for high_pairs.

    Returns:
        CorrelationResult with matrix and high-correlation pairs.
    """
    numeric_cols = [col for col in df.columns if _is_numeric(df[col].dtype)]

    matrix: dict[str, dict[str, float]] = {col: {} for col in numeric_cols}
    high_pairs: list[tuple[str, str, float]] = []

    for i, col_a in enumerate(numeric_cols):
        for j, col_b in enumerate(numeric_cols):
            if i == j:
                r = 1.0
            elif j < i:
                r = matrix[col_b][col_a]
            else:
                pair_df = df.select([col_a, col_b]).drop_nulls()
                if len(pair_df) < 2:
                    r = float("nan")
                else:
                    result = pair_df.select(
                        pl.corr(col_a, col_b, method="pearson")
                    )
                    r = result.item()
                    if r is None:
                        r = float("nan")

            matrix[col_a][col_b] = round(r, 6)

        for j in range(i + 1, len(numeric_cols)):
            col_b = numeric_cols[j]
            r = matrix[col_a][col_b]
            if not math.isnan(r) and abs(r) > threshold:
                high_pairs.append((col_a, col_b, r))

    if target is not None and target in numeric_cols:
        high_pairs.sort(key=lambda t: -abs(t[2]))
    else:
        high_pairs.sort(key=lambda t: -abs(t[2]))

    return CorrelationResult(matrix=matrix, high_pairs=high_pairs)
