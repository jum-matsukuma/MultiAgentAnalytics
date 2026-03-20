"""Pipeline execution context for sharing state between steps."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class PipelineContext:
    """Shared context during pipeline execution."""

    def __init__(
        self,
        parameters: dict[str, str],
        output_dir: Path,
    ) -> None:
        self.parameters = parameters
        self.output_dir = output_dir
        self.step_outputs: dict[str, Path] = {}
        self.derived: dict[str, Any] = {}

    def resolve(self, template: str) -> str:
        """Resolve {{ var }} placeholders in a template string."""

        def _replace(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            if key in self.parameters:
                return self.parameters[key]
            if key in self.derived:
                return str(self.derived[key])
            if key == "output_dir":
                return str(self.output_dir)
            return match.group(0)  # leave unresolved

        return re.sub(r"\{\{\s*(\w+)\s*\}\}", _replace, template)

    def resolve_dict(self, params: dict[str, str]) -> dict[str, str]:
        """Resolve all template strings in a dict."""
        return {k: self.resolve(v) for k, v in params.items()}
