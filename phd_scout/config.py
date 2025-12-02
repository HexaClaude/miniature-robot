from __future__ import annotations

from pathlib import Path

DATA_PATH = Path("data/positions.json")
EXPORTS_DIR = Path("exports")


def ensure_paths() -> None:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
