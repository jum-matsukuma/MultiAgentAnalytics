"""edatool - Multi-agent data analysis platform for Claude Code."""

from edatool import recipes
from edatool import viz as plot
from edatool.analysis.correlation import correlations
from edatool.analysis.profiler import profile
from edatool.analysis.quality import quality_check
from edatool.analysis.stats import summarize
from edatool.io.loader import load

__all__ = [
    "load",
    "summarize",
    "profile",
    "correlations",
    "quality_check",
    "plot",
    "recipes",
]
