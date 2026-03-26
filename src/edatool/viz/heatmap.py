"""Correlation heatmap visualization for edatool."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns

from edatool.core.dtypes import is_numeric
from edatool.viz.common import save_figure


def heatmap(
    df: pl.DataFrame,
    output: str | None = None,
) -> str | None:
    """Create correlation heatmap for numeric columns.

    Uses pairwise complete observations to handle missing values:
    for each pair of columns, rows where either value is null are
    dropped before computing Pearson correlation.

    Args:
        df: Input Polars DataFrame.
        output: File path to save the figure. If None, figure is not saved.

    Returns:
        The output path if saved, otherwise None.
    """
    numeric_cols = [col for col in df.columns if is_numeric(df[col].dtype)]

    if len(numeric_cols) < 2:
        raise ValueError(
            "At least 2 numeric columns are required to create a correlation heatmap."
        )

    # Compute correlation matrix using pairwise complete observations
    n = len(numeric_cols)
    corr_array = np.ones((n, n))
    null_cols: list[str] = []

    for i in range(n):
        col_i_nulls = df[numeric_cols[i]].null_count()
        if col_i_nulls > 0:
            null_cols.append(numeric_cols[i])
        for j in range(i + 1, n):
            pair_df = df.select([numeric_cols[i], numeric_cols[j]]).drop_nulls()
            if len(pair_df) < 2:
                r = float("nan")
            else:
                try:
                    result = pair_df.select(
                        pl.corr(numeric_cols[i], numeric_cols[j], method="pearson")
                    )
                    r = result.item()
                    if r is None:
                        r = float("nan")
                except Exception:
                    r = float("nan")
            corr_array[i, j] = r
            corr_array[j, i] = r

    # De-duplicate null_cols list while preserving order
    seen: set[str] = set()
    unique_null_cols: list[str] = []
    for c in null_cols:
        if c not in seen:
            seen.add(c)
            unique_null_cols.append(c)

    fig_size = max(6, n)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size - 1))

    sns.heatmap(
        corr_array,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        ax=ax,
        square=True,
        linewidths=0.5,
        xticklabels=numeric_cols,
        yticklabels=numeric_cols,
    )

    title = "Correlation Heatmap"
    if unique_null_cols:
        title += " (pairwise complete obs.)"
    ax.set_title(title)

    # Add footnote about null handling
    if unique_null_cols:
        note = f"* Nulls dropped pairwise: {', '.join(unique_null_cols)}"
        fig.text(
            0.02, 0.01, note, fontsize=8, color="#666666", style="italic",
        )

    fig.tight_layout(rect=[0, 0.03, 1, 1] if unique_null_cols else None)

    return save_figure(fig, output)
