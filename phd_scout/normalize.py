from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from phd_scout.models import Category, PhDPosition


KEYWORD_MAP = {
    Category.IMAGING: ["imaging", "radiology", "mri", "ct", "ultrasound"],
    Category.BIOELECTRIC: ["signal", "ecg", "eeg", "emg", "bioelectric"],
    Category.AI: ["ai", "machine learning", "deep learning", "neural"],
}


def categorize_from_text(title: str, topic: str) -> Category:
    text = f"{title} {topic}".lower()
    hits = []
    for category, keywords in KEYWORD_MAP.items():
        if any(k in text for k in keywords):
            hits.append(category)
    if len(hits) > 1:
        return Category.MIXED
    if hits:
        return hits[0]
    return Category.MIXED


def deduplicate(positions: Iterable[PhDPosition]) -> List[PhDPosition]:
    seen = set()
    unique: List[PhDPosition] = []
    for item in positions:
        if item.normalized_key in seen:
            continue
        seen.add(item.normalized_key)
        unique.append(item)
    return unique


def normalize_deadline(deadline: str | None) -> str | None:
    if not deadline:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(deadline, fmt).date().isoformat()
        except ValueError:
            continue
    return deadline


def clean_positions(positions: Iterable[PhDPosition]) -> List[PhDPosition]:
    cleaned: List[PhDPosition] = []
    for pos in positions:
        deadline = normalize_deadline(pos.deadline)
        category = pos.category or categorize_from_text(pos.title, pos.topic)
        cleaned.append(
            PhDPosition(
                title=pos.title.strip(),
                university=pos.university.strip(),
                department=pos.department.strip(),
                supervisors=pos.supervisors.strip(),
                topic=pos.topic.strip(),
                country=pos.country.strip(),
                funding=pos.funding.strip(),
                deadline=deadline,
                url=pos.url.strip(),
                category=category,
                scraped_from=pos.scraped_from,
                scraped_at=pos.scraped_at,
            )
        )
    return deduplicate(cleaned)
