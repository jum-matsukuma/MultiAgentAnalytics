"""Tests for the catalog module."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import pytest

from edatool.catalog.models import (
    AnalysisRecord,
    ColumnSchema,
    DatasetEntry,
    QualitySnapshot,
    generate_id,
)
from edatool.catalog.store import Catalog

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_catalog(tmp_path: Path) -> Path:
    """Return a temporary catalog directory."""
    return tmp_path / "catalog"


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    """Create a sample CSV file and return its path."""
    df = pl.DataFrame(
        {
            "id": list(range(100)),
            "name": [f"item_{i}" for i in range(100)],
            "value": [float(i * 1.5) for i in range(100)],
            "category": ["A", "B", "C", "D"] * 25,
        }
    )
    path = tmp_path / "sample.csv"
    df.write_csv(path)
    return path


@pytest.fixture()
def sample_csv_v2(tmp_path: Path) -> Path:
    """Create a second version of a CSV file with schema changes."""
    df = pl.DataFrame(
        {
            "id": list(range(150)),
            "name": [f"item_{i}" for i in range(150)],
            "value": [float(i * 2.0) for i in range(150)],
            "category": ["A", "B", "C", "D", "E", "F"] * 25,
            "new_col": [i % 10 for i in range(150)],
        }
    )
    path = tmp_path / "sample_v2.csv"
    df.write_csv(path)
    return path


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestModels:
    def test_column_schema_roundtrip(self) -> None:
        cs = ColumnSchema(name="age", dtype="Int64", null_count=5)
        d = cs.to_dict()
        cs2 = ColumnSchema.from_dict(d)
        assert cs2.name == "age"
        assert cs2.null_count == 5

    def test_quality_snapshot_roundtrip(self) -> None:
        qs = QualitySnapshot(
            overall_score=0.87,
            missing_rate=0.03,
            duplicate_rows=2,
            issues=["col_a: 10 missing"],
        )
        d = qs.to_dict()
        qs2 = QualitySnapshot.from_dict(d)
        assert qs2.overall_score == 0.87
        assert len(qs2.issues) == 1

    def test_analysis_record_roundtrip(self) -> None:
        ar = AnalysisRecord(
            id="analysis_001",
            analysis_type="profile",
            executed_at="2026-03-20T10:00:00",
            report_path="reports/profile.md",
            key_findings=["finding 1"],
        )
        d = ar.to_dict()
        ar2 = AnalysisRecord.from_dict(d)
        assert ar2.id == "analysis_001"
        assert ar2.key_findings == ["finding 1"]

    def test_dataset_entry_roundtrip(self) -> None:
        entry = DatasetEntry(
            id="test_data",
            source="/path/to/test.csv",
            file_hash="sha256:abc123",
            registered_at="2026-03-20T10:00:00",
            rows=100,
            columns=[ColumnSchema(name="x", dtype="Float64", null_count=0)],
            quality=QualitySnapshot(overall_score=0.95),
            analyses=[
                AnalysisRecord(
                    id="a001",
                    analysis_type="profile",
                    executed_at="2026-03-20T10:00:00",
                )
            ],
        )
        d = entry.to_dict()
        entry2 = DatasetEntry.from_dict(d)
        assert entry2.id == "test_data"
        assert entry2.rows == 100
        assert len(entry2.columns) == 1
        assert entry2.quality is not None
        assert len(entry2.analyses) == 1

    def test_dataset_entry_to_markdown(self) -> None:
        entry = DatasetEntry(
            id="test_data",
            source="/path/test.csv",
            registered_at="2026-03-20",
            rows=50,
            columns=[ColumnSchema(name="x", dtype="Float64")],
        )
        md = entry.to_markdown()
        assert "## test_data" in md
        assert "50" in md

    def test_generate_id(self) -> None:
        assert generate_id("data/sales_2025.csv") == "sales_2025"
        assert generate_id("My Data File.parquet") == "my_data_file"
        assert generate_id("test") == "test"


# ---------------------------------------------------------------------------
# Catalog store tests
# ---------------------------------------------------------------------------


class TestCatalog:
    def test_register(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        entry = catalog.register(
            str(sample_csv),
            name="sample",
            description="Test data",
            tags=["test"],
        )
        assert entry.id == "sample"
        assert entry.rows == 100
        assert len(entry.columns) == 4
        assert entry.quality is not None
        assert entry.tags == ["test"]

        # Verify file persisted
        json_path = tmp_catalog / "datasets" / "sample.json"
        assert json_path.exists()
        data = json.loads(json_path.read_text())
        assert data["id"] == "sample"

    def test_register_updates_existing(
        self, tmp_catalog: Path, sample_csv: Path
    ) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="sample", tags=["v1"])
        entry = catalog.register(str(sample_csv), name="sample", tags=["v2"])
        assert entry.tags == ["v2"]
        # Should still be only one entry
        assert len(catalog.list_datasets()) == 1

    def test_list(
        self, tmp_catalog: Path, sample_csv: Path, sample_csv_v2: Path
    ) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="sample_a")
        catalog.register(str(sample_csv_v2), name="sample_b")
        entries = catalog.list_datasets()
        assert len(entries) == 2

    def test_list_with_limit(
        self, tmp_catalog: Path, sample_csv: Path, sample_csv_v2: Path
    ) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="a")
        catalog.register(str(sample_csv_v2), name="b")
        assert len(catalog.list_datasets(limit=1)) == 1

    def test_get(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="sample")
        entry = catalog.get("sample")
        assert entry is not None
        assert entry.id == "sample"

    def test_get_missing(self, tmp_catalog: Path) -> None:
        catalog = Catalog(tmp_catalog)
        assert catalog.get("nonexistent") is None

    def test_search_by_keyword(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(
            str(sample_csv), name="sales_data", description="Monthly sales"
        )
        results = catalog.search("sales")
        assert len(results) == 1
        assert results[0].id == "sales_data"

    def test_search_by_tag(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="tagged", tags=["EC"])
        assert len(catalog.search(tag="EC")) == 1
        assert len(catalog.search(tag="other")) == 0

    def test_search_no_results(self, tmp_catalog: Path) -> None:
        catalog = Catalog(tmp_catalog)
        assert catalog.search("nothing") == []

    def test_compare(
        self, tmp_catalog: Path, sample_csv: Path, sample_csv_v2: Path
    ) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="v1")
        catalog.register(str(sample_csv_v2), name="v2")
        report = catalog.compare("v1", "v2")
        assert "Dataset Comparison" in report
        assert "Added" in report  # new_col was added
        assert "Quality Comparison" in report

    def test_compare_missing(self, tmp_catalog: Path) -> None:
        catalog = Catalog(tmp_catalog)
        report = catalog.compare("a", "b")
        assert "not found" in report

    def test_record_analysis(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="sample")
        record = catalog.record_analysis(
            "sample",
            analysis_type="profile",
            report_path="reports/profile.md",
            key_findings=["Found outliers in value column"],
        )
        assert record is not None
        assert record.id == "analysis_001"
        assert record.analysis_type == "profile"

        # Verify it's persisted
        entry = catalog.get("sample")
        assert entry is not None
        assert len(entry.analyses) == 1
        assert entry.last_analyzed != ""

    def test_record_analysis_missing_dataset(self, tmp_catalog: Path) -> None:
        catalog = Catalog(tmp_catalog)
        assert catalog.record_analysis("nope", analysis_type="profile") is None

    def test_check_freshness_ok(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="sample")
        results = catalog.check_freshness()
        assert len(results) == 1
        assert results[0] == ("sample", "ok")

    def test_check_freshness_changed(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="sample")
        # Modify the file
        sample_csv.write_text("a,b\n1,2\n")
        results = catalog.check_freshness()
        assert results[0] == ("sample", "changed")

    def test_check_freshness_missing(self, tmp_catalog: Path, sample_csv: Path) -> None:
        catalog = Catalog(tmp_catalog)
        catalog.register(str(sample_csv), name="sample")
        sample_csv.unlink()
        results = catalog.check_freshness()
        assert results[0] == ("sample", "missing")

    def test_persistence_across_instances(
        self, tmp_catalog: Path, sample_csv: Path
    ) -> None:
        """Verify catalog data persists when loading from a new instance."""
        catalog1 = Catalog(tmp_catalog)
        catalog1.register(str(sample_csv), name="persist_test")
        catalog1.record_analysis(
            "persist_test",
            analysis_type="quality",
            key_findings=["All good"],
        )

        # New instance should load from disk
        catalog2 = Catalog(tmp_catalog)
        entry = catalog2.get("persist_test")
        assert entry is not None
        assert entry.rows == 100
        assert len(entry.analyses) == 1
        assert entry.analyses[0].key_findings == ["All good"]
