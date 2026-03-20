"""Built-in pipeline templates."""

from __future__ import annotations

import json
from typing import Any

_TEMPLATES: dict[str, dict[str, Any]] = {
    "basic-eda": {
        "name": "basic-eda",
        "description": ("Basic EDA: quality check, profile, visualizations"),
        "version": "1.0",
        "output_dir": "output/{{ name }}",
        "parameters": {
            "data_file": {
                "type": "file",
                "description": "Path to the data file to analyze",
                "required": True,
            },
            "target_column": {
                "type": "string",
                "description": "Primary metric column for focused analysis",
                "required": False,
                "default": "",
            },
        },
        "steps": [
            {
                "id": "quality",
                "action": "quality-check",
                "description": "Data quality check",
                "input": "{{ data_file }}",
                "output": "quality_report.md",
            },
            {
                "id": "profile",
                "action": "profile",
                "description": "Full data profile",
                "input": "{{ data_file }}",
                "output": "profile_report.md",
            },
            {
                "id": "correlations",
                "action": "correlations",
                "description": "Correlation analysis",
                "input": "{{ data_file }}",
                "output": "correlations_report.md",
                "depends_on": ["profile"],
            },
            {
                "id": "heatmap",
                "action": "plot heatmap",
                "description": "Correlation heatmap",
                "input": "{{ data_file }}",
                "output": "plot_heatmap.png",
                "depends_on": ["correlations"],
            },
        ],
    },
    "quality-monitor": {
        "name": "quality-monitor",
        "description": "Data quality monitoring pipeline",
        "version": "1.0",
        "output_dir": "output/quality-monitor",
        "parameters": {
            "data_file": {
                "type": "file",
                "description": "Path to the data file to check",
                "required": True,
            },
        },
        "steps": [
            {
                "id": "quality",
                "action": "quality-check",
                "description": "Run quality checks",
                "input": "{{ data_file }}",
                "output": "quality_report.md",
            },
            {
                "id": "summary",
                "action": "summarize",
                "description": "Quick summary",
                "input": "{{ data_file }}",
                "output": "summary.md",
            },
        ],
    },
}


def list_templates() -> list[dict[str, str]]:
    """Return metadata for all available templates."""
    return [
        {"name": t["name"], "description": t["description"]}
        for t in _TEMPLATES.values()
    ]


def get_template(name: str) -> dict[str, Any] | None:
    """Get a template definition by name."""
    return _TEMPLATES.get(name)


def render_template(name: str, output_path: str) -> bool:
    """Write a template to a JSON file.

    Returns True if written, False if template not found.
    """
    template = _TEMPLATES.get(name)
    if template is None:
        return False

    from pathlib import Path

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(template, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return True
