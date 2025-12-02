from __future__ import annotations

from datetime import date
from typing import Iterable, List, Optional

from phd_scout.models import Category, PhDPosition


def filter_positions(
    positions: Iterable[PhDPosition],
    country: Optional[str] = None,
    category: Optional[Category] = None,
    funded_only: bool = False,
    deadline_before: Optional[str] = None,
) -> List[PhDPosition]:
    results: List[PhDPosition] = []
    parsed_deadline = None
    if deadline_before:
        try:
            parsed_deadline = date.fromisoformat(deadline_before)
        except ValueError:
            parsed_deadline = None

    for pos in positions:
        if country and country.lower() not in pos.country.lower():
            continue
        if category and pos.category != category:
            continue
        if funded_only and "fund" not in pos.funding.lower():
            continue
        if parsed_deadline and pos.deadline:
            try:
                pos_deadline = date.fromisoformat(pos.deadline)
                if pos_deadline > parsed_deadline:
                    continue
            except ValueError:
                pass
        results.append(pos)
    return results
