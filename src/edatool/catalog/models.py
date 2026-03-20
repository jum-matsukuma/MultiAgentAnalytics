"""Data models for the catalog system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ColumnSchema:
    """Schema information for a single column."""

    name: str
    dtype: str
    null_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "dtype": self.dtype, "null_count": self.null_count}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ColumnSchema:
        return cls(
            name=data["name"],
            dtype=data["dtype"],
            null_count=data.get("null_count", 0),
        )


@dataclass
class QualitySnapshot:
    """Quality metrics snapshot at a point in time."""

    overall_score: float = 0.0
    missing_rate: float = 0.0
    duplicate_rows: int = 0
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 4),
            "missing_rate": round(self.missing_rate, 4),
            "duplicate_rows": self.duplicate_rows,
            "issues": self.issues,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualitySnapshot:
        return cls(
            overall_score=data.get("overall_score", 0.0),
            missing_rate=data.get("missing_rate", 0.0),
            duplicate_rows=data.get("duplicate_rows", 0),
            issues=data.get("issues", []),
        )


@dataclass
class AnalysisRecord:
    """Record of a single analysis execution."""

    id: str
    analysis_type: str
    executed_at: str  # ISO format
    report_path: str = ""
    key_findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.analysis_type,
            "executed_at": self.executed_at,
        }
        if self.report_path:
            result["report_path"] = self.report_path
        if self.key_findings:
            result["key_findings"] = self.key_findings
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalysisRecord:
        return cls(
            id=data["id"],
            analysis_type=data["type"],
            executed_at=data["executed_at"],
            report_path=data.get("report_path", ""),
            key_findings=data.get("key_findings", []),
        )


@dataclass
class DatasetEntry:
    """Catalog entry for a registered dataset."""

    id: str
    source: str
    file_hash: str = ""
    registered_at: str = ""
    last_analyzed: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    rows: int = 0
    columns: list[ColumnSchema] = field(default_factory=list)
    quality: QualitySnapshot | None = None
    analyses: list[AnalysisRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "source": self.source,
            "file_hash": self.file_hash,
            "registered_at": self.registered_at,
            "last_analyzed": self.last_analyzed,
            "description": self.description,
            "tags": self.tags,
            "schema": {
                "rows": self.rows,
                "columns": [c.to_dict() for c in self.columns],
            },
        }
        if self.quality:
            result["quality"] = self.quality.to_dict()
        if self.analyses:
            result["analyses"] = [a.to_dict() for a in self.analyses]
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DatasetEntry:
        schema = data.get("schema", {})
        quality_data = data.get("quality")
        return cls(
            id=data["id"],
            source=data["source"],
            file_hash=data.get("file_hash", ""),
            registered_at=data.get("registered_at", ""),
            last_analyzed=data.get("last_analyzed", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            rows=schema.get("rows", 0),
            columns=[ColumnSchema.from_dict(c) for c in schema.get("columns", [])],
            quality=(QualitySnapshot.from_dict(quality_data) if quality_data else None),
            analyses=[AnalysisRecord.from_dict(a) for a in data.get("analyses", [])],
        )

    def to_markdown(self) -> str:
        lines = [
            f"## {self.id}",
            f"- **Source**: `{self.source}`",
            f"- **Registered**: {self.registered_at}",
            f"- **Last analyzed**: {self.last_analyzed or 'Never'}",
            f"- **Description**: {self.description or '-'}",
            f"- **Tags**: {', '.join(self.tags) if self.tags else '-'}",
            f"- **Rows**: {self.rows:,}",
            f"- **Columns**: {len(self.columns)}",
        ]
        if self.quality:
            lines.append("")
            lines.append("### Quality")
            lines.append(f"- **Score**: {self.quality.overall_score:.2f}")
            lines.append(f"- **Missing rate**: {self.quality.missing_rate:.1%}")
            lines.append(f"- **Duplicate rows**: {self.quality.duplicate_rows:,}")
            if self.quality.issues:
                for issue in self.quality.issues:
                    lines.append(f"  - {issue}")

        if self.columns:
            lines.append("")
            lines.append("### Schema")
            lines.append("| # | Column | Type | Nulls |")
            lines.append("|---|--------|------|------:|")
            for i, c in enumerate(self.columns, 1):
                lines.append(f"| {i} | {c.name} | {c.dtype} | {c.null_count:,} |")

        if self.analyses:
            lines.append("")
            lines.append("### Analysis History")
            lines.append("| ID | Type | Date | Findings |")
            lines.append("|----|------|------|----------|")
            for a in self.analyses:
                findings = "; ".join(a.key_findings[:3]) if a.key_findings else "-"
                lines.append(
                    f"| {a.id} | {a.analysis_type} | {a.executed_at} " f"| {findings} |"
                )

        return "\n".join(lines)


def generate_id(name: str) -> str:
    """Generate a dataset ID from a name or file path."""
    import re

    # Strip path and extension, keep alphanumeric + underscores
    base = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", base)
    clean = re.sub(r"_+", "_", clean).strip("_").lower()
    return clean or "dataset"


def now_iso() -> str:
    """Return current time as ISO 8601 string."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
