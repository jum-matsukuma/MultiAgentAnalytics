"""Scatter plot visualization for edatool."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import polars as pl

from edatool.viz.common import save_figure


def scatter(
    df: pl.DataFrame,
    x: str,
    y: str,
    output: str | None = None,
    color: str | None = None,
) -> str | None:
    """Create scatter plot.

    Args:
        df: Input Polars DataFrame.
        x: Column name for the x-axis.
        y: Column name for the y-axis.
        output: File path to save the figure. If None, figure is not saved.
        color: Optional column name to use for grouping/coloring points.

    Returns:
        The output path if saved, otherwise None.
    """
    for col in [x, y]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
    if color is not None and color not in df.columns:
        raise ValueError(f"Color column '{color}' not found in DataFrame.")

    fig, ax = plt.subplots(figsize=(8, 6))

    if color is not None:
        groups = df[color].unique().to_list()
        cmap = plt.cm.get_cmap("tab10", len(groups))
        for idx, group in enumerate(groups):
            subset = df.filter(pl.col(color) == group)
            ax.scatter(
                subset[x].to_list(),
                subset[y].to_list(),
                label=str(group),
                color=cmap(idx),
                alpha=0.7,
                s=20,
            )
        ax.legend(title=color, bbox_to_anchor=(1.05, 1), loc="upper left")
    else:
        ax.scatter(
            df[x].to_list(),
            df[y].to_list(),
            alpha=0.7,
            s=20,
        )

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"{x} vs {y}")

    fig.tight_layout()
    return save_figure(fig, output)
