"""Correlation analysis module for edatool."""

from __future__ import annotations

import math

import polars as pl

from edatool.core.dtypes import is_numeric
from edatool.core.types import CorrelationResult, NullHandlingInfo


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
    total_rows = df.height

    matrix: dict[str, dict[str, float]] = {col: {} for col in numeric_cols}
    high_pairs: list[tuple[str, str, float]] = []

    # Track null info and pairwise row counts per column
    null_info: dict[str, dict[str, int | float | list[int]]] = {}
    for col in numeric_cols:
        nc = df[col].null_count()
        if nc > 0:
            null_info[col] = {
                "null_count": nc,
                "null_percent": nc / total_rows * 100 if total_rows > 0 else 0.0,
                "rows_used": [],
            }

    for i, col_a in enumerate(numeric_cols):
        for j, col_b in enumerate(numeric_cols):
            if i == j:
                r = 1.0
            elif j < i:
                r = matrix[col_b][col_a]
            else:
                pair_df = df.select([col_a, col_b]).drop_nulls()
                pair_len = len(pair_df)

                # Track rows used for columns with nulls
                if col_a in null_info:
                    rows_list = null_info[col_a]["rows_used"]
                    assert isinstance(rows_list, list)
                    rows_list.append(pair_len)
                if col_b in null_info:
                    rows_list = null_info[col_b]["rows_used"]
                    assert isinstance(rows_list, list)
                    rows_list.append(pair_len)

                if pair_len < 2:
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

    # Build null handling info
    null_handling: list[NullHandlingInfo] = []
    for col, info in null_info.items():
        rows_list = info["rows_used"]
        assert isinstance(rows_list, list)
        nc = info["null_count"]
        assert isinstance(nc, int)
        np_ = info["null_percent"]
        assert isinstance(np_, float)
        null_handling.append(
            NullHandlingInfo(
                column=col,
                null_count=nc,
                null_percent=np_,
                rows_used_min=min(rows_list) if rows_list else total_rows,
                rows_used_max=max(rows_list) if rows_list else total_rows,
            )
        )

    return CorrelationResult(
        matrix=matrix,
        high_pairs=high_pairs,
        threshold=threshold,
        null_handling=null_handling,
        total_rows=total_rows,
    )
