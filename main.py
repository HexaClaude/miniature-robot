from __future__ import annotations

from pathlib import Path
from typing import Optional

import click
from rich import print

from phd_scout import config
from phd_scout.exporters import default_export_path, export_csv, export_json, to_table
from phd_scout.models import Category
from phd_scout.normalize import deduplicate
from phd_scout.pipeline import run_scrapers
from phd_scout.query import filter_positions
from phd_scout.scrapers.static_sources import sample_scrapers
from phd_scout.storage import load_positions, save_positions


def _category_choice(value: Optional[str]) -> Optional[Category]:
    if value is None:
        return None
    return Category(value)


@click.group(help="Automated collector for medical imaging & bioelectric PhD opportunities.")
def app() -> None:
    """CLI entry point."""
    config.ensure_paths()


@app.command()
@click.option("--replace", "-r", is_flag=True, help="Replace stored data instead of merging.")
def refresh(replace: bool) -> None:
    """Scrape all sources and update the local dataset."""

    scrapers = sample_scrapers()
    print(f"[bold cyan]Running {len(scrapers)} scrapers...[/bold cyan]")
    new_positions = run_scrapers(scrapers)

    if replace:
        merged = new_positions
    else:
        merged = deduplicate([*load_positions(), *new_positions])

    save_positions(merged)
    print(f"[green]Saved {len(merged)} positions to {config.DATA_PATH}[/green]")


@app.command(name="list")
@click.option("--country", help="Filter by country substring.")
@click.option(
    "--category",
    type=click.Choice([c.value for c in Category], case_sensitive=False),
    callback=lambda ctx, param, value: _category_choice(value),
    help="Imaging, Bioelectric, AI, Mixed",
)
@click.option("--funded-only", "-f", is_flag=True, help="Only show positions with explicit funding.")
@click.option("--deadline-before", help="ISO date (YYYY-MM-DD).")
def list_positions(
    country: Optional[str], category: Optional[Category], funded_only: bool, deadline_before: Optional[str]
) -> None:
    """Display positions with optional filters."""

    positions = load_positions()
    if not positions:
        print("[yellow]No positions found. Run `python main.py refresh` first.[/yellow]")
        raise SystemExit(1)

    filtered = filter_positions(
        positions, country=country, category=category, funded_only=funded_only, deadline_before=deadline_before
    )

    if not filtered:
        print("[yellow]No results for the selected filters.[/yellow]")
        raise SystemExit(1)

    print(to_table(filtered))


@app.command()
@click.option("--fmt", type=click.Choice(["json", "csv"], case_sensitive=False), default="json", show_default=True)
@click.option("--output", type=click.Path(path_type=Path), help="Output path; defaults to exports/phd_positions.{fmt}")
@click.option("--country", help="Optional country filter")
@click.option(
    "--category",
    type=click.Choice([c.value for c in Category], case_sensitive=False),
    callback=lambda ctx, param, value: _category_choice(value),
    help="Optional category filter",
)
@click.option("--funded-only", "-f", is_flag=True, help="Only export funded positions")
def export(
    fmt: str,
    output: Optional[Path],
    country: Optional[str],
    category: Optional[Category],
    funded_only: bool,
) -> None:
    """Export positions to JSON or CSV with optional filtering."""

    positions = load_positions()
    filtered = filter_positions(positions, country=country, category=category, funded_only=funded_only)

    if output is None:
        output = default_export_path(fmt)

    fmt_lower = fmt.lower()
    if fmt_lower == "json":
        path = export_json(filtered, output)
    elif fmt_lower == "csv":
        path = export_csv(filtered, output)
    else:
        raise click.BadParameter("Unsupported format; use json or csv.")

    print(f"[green]Exported {len(filtered)} positions to {path}[/green]")


@app.command()
def sources() -> None:
    """List available scrapers."""

    scrapers = sample_scrapers()
    for scraper in scrapers:
        print(f"- {scraper.metadata['university']} ({scraper.metadata['country']}) via {scraper.metadata['source_name']}")


if __name__ == "__main__":
    app()
