"""Data models for the pipeline system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParameterDef:
    """Definition of a pipeline parameter."""

    name: str
    type: str = "string"  # "string", "file", "float", "int"
    description: str = ""
    required: bool = True
    default: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        return result

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> ParameterDef:
        return cls(
            name=name,
            type=data.get("type", "string"),
            description=data.get("description", ""),
            required=data.get("required", True),
            default=data.get("default"),
        )


@dataclass
class StepDefinition:
    """Definition of a single pipeline step."""

    id: str
    action: str
    description: str = ""
    input: str = ""
    output: str = ""
    params: dict[str, str] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "action": self.action,
        }
        if self.description:
            result["description"] = self.description
        if self.input:
            result["input"] = self.input
        if self.output:
            result["output"] = self.output
        if self.params:
            result["params"] = self.params
        if self.depends_on:
            result["depends_on"] = self.depends_on
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StepDefinition:
        return cls(
            id=data["id"],
            action=data["action"],
            description=data.get("description", ""),
            input=data.get("input", ""),
            output=data.get("output", ""),
            params=data.get("params", {}),
            depends_on=data.get("depends_on", []),
        )


@dataclass
class PipelineDefinition:
    """Complete pipeline definition."""

    name: str
    description: str = ""
    version: str = "1.0"
    output_dir: str = "output/{{ name }}"
    parameters: list[ParameterDef] = field(default_factory=list)
    steps: list[StepDefinition] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "output_dir": self.output_dir,
            "parameters": {p.name: p.to_dict() for p in self.parameters},
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipelineDefinition:
        params = [
            ParameterDef.from_dict(name, pdata)
            for name, pdata in data.get("parameters", {}).items()
        ]
        steps = [StepDefinition.from_dict(s) for s in data.get("steps", [])]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            output_dir=data.get("output_dir", "output/{{ name }}"),
            parameters=params,
            steps=steps,
        )

    def to_markdown(self) -> str:
        lines = [
            f"## Pipeline: {self.name}",
            f"- **Description**: {self.description or '-'}",
            f"- **Version**: {self.version}",
            f"- **Output dir**: `{self.output_dir}`",
        ]
        if self.parameters:
            lines.append("\n### Parameters")
            lines.append("| Name | Type | Required | Default | Description |")
            lines.append("|------|------|----------|---------|-------------|")
            for p in self.parameters:
                default = p.default if p.default is not None else "-"
                req = "Yes" if p.required else "No"
                lines.append(
                    f"| {p.name} | {p.type} | {req} | {default} " f"| {p.description} |"
                )
        if self.steps:
            lines.append("\n### Steps")
            lines.append("| # | ID | Action | Depends On |")
            lines.append("|---|-----|--------|------------|")
            for i, s in enumerate(self.steps, 1):
                deps = ", ".join(s.depends_on) if s.depends_on else "-"
                lines.append(f"| {i} | {s.id} | {s.action} | {deps} |")
        return "\n".join(lines)


@dataclass
class StepResult:
    """Result of executing a single step."""

    step_id: str
    status: str = "pending"  # "pending", "running", "completed", "failed", "skipped"
    output_path: str = ""
    error: str = ""
    duration_seconds: float = 0.0


@dataclass
class PipelineResult:
    """Result of executing a complete pipeline."""

    pipeline_name: str
    status: str = "pending"  # "completed", "failed", "partial"
    output_dir: str = ""
    step_results: list[StepResult] = field(default_factory=list)
    duration_seconds: float = 0.0

    def to_markdown(self) -> str:
        lines = [
            f"## Pipeline Result: {self.pipeline_name}",
            f"- **Status**: {self.status}",
            f"- **Output dir**: `{self.output_dir}`",
            f"- **Duration**: {self.duration_seconds:.1f}s",
        ]
        if self.step_results:
            lines.append("\n### Steps")
            lines.append("| Step | Status | Duration | Output |")
            lines.append("|------|--------|----------|--------|")
            for sr in self.step_results:
                out = f"`{sr.output_path}`" if sr.output_path else "-"
                err = f" ({sr.error})" if sr.error else ""
                lines.append(
                    f"| {sr.step_id} | {sr.status}{err} "
                    f"| {sr.duration_seconds:.1f}s | {out} |"
                )
        return "\n".join(lines)
