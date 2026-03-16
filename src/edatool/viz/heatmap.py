"""Correlation heatmap visualization for edatool."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns

from edatool.viz.common import save_figure

# Polars numeric types
_NUMERIC_DTYPES = (
    pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64,
)


def _is_numeric(dtype: pl.DataType) -> bool:
    return isinstance(dtype, _NUMERIC_DTYPES)


def heatmap(
    df: pl.DataFrame,
    output: str | None = None,
) -> str | None:
    """Create correlation heatmap for numeric columns.

    Computes Pearson correlation matrix from numeric columns and renders
    it as an annotated seaborn heatmap.

    Args:
        df: Input Polars DataFrame.
        output: File path to save the figure. If None, figure is not saved.

    Returns:
        The output path if saved, otherwise None.
    """
    numeric_cols = [col for col in df.columns if _is_numeric(df[col].dtype)]

    if len(numeric_cols) < 2:
        raise ValueError(
            "At least 2 numeric columns are required to create a correlation heatmap."
        )

    # Use pandas for correlation matrix computation (seaborn integrates well)
    pandas_df = df.select(numeric_cols).to_pandas()
    corr_matrix = pandas_df.corr()

    n = len(numeric_cols)
    fig_size = max(6, n)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size - 1))

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        ax=ax,
        square=True,
        linewidths=0.5,
    )
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()

    return save_figure(fig, output)
