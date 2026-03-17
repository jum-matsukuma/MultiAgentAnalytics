"""Histogram visualization for edatool."""

from __future__ import annotations

import matplotlib.pyplot as plt
import polars as pl

from edatool.core.dtypes import is_numeric
from edatool.viz.common import save_figure


def histogram(
    df: pl.DataFrame,
    column: str,
    output: str | None = None,
    bins: int = 30,
) -> str | None:
    """Create histogram for a column.

    For numeric columns, creates a histogram with the specified number of bins.
    For categorical/string columns, creates a bar chart of value counts (top 20).

    Args:
        df: Input Polars DataFrame.
        column: Column name to plot.
        output: File path to save the figure. If None, figure is not saved.
        bins: Number of bins for numeric histograms. Defaults to 30.

    Returns:
        The output path if saved, otherwise None.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    series = df[column].drop_nulls()
    fig, ax = plt.subplots(figsize=(8, 5))

    if is_numeric(df[column].dtype):
        values = series.to_list()
        ax.hist(values, bins=bins, edgecolor="white", linewidth=0.5)
        ax.set_xlabel(column)
        ax.set_ylabel("Count")
        ax.set_title(f"Histogram of {column}")
    else:
        # Bar chart of value counts (top 20)
        counts = (
            df[column]
            .value_counts()
            .sort("count", descending=True)
            .head(20)
        )
        labels = counts[column].cast(pl.Utf8).to_list()
        values_counts = counts["count"].to_list()

        ax.barh(range(len(labels)), values_counts)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel("Count")
        ax.set_title(f"Value Counts of {column} (top {len(labels)})")

    fig.tight_layout()
    return save_figure(fig, output)
