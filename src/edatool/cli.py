"""CLI for edatool - Multi-agent data analysis platform."""

from __future__ import annotations

from pathlib import Path

import click
import typer

from edatool.analysis.correlation import correlations
from edatool.analysis.profiler import profile
from edatool.analysis.quality import quality_check
from edatool.analysis.stats import summarize
from edatool.io.loader import load
from edatool.reporting.markdown import report_to_markdown

app = typer.Typer(help="edatool - Multi-agent data analysis platform")
plot_app = typer.Typer(help="Visualization commands")
app.add_typer(plot_app, name="plot")
recipe_app = typer.Typer(help="Reusable analysis recipes")
app.add_typer(recipe_app, name="recipe")
catalog_app = typer.Typer(help="Data catalog and analysis history")
app.add_typer(catalog_app, name="catalog")

_FORMAT_HELP = "Output format: 'markdown' or 'json'."
_FORMAT_CHOICE = typer.Option(
    "markdown",
    "--format",
    help=_FORMAT_HELP,
    click_type=click.Choice(["markdown", "json"]),
)


def _output_result(text: str, output_file: Path | None) -> None:
    """Print text to stdout or save to file."""
    if output_file is not None:
        output_file.write_text(text, encoding="utf-8")
        typer.echo(f"Saved to {output_file}")
    else:
        typer.echo(text)


def _to_json(obj: object) -> str:
    import json

    return json.dumps(obj.to_dict(), ensure_ascii=False, indent=2)  # type: ignore[union-attr]


@app.command(name="summarize")
def summarize_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    output_format: str = _FORMAT_CHOICE,
    output: Path | None = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Quick summary of a dataset (schema + basic statistics)."""
    df = load(file)
    result = summarize(df)
    text = _to_json(result) if output_format == "json" else result.to_markdown()
    _output_result(text, output)


@app.command(name="profile")
def profile_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    output_format: str = _FORMAT_CHOICE,
    output: Path | None = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Full profile report (stats + correlations + quality check)."""
    df = load(file)
    result = profile(df)
    text = result.to_json() if output_format == "json" else report_to_markdown(result)
    _output_result(text, output)


@app.command(name="correlations")
def correlations_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    target: str | None = typer.Option(None, "--target", help="Target column name."),
    threshold: float = typer.Option(0.8, "--threshold", help="Correlation threshold."),
    output_format: str = _FORMAT_CHOICE,
    output: Path | None = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Compute correlation matrix for numeric columns."""
    df = load(file)
    result = correlations(df, target=target, threshold=threshold)
    text = _to_json(result) if output_format == "json" else result.to_markdown()
    _output_result(text, output)


@app.command(name="quality-check")
def quality_check_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    output_format: str = _FORMAT_CHOICE,
    output: Path | None = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Run data quality checks (missing values, duplicates, cardinality)."""
    df = load(file)
    result = quality_check(df)
    text = _to_json(result) if output_format == "json" else result.to_markdown()
    _output_result(text, output)


@plot_app.command(name="histogram")
def plot_histogram(
    file: str = typer.Argument(..., help="Path to the data file."),
    column: str = typer.Option(..., "--column", help="Column to plot."),
    output: str | None = typer.Option(None, "-o", help="Output image path."),
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
    output: str | None = typer.Option(None, "-o", help="Output image path."),
    color: str | None = typer.Option(
        None, "--color", help="Column for color grouping."
    ),
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
    output: str | None = typer.Option(None, "-o", help="Output image path."),
) -> None:
    """Create a correlation heatmap for numeric columns."""
    from edatool.viz.heatmap import heatmap

    df = load(file)
    path = heatmap(df, output=output)

    if path:
        typer.echo(f"Saved to {path}")
    else:
        typer.echo("No output path specified; figure was not saved.")


@recipe_app.command(name="list")
def recipe_list_cmd() -> None:
    """List all available analysis recipes."""
    from edatool.recipes.registry import list_recipes

    recipes = list_recipes()
    if not recipes:
        typer.echo("No recipes available.")
        return

    typer.echo("## Available Recipes\n")
    typer.echo("| Name | Description |")
    typer.echo("|------|-------------|")
    for r in recipes:
        typer.echo(f"| {r.name} | {r.description} |")


