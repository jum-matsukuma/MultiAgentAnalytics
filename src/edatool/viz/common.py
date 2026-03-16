"""Shared visualization utilities for edatool."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt


def save_figure(fig: "plt.Figure", output: str | None) -> str | None:
    """Save a matplotlib figure to file.

    Args:
        fig: Matplotlib figure to save.
        output: File path to save to. If None, figure is not saved.

    Returns:
        The output path if saved, otherwise None.
    """
    if output is None:
        plt.close(fig)
        return None
    fig.savefig(output, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return output


def save_plotly(fig: "go.Figure", output: str | None) -> str | None:  # noqa: F821
    """Save a plotly figure to file (png or html).

    Args:
        fig: Plotly figure to save.
        output: File path. If ends with .html, saves as interactive HTML.
                Otherwise saves as static PNG. If None, figure is not saved.

    Returns:
        The output path if saved, otherwise None.
    """
    if output is None:
        return None

    if output.endswith(".html"):
        fig.write_html(output)
    else:
        fig.write_image(output)

    return output
