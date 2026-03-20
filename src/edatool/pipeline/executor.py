"""Pipeline execution engine."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from edatool.pipeline.context import PipelineContext
from edatool.pipeline.models import (
    PipelineDefinition,
    PipelineResult,
    StepDefinition,
    StepResult,
)
from edatool.pipeline.parser import topological_sort, validate_pipeline

# Map action names to edatool CLI commands
_ACTION_MAP: dict[str, list[str]] = {
    "summarize": ["summarize"],
    "profile": ["profile"],
    "correlations": ["correlations"],
    "quality-check": ["quality-check"],
    "plot histogram": ["plot", "histogram"],
    "plot scatter": ["plot", "scatter"],
    "plot heatmap": ["plot", "heatmap"],
}


def _build_command(
    step: StepDefinition,
    ctx: PipelineContext,
) -> list[str]:
    """Build the edatool CLI command for a step."""
    action_parts = _ACTION_MAP.get(step.action)
    if action_parts is None:
        raise ValueError(f"Unknown action: '{step.action}'")

    cmd = ["uv", "run", "edatool", *action_parts]

    # Add input file
    input_path = ctx.resolve(step.input) if step.input else ""
    if input_path:
        cmd.append(input_path)

    # Add resolved params
    resolved_params = ctx.resolve_dict(step.params)
    for key, value in resolved_params.items():
        cmd.extend([f"--{key}", value])

    # Add output
    if step.output:
        output_path = str(ctx.output_dir / ctx.resolve(step.output))
        cmd.extend(["-o", output_path])

    return cmd


def _run_step(
    step: StepDefinition,
    ctx: PipelineContext,
    dry_run: bool = False,
) -> StepResult:
    """Execute a single pipeline step."""
    start = time.monotonic()

    try:
        cmd = _build_command(step, ctx)
    except ValueError as e:
        return StepResult(
            step_id=step.id,
            status="failed",
            error=str(e),
            duration_seconds=time.monotonic() - start,
        )

    if dry_run:
        return StepResult(
            step_id=step.id,
            status="dry-run",
            output_path=" ".join(cmd),
            duration_seconds=0.0,
        )

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        elapsed = time.monotonic() - start

        output_file = ""
        if step.output:
            output_file = str(ctx.output_dir / ctx.resolve(step.output))
            ctx.step_outputs[step.id] = Path(output_file)

        if result.returncode != 0:
            return StepResult(
                step_id=step.id,
                status="failed",
                error=result.stderr.strip()[:200],
                duration_seconds=elapsed,
            )

        return StepResult(
            step_id=step.id,
            status="completed",
            output_path=output_file,
            duration_seconds=elapsed,
        )

    except subprocess.TimeoutExpired:
        return StepResult(
            step_id=step.id,
            status="failed",
            error="Step timed out (300s)",
            duration_seconds=300.0,
        )
    except Exception as e:
        return StepResult(
            step_id=step.id,
            status="failed",
            error=str(e)[:200],
            duration_seconds=time.monotonic() - start,
        )


def execute_pipeline(
    pipeline: PipelineDefinition,
    params: dict[str, str],
    *,
    dry_run: bool = False,
    from_step: str | None = None,
) -> PipelineResult:
    """Execute a pipeline with the given parameters.

    Args:
        pipeline: The pipeline definition.
        params: User-provided parameter values.
        dry_run: If True, only show what would be executed.
        from_step: If provided, start execution from this step.

    Returns:
        PipelineResult with status and step results.
    """
    start = time.monotonic()

    # Apply defaults for missing optional params
    full_params = dict(params)
    for p in pipeline.parameters:
        if p.name not in full_params and p.default is not None:
            full_params[p.name] = p.default
    full_params.setdefault("name", pipeline.name)

    # Validate
    errors = validate_pipeline(pipeline, full_params)
    if errors:
        return PipelineResult(
            pipeline_name=pipeline.name,
            status="failed",
            step_results=[
                StepResult(
                    step_id="validation",
                    status="failed",
                    error="; ".join(errors),
                )
            ],
            duration_seconds=time.monotonic() - start,
        )

    # Resolve output directory
    ctx = PipelineContext(
        parameters=full_params,
        output_dir=Path(""),  # temporary
    )
    output_dir_str = ctx.resolve(pipeline.output_dir)
    output_dir = Path(output_dir_str)
    ctx.output_dir = output_dir

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Sort steps
    try:
        ordered_steps = topological_sort(pipeline.steps, from_step=from_step)
    except ValueError as e:
        return PipelineResult(
            pipeline_name=pipeline.name,
            status="failed",
            output_dir=str(output_dir),
            step_results=[
                StepResult(step_id="ordering", status="failed", error=str(e))
            ],
            duration_seconds=time.monotonic() - start,
        )

    # Execute steps
    step_results: list[StepResult] = []
    failed = False

    for step in ordered_steps:
        # Skip if a dependency failed
        if failed:
            step_results.append(StepResult(step_id=step.id, status="skipped"))
            continue

        sr = _run_step(step, ctx, dry_run=dry_run)
        step_results.append(sr)

        if sr.status == "failed":
            failed = True

    # Determine overall status
    statuses = {sr.status for sr in step_results}
    if dry_run:
        overall = "dry-run"
    elif "failed" in statuses:
        overall = (
            "failed" if all(s in ("failed", "skipped") for s in statuses) else "partial"
        )
    else:
        overall = "completed"

    return PipelineResult(
        pipeline_name=pipeline.name,
        status=overall,
        output_dir=str(output_dir),
        step_results=step_results,
        duration_seconds=time.monotonic() - start,
    )
