"""Markdown report generation for edatool."""

from __future__ import annotations

from datetime import datetime

from edatool.core.types import ProfileReport

_ALL_SECTIONS = ["overview", "columns", "correlation", "quality"]


def report_to_markdown(
    profile: ProfileReport,
    sections: list[str] | None = None,
) -> str:
    """Generate a comprehensive Markdown report from a ProfileReport.

    Args:
        profile: The profile report to render.
        sections: Optional list of sections to include. Defaults to all:
                  ["overview", "columns", "correlation", "quality"].

    Returns:
        A Markdown-formatted string containing the requested sections.
    """
    if sections is None:
        sections = list(_ALL_SECTIONS)

    parts: list[str] = []

    # Header with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts.append(f"# EDA Report\n\n_Generated at {timestamp}_")

    summary = profile.summary

    if "overview" in sections:
        rows, cols = summary.shape
        memory_str = ""
        if summary.memory_bytes:
            mb = summary.memory_bytes / (1024 * 1024)
            memory_str = f"\n- **Memory**: {mb:.1f} MB"

        numeric_count = sum(
            1 for c in summary.columns if c.mean is not None
        )
        non_numeric_count = cols - numeric_count

        overview = (
            "## Overview\n\n"
            f"- **Rows**: {rows:,}\n"
            f"- **Columns**: {cols}"
            f"{memory_str}\n"
            f"- **Numeric columns**: {numeric_count}\n"
            f"- **Non-numeric columns**: {non_numeric_count}"
        )
        parts.append(overview)

    if "columns" in sections:
        parts.append(summary.to_markdown())

    if "correlation" in sections and profile.correlations is not None:
        parts.append(profile.correlations.to_markdown())

    if "quality" in sections and profile.quality is not None:
        parts.append(profile.quality.to_markdown())

    return "\n\n---\n\n".join(parts)
