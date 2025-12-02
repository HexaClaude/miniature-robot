from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class Category(str, Enum):
    IMAGING = "Imaging"
    BIOELECTRIC = "Bioelectric"
    AI = "AI"
    MIXED = "Mixed"


@dataclass
class PhDPosition:
    title: str
    university: str
    department: str
    supervisors: str
    topic: str
    country: str
    funding: str
    deadline: Optional[str]
    url: str
    category: Category
    scraped_from: str
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Optional[str]]:
        data = asdict(self)
        data["category"] = self.category.value
        return data

    @property
    def normalized_key(self) -> str:
        base = f"{self.title}|{self.university}|{self.supervisors}".lower()
        return " ".join(base.split())