@recipe_app.command(name="info")
def recipe_info_cmd(
    name: str = typer.Argument(..., help="Recipe name."),
) -> None:
    """Show detailed information about a recipe."""
    from edatool.recipes.registry import get_recipe

    recipe = get_recipe(name)
    if recipe is None:
        typer.echo(f"Recipe '{name}' not found.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"## {recipe.name}\n")
    typer.echo(f"{recipe.description}\n")
    typer.echo("### Parameters\n")
    typer.echo("| Name | Type | Required | Default | Description |")
    typer.echo("|------|------|----------|---------|-------------|")
    for p in recipe.parameters:
        default = p.default if p.default is not None else "-"
        required = "Yes" if p.required else "No"
        typer.echo(
            f"| {p.name} | {p.type} | {required} | {default} | {p.description} |"
        )


@recipe_app.command(name="run")
def recipe_run_cmd(
    name: str = typer.Argument(..., help="Recipe name."),
    file: str = typer.Argument(..., help="Path to the data file."),
    param: list[str] | None = typer.Option(
        None, "--param", "-p", help="Parameters as key=value pairs."
    ),
    output_format: str = _FORMAT_CHOICE,
    output: Path | None = typer.Option(None, "-o", help="Save output to file."),
) -> None:
    """Run an analysis recipe on a dataset."""
    from edatool.recipes.registry import get_recipe

    recipe = get_recipe(name)
    if recipe is None:
        typer.echo(f"Recipe '{name}' not found.", err=True)
        raise typer.Exit(code=1)

    df = load(file)

    # Parse key=value params
    params: dict[str, str] = {}
    if param:
        for p in param:
            if "=" not in p:
                typer.echo(f"Invalid parameter format: '{p}'. Use key=value.", err=True)
                raise typer.Exit(code=1)
            key, value = p.split("=", 1)
            params[key] = value

    # Convert numeric params
    parsed_params: dict[str, object] = {}
    param_types = {rp.name: rp.type for rp in recipe.parameters}
    for key, value in params.items():
        expected_type = param_types.get(key)
        if expected_type == "float":
            try:
                parsed_params[key] = float(value)
            except ValueError:
                typer.echo(
                    f"Invalid value for parameter '{key}': "
                    f"expected float, got '{value}'.",
                    err=True,
                )
                raise typer.Exit(code=1)
        elif expected_type == "int":
            try:
                parsed_params[key] = int(value)
            except ValueError:
                typer.echo(
                    f"Invalid value for parameter '{key}': "
                    f"expected int, got '{value}'.",
                    err=True,
                )
                raise typer.Exit(code=1)
        elif expected_type == "bool":
            parsed_params[key] = value.lower() in ("true", "1", "yes")
        else:
            parsed_params[key] = value

    result = recipe.run(df, **parsed_params)
    text = result.to_json() if output_format == "json" else result.to_markdown()
    _output_result(text, output)


# ---------------------------------------------------------------------------
# catalog commands
# ---------------------------------------------------------------------------


@catalog_app.command(name="register")
def catalog_register_cmd(
    file: str = typer.Argument(..., help="Path to the data file."),
    name: str = typer.Option("", "--name", help="Display name for the dataset."),
    description: str = typer.Option("", "--description", "-d", help="Description."),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags."),
    catalog_dir: str = typer.Option("./catalog", "--catalog-dir", help="Catalog dir."),
) -> None:
    """Register a dataset in the catalog."""
    from edatool.catalog.store import Catalog

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    catalog = Catalog(catalog_dir)
    entry = catalog.register(file, name=name, description=description, tags=tag_list)
    typer.echo(f"Registered dataset '{entry.id}' ({entry.rows:,} rows)")


@catalog_app.command(name="list")
def catalog_list_cmd(
    sort_by: str = typer.Option(
        "registered_at", "--sort-by", help="Sort by: registered_at or last_analyzed."
    ),
    limit: int = typer.Option(0, "--limit", help="Max entries (0 = all)."),
    catalog_dir: str = typer.Option("./catalog", "--catalog-dir", help="Catalog dir."),
) -> None:
    """List all registered datasets."""
    from edatool.catalog.store import Catalog

    catalog = Catalog(catalog_dir)
    entries = catalog.list_datasets(sort_by=sort_by, limit=limit)
    if not entries:
        typer.echo("No datasets registered.")
        return

    typer.echo("| ID | Rows | Columns | Quality | Tags | Registered |")
    typer.echo("|----|------|---------|---------|------|------------|")
    for e in entries:
        score = f"{e.quality.overall_score:.2f}" if e.quality else "-"
        tags_str = ", ".join(e.tags) if e.tags else "-"
        typer.echo(
            f"| {e.id} | {e.rows:,} | {len(e.columns)} "
            f"| {score} | {tags_str} | {e.registered_at} |"
        )


@catalog_app.command(name="search")
def catalog_search_cmd(
    query: str = typer.Argument("", help="Search keyword."),
    tag: str = typer.Option("", "--tag", help="Filter by tag."),
    catalog_dir: str = typer.Option("./catalog", "--catalog-dir", help="Catalog dir."),
) -> None:
    """Search datasets by keyword or tag."""
    from edatool.catalog.store import Catalog

    catalog = Catalog(catalog_dir)
    results = catalog.search(query, tag=tag)
    if not results:
        typer.echo("No datasets found.")
        return

    for e in results:
        tags_str = f" [{', '.join(e.tags)}]" if e.tags else ""
        typer.echo(f"- {e.id}: {e.description or e.source}{tags_str}")


@catalog_app.command(name="show")
def catalog_show_cmd(
    dataset_id: str = typer.Argument(..., help="Dataset ID."),
    catalog_dir: str = typer.Option("./catalog", "--catalog-dir", help="Catalog dir."),
) -> None:
    """Show detailed info about a dataset."""
    from edatool.catalog.store import Catalog

    catalog = Catalog(catalog_dir)
    entry = catalog.get(dataset_id)
    if entry is None:
        typer.echo(f"Dataset '{dataset_id}' not found.", err=True)
        raise typer.Exit(code=1)
    typer.echo(entry.to_markdown())


@catalog_app.command(name="compare")
def catalog_compare_cmd(
    id_a: str = typer.Argument(..., help="First dataset ID."),
    id_b: str = typer.Argument(..., help="Second dataset ID."),
    catalog_dir: str = typer.Option("./catalog", "--catalog-dir", help="Catalog dir."),
) -> None:
    """Compare two datasets (schema + quality)."""
    from edatool.catalog.store import Catalog

    catalog = Catalog(catalog_dir)
    report = catalog.compare(id_a, id_b)
    typer.echo(report)


@catalog_app.command(name="record")
def catalog_record_cmd(
    dataset_id: str = typer.Argument(..., help="Dataset ID."),
    analysis_type: str = typer.Option(
        ..., "--analysis-type", help="Type of analysis (profile, correlations, etc.)."
    ),
    report: str = typer.Option("", "--report", help="Path to the report file."),
    findings: str = typer.Option(
        "", "--findings", help="Comma-separated key findings."
    ),
    catalog_dir: str = typer.Option("./catalog", "--catalog-dir", help="Catalog dir."),
) -> None:
    """Record an analysis result for a dataset."""
    from edatool.catalog.store import Catalog

    finding_list = (
        [f.strip() for f in findings.split(",") if f.strip()] if findings else []
    )
    catalog = Catalog(catalog_dir)
    record = catalog.record_analysis(
        dataset_id,
        analysis_type=analysis_type,
        report_path=report,
        key_findings=finding_list,
    )
    if record is None:
        typer.echo(f"Dataset '{dataset_id}' not found.", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Recorded {record.id} ({record.analysis_type}) for {dataset_id}")


@catalog_app.command(name="check-freshness")
def catalog_freshness_cmd(
    catalog_dir: str = typer.Option("./catalog", "--catalog-dir", help="Catalog dir."),
) -> None:
    """Check if registered files have changed since registration."""
    from edatool.catalog.store import Catalog

    catalog = Catalog(catalog_dir)
    results = catalog.check_freshness()
    if not results:
        typer.echo("No datasets registered.")
        return

    for dataset_id, status in results:
        icon = {"ok": "ok", "changed": "CHANGED", "missing": "MISSING"}
        typer.echo(f"  [{icon.get(status, status)}] {dataset_id}")


if __name__ == "__main__":
    app()
