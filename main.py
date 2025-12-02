from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from phd_scout import config
from phd_scout.exporters import default_export_path, export_csv, export_json, to_table
from phd_scout.models import Category
from phd_scout.normalize import deduplicate
from phd_scout.pipeline import run_scrapers
from phd_scout.query import filter_positions
from phd_scout.scrapers.static_sources import sample_scrapers
from phd_scout.storage import load_positions, save_positions

app = typer.Typer(help="Automated collector for medical imaging & bioelectric PhD opportunities.")


@app.command()
def refresh(replace: bool = typer.Option(False, help="Replace stored data instead of merging.")):
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
def list_positions(
    country: Optional[str] = typer.Option(None, help="Filter by country substring."),
    category: Optional[Category] = typer.Option(None, case_sensitive=False, help="Imaging, Bioelectric, AI, Mixed"),
    funded_only: bool = typer.Option(False, help="Only show positions with explicit funding."),
    deadline_before: Optional[str] = typer.Option(None, help="ISO date (YYYY-MM-DD)."),
):
    """Display positions with optional filters."""

    positions = load_positions()
    if not positions:
        print("[yellow]No positions found. Run `python main.py refresh` first.[/yellow]")
        raise typer.Exit(code=1)

    filtered = filter_positions(positions, country=country, category=category, funded_only=funded_only, deadline_before=deadline_before)

    if not filtered:
        print("[yellow]No results for the selected filters.[/yellow]")
        raise typer.Exit(code=1)

    print(to_table(filtered))


@app.command()
def export(
    fmt: str = typer.Option("json", help="json or csv"),
    output: Optional[Path] = typer.Option(None, help="Output path; defaults to exports/phd_positions.{fmt}"),
    country: Optional[str] = typer.Option(None, help="Optional country filter"),
    category: Optional[Category] = typer.Option(None, case_sensitive=False, help="Optional category filter"),
    funded_only: bool = typer.Option(False, help="Only export funded positions"),
):
    """Export positions to JSON or CSV with optional filtering."""

    positions = load_positions()
    filtered = filter_positions(positions, country=country, category=category, funded_only=funded_only)

    if output is None:
        output = default_export_path(fmt)

    if fmt.lower() == "json":
        path = export_json(filtered, output)
    elif fmt.lower() == "csv":
        path = export_csv(filtered, output)
    else:
        raise typer.BadParameter("Unsupported format; use json or csv.")

    print(f"[green]Exported {len(filtered)} positions to {path}[/green]")


@app.command()
def sources():
    """List available scrapers."""

    scrapers = sample_scrapers()
    for scraper in scrapers:
        print(f"- {scraper.metadata['university']} ({scraper.metadata['country']}) via {scraper.metadata['source_name']}")


if __name__ == "__main__":
    config.ensure_paths()
    app()
