"""JSON report generation for edatool."""

from __future__ import annotations

from edatool.core.types import ProfileReport


def report_to_json(profile: ProfileReport) -> str:
    """Generate JSON report from a ProfileReport.

    Args:
        profile: The profile report to serialize.

    Returns:
        A JSON-formatted string of the full profile report.
    """
    return profile.to_json()
