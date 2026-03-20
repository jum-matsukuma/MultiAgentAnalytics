"""Base classes for analysis recipes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import polars as pl


@dataclass
class Parameter:
    """Definition of a recipe parameter."""

    name: str
    description: str
    type: str  # "column", "string", "float", "int", "bool"
    required: bool = True
    default: Any = None


@dataclass
class ValidationResult:
    """Result of validating data against a recipe."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = ["## Validation Result"]
        lines.append(f"- **Valid**: {'Yes' if self.valid else 'No'}")
        if self.errors:
            lines.append("\n### Errors")
            for e in self.errors:
                lines.append(f"- {e}")
        if self.warnings:
            lines.append("\n### Warnings")
            for w in self.warnings:
                lines.append(f"- {w}")
        return "\n".join(lines)


@dataclass
class VizSpec:
    """Specification for a suggested visualization."""

    chart_type: str  # "histogram", "scatter", "bar", "heatmap"
    params: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class RecipeResult:
    """Result of running a recipe."""

    recipe_name: str
    sections: dict[str, Any] = field(default_factory=dict)
    visualizations: list[VizSpec] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe": self.recipe_name,
            "sections": self.sections,
        }

    def to_markdown(self) -> str:
        lines: list[str] = []
        for title, content in self.sections.items():
            lines.append(f"## {title}")
            if isinstance(content, str):
                lines.append(content)
            elif isinstance(content, dict):
                for k, v in content.items():
                    lines.append(f"- **{k}**: {v}")
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        row = " | ".join(str(v) for v in item.values())
                        lines.append(f"| {row} |")
                    else:
                        lines.append(f"- {item}")
            lines.append("")
        return "\n".join(lines)

    def to_json(self) -> str:
        import json

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class RecipeBase(ABC):
    """Base class for all analysis recipes."""

    name: str = ""
    description: str = ""
    parameters: list[Parameter] = []

    @abstractmethod
    def validate(self, df: pl.DataFrame, **params: Any) -> ValidationResult:
        """Validate that the data is suitable for this recipe."""

    @abstractmethod
    def run(self, df: pl.DataFrame, **params: Any) -> RecipeResult:
        """Execute the analysis recipe."""

    def suggest_visualizations(self, result: RecipeResult) -> list[VizSpec]:
        """Suggest visualizations for the result. Override in subclasses."""
        return result.visualizations

    def _check_columns_exist(self, df: pl.DataFrame, columns: list[str]) -> list[str]:
        """Helper: check that required columns exist in the DataFrame."""
        missing = [c for c in columns if c not in df.columns]
        return [f"Column '{c}' not found in data" for c in missing]

    def _check_min_rows(self, df: pl.DataFrame, min_rows: int) -> list[str]:
        """Helper: check minimum row count."""
        if df.height < min_rows:
            return [f"Need at least {min_rows} rows, got {df.height}"]
        return []
