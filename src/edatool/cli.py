"""CLI for edatool - Multi-agent data analysis platform."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from edatool.io.loader import load
from edatool.analysis.stats import summarize
from edatool.analysis.profiler import profile
from edatool.analysis.correlation import correlations
from edatool.analysis.quality import quality_check
from edatool.reporting.markdown import report_to_markdown
from edatool.reporting.json_report import report_to_json

app = typer.Typer(help="edatool - Multi-agent data analysis platform")
plot_app = typer.Typer(help="Visualization commands")
app.add_typer(plot_app, name="plot")

_FORMAT_HELP = "Output format: 'markdown' or 'json'."


def _output_result(text: str, output_file: Optional[Path]) -> None:
    """Print text to stdout or save to file."""
    if output_file is not None:
        output_file.write_text(text, encoding="utf-8")
        typer.echo(f"Saved to {output_file}")
    else:
        typer.echo(text)


@app.command(name="summarize")
def summarize_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    format: str = typer.Option("markdown", "--format", help=_FORMAT_HELP),
    output: Optional[Path] = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Quick summary of a dataset (schema + basic statistics)."""
    df = load(file)
    result = summarize(df)

    if format == "json":
        import json
        text = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    else:
        text = result.to_markdown()

    _output_result(text, output)


# Rename to avoid shadowing the imported `profile` function
@app.command(name="profile")
def profile_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    format: str = typer.Option("markdown", "--format", help=_FORMAT_HELP),
    output: Optional[Path] = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Full profile report (stats + correlations + quality check)."""
    df = load(file)
    result = profile(df)

    if format == "json":
        text = report_to_json(result)
    else:
        text = report_to_markdown(result)

    _output_result(text, output)


@app.command(name="correlations")
def correlations_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    target: Optional[str] = typer.Option(None, "--target", help="Target column name."),
    threshold: float = typer.Option(0.8, "--threshold", help="Correlation threshold."),
    format: str = typer.Option("markdown", "--format", help=_FORMAT_HELP),
    output: Optional[Path] = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Compute correlation matrix for numeric columns."""
    df = load(file)
    result = correlations(df, target=target, threshold=threshold)

    if format == "json":
        import json
        text = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    else:
        text = result.to_markdown()

    _output_result(text, output)


@app.command(name="quality-check")
def quality_check_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    format: str = typer.Option("markdown", "--format", help=_FORMAT_HELP),
    output: Optional[Path] = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Run data quality checks (missing values, duplicates, cardinality)."""
    df = load(file)
    result = quality_check(df)

    if format == "json":
        import json
        text = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    else:
        text = result.to_markdown()

    _output_result(text, output)


@plot_app.command(name="histogram")
def plot_histogram(
    file: str = typer.Argument(..., help="Path to the data file."),
    column: str = typer.Option(..., "--column", help="Column to plot."),
    output: Optional[str] = typer.Option(None, "-o", help="Output image path."),
    bins: int = typer.Option(30, "--bins", help="Number of histogram bins."),
) -> None:
    """Create a histogram for a column."""
    from edatool.viz.histogram import histogram

    df = load(file)
    path = histogram(df, column=column, output=output, bins=bins)

    if path:
        typer.echo(f"Saved to {path}")
    else:
        typer.echo("No output path specified; figure was not saved.")


@plot_app.command(name="scatter")
def plot_scatter(
    file: str = typer.Argument(..., help="Path to the data file."),
    x: str = typer.Option(..., "--x", help="Column for the x-axis."),
    y: str = typer.Option(..., "--y", help="Column for the y-axis."),
    output: Optional[str] = typer.Option(None, "-o", help="Output image path."),
    color: Optional[str] = typer.Option(None, "--color", help="Column for color grouping."),
) -> None:
    """Create a scatter plot for two columns."""
    from edatool.viz.scatter import scatter

    df = load(file)
    path = scatter(df, x=x, y=y, output=output, color=color)

    if path:
        typer.echo(f"Saved to {path}")
    else:
        typer.echo("No output path specified; figure was not saved.")


@plot_app.command(name="heatmap")
def plot_heatmap(
    file: str = typer.Argument(..., help="Path to the data file."),
    output: Optional[str] = typer.Option(None, "-o", help="Output image path."),
) -> None:
    """Create a correlation heatmap for numeric columns."""
    from edatool.viz.heatmap import heatmap

    df = load(file)
    path = heatmap(df, output=output)

    if path:
        typer.echo(f"Saved to {path}")
    else:
        typer.echo("No output path specified; figure was not saved.")


if __name__ == "__main__":
    app()
