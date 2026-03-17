"""Correlation heatmap visualization for edatool."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns

from edatool.core.dtypes import is_numeric
from edatool.viz.common import save_figure


def heatmap(
    df: pl.DataFrame,
    output: str | None = None,
) -> str | None:
    """Create correlation heatmap for numeric columns.

    Uses Polars-native correlation (no pandas dependency).

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

    # Compute correlation matrix using Polars native API
    numeric_df = df.select(numeric_cols)
    corr_df = numeric_df.corr()
    corr_array = corr_df.to_numpy()

    n = len(numeric_cols)
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
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()

    return save_figure(fig, output)
