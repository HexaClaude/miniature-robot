from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from phd_scout.models import PhDPosition


class BaseScraper(ABC):
    """Base scraper interface.

    Implementations should return PhDPosition objects that are already normalized
    enough to pass through the cleaning pipeline.
    """

    name: str

    @abstractmethod
    def scrape(self) -> List[PhDPosition]:
        raise NotImplementedError
