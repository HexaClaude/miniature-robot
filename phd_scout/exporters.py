from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from tabulate import tabulate

from phd_scout.config import EXPORTS_DIR
from phd_scout.models import PhDPosition


def export_json(positions: Iterable[PhDPosition], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in positions]
    path.write_text(json.dumps(data, indent=2))
    return path


def export_csv(positions: Iterable[PhDPosition], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in positions]
    if not data:
        path.write_text("")
        return path
    headers = data[0].keys()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    return path


def to_table(positions: Iterable[PhDPosition]) -> str:
    rows = [
        [
            p.title,
            p.university,
            p.country,
            p.category.value,
            p.funding,
            p.deadline or "--",
            p.url,
        ]
        for p in positions
    ]
    headers = ["Title", "University", "Country", "Category", "Funding", "Deadline", "Link"]
    return tabulate(rows, headers=headers, tablefmt="github")


def default_export_path(fmt: str) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return EXPORTS_DIR / f"phd_positions.{fmt}"
