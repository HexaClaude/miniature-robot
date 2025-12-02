from __future__ import annotations

import json
from typing import Iterable, List

from phd_scout.config import DATA_PATH, ensure_paths
from phd_scout.models import Category, PhDPosition


def load_positions() -> List[PhDPosition]:
    ensure_paths()
    if not DATA_PATH.exists():
        return []
    data = json.loads(DATA_PATH.read_text())
    hydrated = []
    for item in data:
        raw_category = item.get("category")
        if isinstance(raw_category, str):
            try:
                item["category"] = Category(raw_category)
            except ValueError:
                item["category"] = Category.MIXED
        hydrated.append(PhDPosition(**item))
    return hydrated


def save_positions(positions: Iterable[PhDPosition]) -> None:
    ensure_paths()
    serialized = [pos.to_dict() for pos in positions]
    DATA_PATH.write_text(json.dumps(serialized, indent=2))
