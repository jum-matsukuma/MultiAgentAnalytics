"""Catalog store: persistence, registration, search, and comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl

from edatool.catalog.models import (
    AnalysisRecord,
    ColumnSchema,
    DatasetEntry,
    QualitySnapshot,
    generate_id,
    now_iso,
)


def _file_hash(path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return f"sha256:{h.hexdigest()[:16]}"


def _extract_schema(df: pl.DataFrame) -> list[ColumnSchema]:
    """Extract column schema from a DataFrame."""
    return [
        ColumnSchema(
            name=col,
            dtype=str(df[col].dtype),
            null_count=df[col].null_count(),
        )
        for col in df.columns
    ]


def _extract_quality(df: pl.DataFrame) -> QualitySnapshot:
    """Extract quality snapshot from a DataFrame."""
    total = df.height
    if total == 0:
        return QualitySnapshot()

    total_nulls = sum(df[col].null_count() for col in df.columns)
    total_cells = total * df.width
    missing_rate = total_nulls / total_cells if total_cells > 0 else 0.0
    duplicate_rows = total - df.unique().height

    issues: list[str] = []
    for col in df.columns:
        nc = df[col].null_count()
        if nc > 0:
            pct = nc / total * 100
            issues.append(f"{col}: {nc:,} missing ({pct:.1f}%)")

    # Simple quality score: 1 - (missing_rate + dup_rate) / 2
    dup_rate = duplicate_rows / total if total > 0 else 0.0
    score = max(0.0, 1.0 - (missing_rate + dup_rate) / 2)

    return QualitySnapshot(
        overall_score=score,
        missing_rate=missing_rate,
        duplicate_rows=duplicate_rows,
        issues=issues,
    )


class Catalog:
    """Dataset catalog with JSON-based persistence."""

    def __init__(self, catalog_dir: str | Path = "./catalog") -> None:
        self._dir = Path(catalog_dir)
        self._datasets_dir = self._dir / "datasets"
        self._entries: dict[str, DatasetEntry] = {}
        self._loaded = False

    def _ensure_dirs(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._datasets_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self._datasets_dir.exists():
            return
        for f in sorted(self._datasets_dir.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            entry = DatasetEntry.from_dict(data)
            self._entries[entry.id] = entry

    def _save_entry(self, entry: DatasetEntry) -> None:
        self._ensure_dirs()
        path = self._datasets_dir / f"{entry.id}.json"
        path.write_text(
            json.dumps(entry.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def register(
        self,
        source: str,
        *,
        name: str = "",
        description: str = "",
        tags: list[str] | None = None,
    ) -> DatasetEntry:
        """Register a dataset in the catalog.

        Loads the file to extract schema and quality metrics.
        """
        self._load()

        from edatool.io.loader import load

        source_path = Path(source).resolve()
        df = load(str(source_path))

        dataset_id = generate_id(name or source)

        # If already registered, update
        existing = self._entries.get(dataset_id)
        if existing:
            entry = existing
            entry.source = str(source_path)
            entry.file_hash = _file_hash(source_path)
            entry.rows = df.height
            entry.columns = _extract_schema(df)
            entry.quality = _extract_quality(df)
            if description:
                entry.description = description
            if tags is not None:
                entry.tags = tags
        else:
            entry = DatasetEntry(
                id=dataset_id,
                source=str(source_path),
                file_hash=_file_hash(source_path),
                registered_at=now_iso(),
                description=description,
                tags=tags or [],
                rows=df.height,
                columns=_extract_schema(df),
                quality=_extract_quality(df),
            )

        self._entries[dataset_id] = entry
        self._save_entry(entry)
        return entry

    def list_datasets(
        self, *, sort_by: str = "registered_at", limit: int = 0
    ) -> list[DatasetEntry]:
        """List all registered datasets."""
        self._load()
        entries = list(self._entries.values())

        if sort_by == "last_analyzed":
            entries.sort(key=lambda e: e.last_analyzed or "", reverse=True)
        else:
            entries.sort(key=lambda e: e.registered_at, reverse=True)

        if limit > 0:
            entries = entries[:limit]
        return entries

    def get(self, dataset_id: str) -> DatasetEntry | None:
        """Get a dataset entry by ID."""
        self._load()
        return self._entries.get(dataset_id)

    def search(self, query: str = "", *, tag: str = "") -> list[DatasetEntry]:
        """Search datasets by keyword or tag."""
        self._load()
        results: list[DatasetEntry] = []
        query_lower = query.lower()

        for entry in self._entries.values():
            if tag and tag not in entry.tags:
                continue
            if query_lower:
                searchable = " ".join(
                    [
                        entry.id,
                        entry.description,
                        " ".join(entry.tags),
                    ]
                    + [f for a in entry.analyses for f in a.key_findings]
                ).lower()
                if query_lower not in searchable:
                    continue
            results.append(entry)
        return results

    def compare(self, id_a: str, id_b: str) -> str:
        """Compare two datasets and return a Markdown report."""
        self._load()
        a = self._entries.get(id_a)
        b = self._entries.get(id_b)
        if not a or not b:
            missing = id_a if not a else id_b
            return f"Dataset '{missing}' not found in catalog."

        lines = [f"## Dataset Comparison: {id_a} vs {id_b}"]

        # Schema diff
        cols_a = {c.name: c for c in a.columns}
        cols_b = {c.name: c for c in b.columns}
        all_cols = sorted(set(cols_a) | set(cols_b))

        schema_rows: list[str] = []
        for col in all_cols:
            ca = cols_a.get(col)
            cb = cols_b.get(col)
            if ca and not cb:
                schema_rows.append(f"| Removed | {col} | Was {ca.dtype} |")
            elif cb and not ca:
                schema_rows.append(f"| Added | {col} | {cb.dtype} |")
            elif ca and cb and ca.dtype != cb.dtype:
                schema_rows.append(
                    f"| Type changed | {col} | {ca.dtype} -> {cb.dtype} |"
                )

        if schema_rows:
            lines.append("")
            lines.append("### Schema Diff")
            lines.append("| Change | Column | Detail |")
            lines.append("|--------|--------|--------|")
            lines.extend(schema_rows)
        else:
            lines.append("\n### Schema Diff\nNo schema differences found.")

        # Quality comparison
        qa = a.quality
        qb = b.quality
        if qa and qb:
            lines.append("")
            lines.append("### Quality Comparison")
            lines.append(f"| Metric | {id_a} | {id_b} | Change |")
            lines.append("|--------|--------|--------|--------|")
            lines.append(
                f"| Rows | {a.rows:,} | {b.rows:,} "
                f"| {_change_pct(a.rows, b.rows)} |"
            )
            lines.append(
                f"| Missing rate | {qa.missing_rate:.1%} "
                f"| {qb.missing_rate:.1%} "
                f"| {_change_pp(qa.missing_rate, qb.missing_rate)} |"
            )
            lines.append(
                f"| Quality score | {qa.overall_score:.2f} "
                f"| {qb.overall_score:.2f} "
                f"| {qb.overall_score - qa.overall_score:+.2f} |"
            )
            lines.append(
                f"| Duplicates | {qa.duplicate_rows:,} "
                f"| {qb.duplicate_rows:,} "
                f"| {qb.duplicate_rows - qa.duplicate_rows:+,} |"
            )

        return "\n".join(lines)

    def record_analysis(
        self,
        dataset_id: str,
        *,
        analysis_type: str,
        report_path: str = "",
        key_findings: list[str] | None = None,
    ) -> AnalysisRecord | None:
        """Record an analysis result for a dataset."""
        self._load()
        entry = self._entries.get(dataset_id)
        if entry is None:
            return None

        # Generate analysis ID
        count = len(entry.analyses) + 1
        analysis_id = f"analysis_{count:03d}"

        record = AnalysisRecord(
            id=analysis_id,
            analysis_type=analysis_type,
            executed_at=now_iso(),
            report_path=report_path,
            key_findings=key_findings or [],
        )
        entry.analyses.append(record)
        entry.last_analyzed = record.executed_at
        self._save_entry(entry)
        return record

    def check_freshness(self) -> list[tuple[str, str]]:
        """Check if registered files have changed since registration.

        Returns list of (dataset_id, status) where status is
        'changed', 'missing', or 'ok'.
        """
        self._load()
        results: list[tuple[str, str]] = []
        for entry in self._entries.values():
            source = Path(entry.source)
            if not source.exists():
                results.append((entry.id, "missing"))
            else:
                current_hash = _file_hash(source)
                if current_hash != entry.file_hash:
                    results.append((entry.id, "changed"))
                else:
                    results.append((entry.id, "ok"))
        return results


def _change_pct(old: int | float, new: int | float) -> str:
    if old == 0:
        return "N/A"
    pct = (new - old) / old * 100
    return f"{pct:+.1f}%"


def _change_pp(old: float, new: float) -> str:
    diff = (new - old) * 100
    return f"{diff:+.1f}pp"
