"""Correlation analysis module for edatool."""

from __future__ import annotations

import math

import polars as pl

from edatool.core.dtypes import is_numeric
from edatool.core.types import CorrelationResult


def correlations(
    df: pl.DataFrame,
    target: str | None = None,
    threshold: float = 0.8,
) -> CorrelationResult:
    """Compute Pearson correlation matrix for numeric columns.

    Args:
        df: Input Polars DataFrame.
        target: Optional target column. When set, high_pairs only includes
                pairs involving the target, sorted by absolute correlation.
        threshold: Absolute correlation threshold for high_pairs.

    Returns:
        CorrelationResult with matrix and high-correlation pairs.
    """
    numeric_cols = [col for col in df.columns if is_numeric(df[col].dtype)]

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
                    try:
                        result = pair_df.select(
                            pl.corr(col_a, col_b, method="pearson")
                        )
                        r = result.item()
                        if r is None:
                            r = float("nan")
                    except Exception:
                        r = float("nan")

            matrix[col_a][col_b] = round(r, 6)

    # Collect high-correlation pairs from upper triangle
    for i, col_a in enumerate(numeric_cols):
        for j in range(i + 1, len(numeric_cols)):
            col_b = numeric_cols[j]
            r = matrix[col_a][col_b]
            if math.isnan(r) or abs(r) <= threshold:
                continue
            # If target is set, only include pairs involving the target
            if target is not None and target in numeric_cols:
                if col_a != target and col_b != target:
                    continue
            high_pairs.append((col_a, col_b, r))

    high_pairs.sort(key=lambda t: -abs(t[2]))

    return CorrelationResult(
        matrix=matrix, high_pairs=high_pairs, threshold=threshold
    )
