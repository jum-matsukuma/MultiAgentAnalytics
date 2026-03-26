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

    _OPTIONAL_FIELDS = {"mean", "std", "min", "max", "median", "q25", "q75"}

    def to_dict(self) -> dict[str, Any]:
        return {
            k: v
            for k, v in self.__dict__.items()
            if not (v is None and k in self._OPTIONAL_FIELDS)
        }


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
            "## Dataset Summary",
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
class NullHandlingInfo:
    """Information about how null values were handled in correlation."""

    column: str
    null_count: int
    null_percent: float
    rows_used_min: int  # minimum rows used across pairwise comparisons
    rows_used_max: int  # maximum rows used across pairwise comparisons


@dataclass
class CorrelationResult:
    """Correlation analysis result."""

    matrix: dict[str, dict[str, float]]
    high_pairs: list[tuple[str, str, float]]  # |r| > threshold
    threshold: float = 0.8
    null_handling: list[NullHandlingInfo] = field(default_factory=list)
    total_rows: int = 0

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "matrix": self.matrix,
            "high_pairs": [
                {"col1": a, "col2": b, "correlation": r}
                for a, b, r in self.high_pairs
            ],
        }
        if self.null_handling:
            result["null_handling"] = {
                "method": "pairwise_complete_observations",
                "total_rows": self.total_rows,
                "columns_with_nulls": [
                    {
                        "column": nh.column,
                        "null_count": nh.null_count,
                        "null_percent": nh.null_percent,
                        "rows_used_range": [nh.rows_used_min, nh.rows_used_max],
                    }
                    for nh in self.null_handling
                ],
            }
        return result

    def to_markdown(self) -> str:
        lines = ["## Correlation Analysis"]

        # Null handling section
        if self.null_handling:
            lines.append("")
            lines.append("### Missing Value Handling")
            lines.append("")
            lines.append(
                "Correlations computed using **pairwise complete observations**: "
                "for each pair of columns, rows with nulls in either column are "
                "excluded before computing the Pearson coefficient."
            )
            lines.append("")
            lines.append(
                "| Column | Nulls | Null% | Rows Used (min-max) |"
            )
            lines.append(
                "|--------|------:|------:|--------------------:|"
            )
            for nh in self.null_handling:
                if nh.rows_used_min == nh.rows_used_max:
                    rows_str = f"{nh.rows_used_min:,}"
                else:
                    rows_str = f"{nh.rows_used_min:,}-{nh.rows_used_max:,}"
                lines.append(
                    f"| {nh.column} | {nh.null_count:,} "
                    f"| {nh.null_percent:.1f}% | {rows_str} |"
                )

        if self.high_pairs:
            lines.append("")
            lines.append(f"### High Correlation Pairs (|r| > {self.threshold})")
            lines.append("| Column 1 | Column 2 | Correlation |")
            lines.append("|----------|----------|------------:|")
            for a, b, r in self.high_pairs:
                lines.append(f"| {a} | {b} | {r:.3f} |")
        else:
            lines.append(f"\nNo high correlation pairs found (|r| > {self.threshold}).")

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
