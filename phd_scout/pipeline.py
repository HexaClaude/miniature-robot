from __future__ import annotations

from typing import Iterable, List

from phd_scout.models import PhDPosition
from phd_scout.normalize import clean_positions
from phd_scout.scrapers.base import BaseScraper


def run_scrapers(scrapers: Iterable[BaseScraper]) -> List[PhDPosition]:
    collected: List[PhDPosition] = []
    for scraper in scrapers:
        try:
            collected.extend(scraper.scrape())
        except Exception as exc:  # noqa: BLE001
            # Preserve partial results and continue
            print(f"[warn] {scraper.name} failed: {exc}")
    return clean_positions(collected)
