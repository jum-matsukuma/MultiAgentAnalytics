"""Pipeline definition parser and validator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from edatool.pipeline.models import PipelineDefinition


def load_pipeline(source: str | Path) -> PipelineDefinition:
    """Load a pipeline definition from a JSON file.

    Args:
        source: Path to a JSON pipeline definition file.

    Returns:
        Parsed PipelineDefinition.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not valid JSON or missing required fields.
    """
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Pipeline file not found: {source}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in pipeline file: {e}") from e

    if "name" not in data:
        raise ValueError("Pipeline definition must have a 'name' field")
    if "steps" not in data or not data["steps"]:
        raise ValueError("Pipeline definition must have at least one step")

    return PipelineDefinition.from_dict(data)


def validate_pipeline(
    pipeline: PipelineDefinition,
    params: dict[str, str] | None = None,
) -> list[str]:
    """Validate a pipeline definition and return a list of errors.

    Checks:
    - All steps have unique IDs
    - depends_on references valid step IDs
    - No circular dependencies
    - Required parameters are provided (if params given)

    Returns:
        List of error messages. Empty means valid.
    """
    errors: list[str] = []

    # Check unique step IDs
    step_ids = [s.id for s in pipeline.steps]
    seen: set[str] = set()
    for sid in step_ids:
        if sid in seen:
            errors.append(f"Duplicate step ID: '{sid}'")
        seen.add(sid)

    # Check depends_on references
    step_id_set = set(step_ids)
    for step in pipeline.steps:
        for dep in step.depends_on:
            if dep not in step_id_set:
                errors.append(f"Step '{step.id}' depends on unknown step '{dep}'")

    # Check circular dependencies
    cycle = _detect_cycle(pipeline.steps)
    if cycle:
        errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")

    # Check required parameters
    if params is not None:
        for p in pipeline.parameters:
            if p.required and p.name not in params and p.default is None:
                errors.append(f"Required parameter '{p.name}' not provided")

    return errors


def topological_sort(steps: list[Any], from_step: str | None = None) -> list[Any]:
    """Sort steps by dependency order (topological sort).

    Args:
        steps: List of StepDefinition objects.
        from_step: If provided, only include this step and its dependents.

    Returns:
        Steps sorted so dependencies come before dependents.

    Raises:
        ValueError: If a cycle is detected.
    """
    step_map = {s.id: s for s in steps}
    in_degree: dict[str, int] = {s.id: 0 for s in steps}
    dependents: dict[str, list[str]] = {s.id: [] for s in steps}

    for s in steps:
        for dep in s.depends_on:
            if dep in step_map:
                in_degree[s.id] += 1
                dependents[dep].append(s.id)

    queue = [sid for sid, deg in in_degree.items() if deg == 0]
    result: list[Any] = []

    while queue:
        queue.sort()  # deterministic order
        sid = queue.pop(0)
        result.append(step_map[sid])
        for dep_id in dependents[sid]:
            in_degree[dep_id] -= 1
            if in_degree[dep_id] == 0:
                queue.append(dep_id)

    if len(result) != len(steps):
        raise ValueError("Circular dependency detected in pipeline steps")

    # Filter from_step if specified
    if from_step is not None:
        if from_step not in step_map:
            raise ValueError(f"Step '{from_step}' not found in pipeline")
        # Include from_step and all steps that come after it in topo order
        idx = next(i for i, s in enumerate(result) if s.id == from_step)
        result = result[idx:]

    return result


def _detect_cycle(steps: list[Any]) -> list[str]:
    """Detect a cycle in step dependencies. Returns cycle path or empty list."""
    step_ids = {s.id for s in steps}
    deps: dict[str, list[str]] = {
        s.id: [d for d in s.depends_on if d in step_ids] for s in steps
    }

    white, gray, black = 0, 1, 2
    color: dict[str, int] = {sid: white for sid in step_ids}
    parent: dict[str, str] = {}

    def dfs(node: str) -> list[str]:
        color[node] = gray
        for neighbor in deps.get(node, []):
            if color[neighbor] == gray:
                # Found cycle, reconstruct path
                cycle = [neighbor, node]
                current = node
                while current != neighbor:
                    current = parent.get(current, "")
                    if current:
                        cycle.append(current)
                    else:
                        break
                cycle.reverse()
                return cycle
            if color[neighbor] == white:
                parent[neighbor] = node
                result = dfs(neighbor)
                if result:
                    return result
        color[node] = black
        return []

    for sid in step_ids:
        if color[sid] == white:
            result = dfs(sid)
            if result:
                return result
    return []
