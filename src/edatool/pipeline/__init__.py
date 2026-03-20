"""Pipeline system for defining and running analysis workflows."""

from edatool.pipeline.context import PipelineContext
from edatool.pipeline.executor import execute_pipeline
from edatool.pipeline.models import (
    ParameterDef,
    PipelineDefinition,
    PipelineResult,
    StepDefinition,
    StepResult,
)
from edatool.pipeline.parser import load_pipeline, validate_pipeline
from edatool.pipeline.templates import get_template, list_templates

__all__ = [
    "ParameterDef",
    "PipelineContext",
    "PipelineDefinition",
    "PipelineResult",
    "StepDefinition",
    "StepResult",
    "execute_pipeline",
    "get_template",
    "list_templates",
    "load_pipeline",
    "validate_pipeline",
]
