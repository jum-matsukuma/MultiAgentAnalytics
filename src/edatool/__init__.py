"""edatool - Multi-agent data analysis platform for Claude Code."""

from edatool.io.loader import load
from edatool.analysis.stats import summarize
from edatool.analysis.profiler import profile
from edatool.analysis.correlation import correlations
from edatool.analysis.quality import quality_check
from edatool import viz as plot

__all__ = [
    "load",
    "summarize",
    "profile",
    "correlations",
    "quality_check",
    "plot",
]
