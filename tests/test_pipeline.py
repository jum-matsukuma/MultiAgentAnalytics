"""Tests for the pipeline module."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from edatool.pipeline.context import PipelineContext
from edatool.pipeline.executor import execute_pipeline
from edatool.pipeline.models import (
    ParameterDef,
    PipelineDefinition,
    PipelineResult,
    StepDefinition,
    StepResult,
)
from edatool.pipeline.parser import (
    load_pipeline,
    topological_sort,
    validate_pipeline,
)
from edatool.pipeline.templates import get_template, list_templates, render_template

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def basic_pipeline() -> PipelineDefinition:
    return PipelineDefinition(
        name="test-pipeline",
        description="A test pipeline",
        parameters=[
            ParameterDef(name="data_file", type="file", required=True),
            ParameterDef(
                name="target",
                type="string",
                required=False,
                default="value",
            ),
        ],
        steps=[
            StepDefinition(
                id="quality",
                action="quality-check",
                input="{{ data_file }}",
                output="quality.md",
            ),
            StepDefinition(
                id="profile",
                action="profile",
                input="{{ data_file }}",
                output="profile.md",
            ),
            StepDefinition(
                id="heatmap",
                action="plot heatmap",
                input="{{ data_file }}",
                output="heatmap.png",
                depends_on=["profile"],
            ),
        ],
    )


@pytest.fixture()
def pipeline_json(tmp_path: Path, basic_pipeline: PipelineDefinition) -> Path:
    path = tmp_path / "test_pipeline.json"
    path.write_text(
        json.dumps(basic_pipeline.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    import polars as pl

    df = pl.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})
    path = tmp_path / "data.csv"
    df.write_csv(path)
    return path


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestModels:
    def test_pipeline_roundtrip(self, basic_pipeline: PipelineDefinition) -> None:
        d = basic_pipeline.to_dict()
        restored = PipelineDefinition.from_dict(d)
        assert restored.name == "test-pipeline"
        assert len(restored.parameters) == 2
        assert len(restored.steps) == 3

    def test_step_roundtrip(self) -> None:
        step = StepDefinition(
            id="s1",
            action="profile",
            input="{{ file }}",
            output="out.md",
            params={"target": "col"},
            depends_on=["s0"],
        )
        d = step.to_dict()
        restored = StepDefinition.from_dict(d)
        assert restored.id == "s1"
        assert restored.depends_on == ["s0"]
        assert restored.params == {"target": "col"}

    def test_pipeline_to_markdown(self, basic_pipeline: PipelineDefinition) -> None:
        md = basic_pipeline.to_markdown()
        assert "## Pipeline: test-pipeline" in md
        assert "data_file" in md
        assert "quality" in md

    def test_pipeline_result_to_markdown(self) -> None:
        result = PipelineResult(
            pipeline_name="test",
            status="completed",
            step_results=[
                StepResult(step_id="s1", status="completed", duration_seconds=1.5)
            ],
            duration_seconds=2.0,
        )
        md = result.to_markdown()
        assert "completed" in md
        assert "s1" in md


# ---------------------------------------------------------------------------
# Context tests
# ---------------------------------------------------------------------------


class TestContext:
    def test_resolve_parameters(self) -> None:
        ctx = PipelineContext(
            parameters={"data_file": "/data/test.csv", "month": "2026-03"},
            output_dir=Path("/output"),
        )
        assert ctx.resolve("{{ data_file }}") == "/data/test.csv"
        assert ctx.resolve("report_{{ month }}.md") == "report_2026-03.md"

    def test_resolve_derived(self) -> None:
        ctx = PipelineContext(parameters={}, output_dir=Path("/output"))
        ctx.derived["top_col"] = "revenue"
        assert ctx.resolve("{{ top_col }}") == "revenue"

    def test_resolve_output_dir(self) -> None:
        ctx = PipelineContext(parameters={}, output_dir=Path("/my/output"))
        assert ctx.resolve("{{ output_dir }}") == "/my/output"

    def test_resolve_unknown_left_as_is(self) -> None:
        ctx = PipelineContext(parameters={}, output_dir=Path("/out"))
        assert ctx.resolve("{{ unknown }}") == "{{ unknown }}"

    def test_resolve_dict(self) -> None:
        ctx = PipelineContext(
            parameters={"col": "age"},
            output_dir=Path("/out"),
        )
        result = ctx.resolve_dict({"column": "{{ col }}", "bins": "30"})
        assert result == {"column": "age", "bins": "30"}


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------


class TestParser:
    def test_load_pipeline(self, pipeline_json: Path) -> None:
        pipeline = load_pipeline(pipeline_json)
        assert pipeline.name == "test-pipeline"
        assert len(pipeline.steps) == 3

    def test_load_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_pipeline("/nonexistent/pipeline.json")

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_pipeline(bad)

    def test_load_missing_name(self, tmp_path: Path) -> None:
        f = tmp_path / "noname.json"
        f.write_text(json.dumps({"steps": [{"id": "s", "action": "profile"}]}))
        with pytest.raises(ValueError, match="name"):
            load_pipeline(f)

    def test_load_missing_steps(self, tmp_path: Path) -> None:
        f = tmp_path / "nosteps.json"
        f.write_text(json.dumps({"name": "test"}))
        with pytest.raises(ValueError, match="step"):
            load_pipeline(f)

    def test_validate_valid(self, basic_pipeline: PipelineDefinition) -> None:
        errors = validate_pipeline(basic_pipeline, {"data_file": "test.csv"})
        assert errors == []

    def test_validate_missing_required_param(
        self, basic_pipeline: PipelineDefinition
    ) -> None:
        errors = validate_pipeline(basic_pipeline, {})
        assert any("data_file" in e for e in errors)

    def test_validate_duplicate_step_id(self) -> None:
        pipeline = PipelineDefinition(
            name="dup",
            steps=[
                StepDefinition(id="s1", action="profile"),
                StepDefinition(id="s1", action="summarize"),
            ],
        )
        errors = validate_pipeline(pipeline)
        assert any("Duplicate" in e for e in errors)

    def test_validate_unknown_dependency(self) -> None:
        pipeline = PipelineDefinition(
            name="bad-dep",
            steps=[
                StepDefinition(id="s1", action="profile", depends_on=["nonexistent"]),
            ],
        )
        errors = validate_pipeline(pipeline)
        assert any("nonexistent" in e for e in errors)

    def test_validate_circular_dependency(self) -> None:
        pipeline = PipelineDefinition(
            name="cycle",
            steps=[
                StepDefinition(id="a", action="profile", depends_on=["b"]),
                StepDefinition(id="b", action="profile", depends_on=["a"]),
            ],
        )
        errors = validate_pipeline(pipeline)
        assert any("Circular" in e for e in errors)


class TestTopologicalSort:
    def test_basic_sort(self, basic_pipeline: PipelineDefinition) -> None:
        ordered = topological_sort(basic_pipeline.steps)
        ids = [s.id for s in ordered]
        assert ids.index("profile") < ids.index("heatmap")

    def test_no_deps(self) -> None:
        steps = [
            StepDefinition(id="a", action="profile"),
            StepDefinition(id="b", action="summarize"),
        ]
        ordered = topological_sort(steps)
        assert len(ordered) == 2

    def test_from_step(self, basic_pipeline: PipelineDefinition) -> None:
        ordered = topological_sort(basic_pipeline.steps, from_step="heatmap")
        ids = [s.id for s in ordered]
        assert "heatmap" in ids
        # quality is unrelated to heatmap, so it should be excluded
        assert "quality" not in ids
        # profile is not a dependent of heatmap, so it's excluded too
        assert "profile" not in ids

    def test_from_step_invalid(self, basic_pipeline: PipelineDefinition) -> None:
        with pytest.raises(ValueError, match="not found"):
            topological_sort(basic_pipeline.steps, from_step="nonexistent")

    def test_cycle_raises(self) -> None:
        steps = [
            StepDefinition(id="a", action="profile", depends_on=["b"]),
            StepDefinition(id="b", action="profile", depends_on=["a"]),
        ]
        with pytest.raises(ValueError, match="Circular"):
            topological_sort(steps)


# ---------------------------------------------------------------------------
# Template tests
# ---------------------------------------------------------------------------


class TestTemplates:
    def test_list_templates(self) -> None:
        templates = list_templates()
        names = [t["name"] for t in templates]
        assert "basic-eda" in names
        assert "quality-monitor" in names

    def test_get_template(self) -> None:
        t = get_template("basic-eda")
        assert t is not None
        assert t["name"] == "basic-eda"
        assert "steps" in t

    def test_get_template_missing(self) -> None:
        assert get_template("nonexistent") is None

    def test_render_template(self, tmp_path: Path) -> None:
        output = tmp_path / "my_pipeline.json"
        assert render_template("basic-eda", str(output))
        assert output.exists()
        data = json.loads(output.read_text())
        assert data["name"] == "basic-eda"

    def test_render_template_missing(self, tmp_path: Path) -> None:
        assert not render_template("nope", str(tmp_path / "out.json"))


# ---------------------------------------------------------------------------
# Executor tests (mostly dry-run; real execution requires uv)
# ---------------------------------------------------------------------------


class TestExecutor:
    def test_dry_run(
        self, basic_pipeline: PipelineDefinition, sample_csv: Path
    ) -> None:
        result = execute_pipeline(
            basic_pipeline,
            {"data_file": str(sample_csv)},
            dry_run=True,
        )
        assert result.status == "dry-run"
        assert len(result.step_results) == 3
        for sr in result.step_results:
            assert sr.status == "dry-run"
            assert "edatool" in sr.output_path

    def test_dry_run_with_from_step(
        self, basic_pipeline: PipelineDefinition, sample_csv: Path
    ) -> None:
        result = execute_pipeline(
            basic_pipeline,
            {"data_file": str(sample_csv)},
            dry_run=True,
            from_step="heatmap",
        )
        assert result.status == "dry-run"
        step_ids = [sr.step_id for sr in result.step_results]
        assert "heatmap" in step_ids

    def test_validation_failure(self, basic_pipeline: PipelineDefinition) -> None:
        result = execute_pipeline(basic_pipeline, {})
        assert result.status == "failed"
        assert result.step_results[0].step_id == "validation"

    def test_default_params_applied(self) -> None:
        pipeline = PipelineDefinition(
            name="defaults",
            parameters=[
                ParameterDef(name="col", type="string", required=False, default="age"),
            ],
            steps=[
                StepDefinition(
                    id="s1",
                    action="summarize",
                    input="test.csv",
                    output="out.md",
                ),
            ],
        )
        result = execute_pipeline(pipeline, {}, dry_run=True)
        assert result.status == "dry-run"

    @pytest.mark.skipif(
        not shutil.which("uv"),
        reason="uv not available",
    )
    def test_real_execution(
        self, basic_pipeline: PipelineDefinition, sample_csv: Path, tmp_path: Path
    ) -> None:
        """Integration test: actual execution via subprocess (requires uv)."""
        pipeline = PipelineDefinition(
            name="real-test",
            output_dir=str(tmp_path / "output"),
            parameters=[
                ParameterDef(name="data_file", type="file", required=True),
            ],
            steps=[
                StepDefinition(
                    id="summary",
                    action="summarize",
                    input="{{ data_file }}",
                    output="summary.md",
                ),
            ],
        )
        result = execute_pipeline(pipeline, {"data_file": str(sample_csv)})
        assert result.status == "completed"
        assert len(result.step_results) == 1
        assert result.step_results[0].status == "completed"
        # Check output file exists
        output_file = Path(result.step_results[0].output_path)
        assert output_file.exists()
