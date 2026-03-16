"""Common types and result containers for edatool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ColumnStats:
    """Statistics for a single column."""

    name: str
    dtype: str
    count: int
    null_count: int
    null_percent: float
    unique_count: int
    sample_values: list[Any] = field(default_factory=list)
    # Numeric stats (None for non-numeric)
    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    median: float | None = None
    q25: float | None = None
    q75: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class DataSummary:
    """Lightweight dataset summary (schema + basic stats)."""

    shape: tuple[int, int]
    columns: list[ColumnStats]
    memory_bytes: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape": self.shape,
            "memory_bytes": self.memory_bytes,
            "columns": [c.to_dict() for c in self.columns],
        }

    def to_markdown(self) -> str:
        lines = [
            f"## Dataset Summary",
            f"- **Shape**: {self.shape[0]:,} rows × {self.shape[1]} columns",
        ]
        if self.memory_bytes:
            mb = self.memory_bytes / (1024 * 1024)
            lines.append(f"- **Memory**: {mb:.1f} MB")
        lines.append("")

        # Column table
        lines.append("### Columns")
        lines.append(
            "| # | Column | Type | Nulls | Null% | Unique | Mean | Std | Min | Max |"
        )
        lines.append(
            "|---|--------|------|------:|------:|-------:|-----:|----:|----:|----:|"
        )
        for i, c in enumerate(self.columns, 1):
            mean = f"{c.mean:.2f}" if c.mean is not None else "-"
            std = f"{c.std:.2f}" if c.std is not None else "-"
            min_v = f"{c.min:.2f}" if c.min is not None else "-"
            max_v = f"{c.max:.2f}" if c.max is not None else "-"
            lines.append(
                f"| {i} | {c.name} | {c.dtype} | {c.null_count:,} "
                f"| {c.null_percent:.1f}% | {c.unique_count:,} "
                f"| {mean} | {std} | {min_v} | {max_v} |"
            )
        return "\n".join(lines)


@dataclass
class CorrelationResult:
    """Correlation analysis result."""

    matrix: dict[str, dict[str, float]]
    high_pairs: list[tuple[str, str, float]]  # |r| > threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "matrix": self.matrix,
            "high_pairs": [
                {"col1": a, "col2": b, "correlation": r}
                for a, b, r in self.high_pairs
            ],
        }

    def to_markdown(self) -> str:
        lines = ["## Correlation Analysis"]
        if self.high_pairs:
            lines.append("")
            lines.append("### High Correlation Pairs (|r| > 0.8)")
            lines.append("| Column 1 | Column 2 | Correlation |")
            lines.append("|----------|----------|------------:|")
            for a, b, r in self.high_pairs:
                lines.append(f"| {a} | {b} | {r:.3f} |")
        else:
            lines.append("\nNo high correlation pairs found (|r| > 0.8).")

        # Matrix
        cols = list(self.matrix.keys())
        if cols:
            lines.append("")
            lines.append("### Correlation Matrix")
            header = "| | " + " | ".join(cols) + " |"
            sep = "|---|" + "|".join(["---:" for _ in cols]) + "|"
            lines.append(header)
            lines.append(sep)
            for col in cols:
                vals = " | ".join(
                    f"{self.matrix[col].get(c, 0):.2f}" for c in cols
                )
                lines.append(f"| {col} | {vals} |")
        return "\n".join(lines)


@dataclass
class QualityIssue:
    """A single data quality issue."""

    category: str  # "missing", "duplicate", "constant", "high_cardinality"
    description: str
    severity: str  # "warning", "error", "info"
    column: str | None = None
    detail: Any = None


@dataclass
class QualityReport:
    """Data quality check result."""

    issues: list[QualityIssue] = field(default_factory=list)
    duplicate_row_count: int = 0
    total_rows: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_rows": self.total_rows,
            "duplicate_rows": self.duplicate_row_count,
            "issue_count": len(self.issues),
            "issues": [
                {
                    "category": i.category,
                    "severity": i.severity,
                    "description": i.description,
                    "column": i.column,
                }
                for i in self.issues
            ],
        }

    def to_markdown(self) -> str:
        lines = [
            "## Data Quality Report",
            f"- **Total rows**: {self.total_rows:,}",
            f"- **Duplicate rows**: {self.duplicate_row_count:,}",
            f"- **Issues found**: {len(self.issues)}",
        ]
        if self.issues:
            lines.append("")
            lines.append("### Issues")
            lines.append("| Severity | Category | Column | Description |")
            lines.append("|----------|----------|--------|-------------|")
            for i in self.issues:
                col = i.column or "-"
                lines.append(
                    f"| {i.severity} | {i.category} | {col} | {i.description} |"
                )
        else:
            lines.append("\nNo quality issues found.")
        return "\n".join(lines)


@dataclass
class ProfileReport:
    """Full profiling report combining all analyses."""

    summary: DataSummary
    correlations: CorrelationResult | None = None
    quality: QualityReport | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"summary": self.summary.to_dict()}
        if self.correlations:
            result["correlations"] = self.correlations.to_dict()
        if self.quality:
            result["quality"] = self.quality.to_dict()
        return result

    def to_markdown(self) -> str:
        sections = [self.summary.to_markdown()]
        if self.correlations:
            sections.append(self.correlations.to_markdown())
        if self.quality:
            sections.append(self.quality.to_markdown())
        return "\n\n---\n\n".join(sections)

    def to_json(self) -> str:
        import json

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
