from __future__ import annotations

import json
from typing import Iterable, List

from phd_scout.config import DATA_PATH, ensure_paths
from phd_scout.models import PhDPosition


def load_positions() -> List[PhDPosition]:
    ensure_paths()
    if not DATA_PATH.exists():
        return []
    data = json.loads(DATA_PATH.read_text())
    return [PhDPosition(**item) for item in data]


def save_positions(positions: Iterable[PhDPosition]) -> None:
    ensure_paths()
    serialized = [pos.to_dict() for pos in positions]
    DATA_PATH.write_text(json.dumps(serialized, indent=2))
