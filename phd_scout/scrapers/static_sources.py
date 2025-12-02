from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup

from phd_scout.models import Category, PhDPosition
from phd_scout.scrapers.base import BaseScraper


class StaticHTMLScraper(BaseScraper):
    """A demo scraper that mimics parsing university listings with BeautifulSoup."""

    name = "Static HTML Scraper"

    def __init__(self, html: str, metadata: dict):
        self.html = html
        self.metadata = metadata

    def scrape(self) -> List[PhDPosition]:
        soup = BeautifulSoup(self.html, "html.parser")
        results: List[PhDPosition] = []
        for block in soup.select("article.position"):
            title = block.select_one("h2").get_text(strip=True)
            department = block.select_one(".department").get_text(strip=True)
            supervisor = block.select_one(".supervisor").get_text(strip=True)
            topic = block.select_one(".topic").get_text(strip=True)
            funding = block.select_one(".funding").get_text(strip=True)
            deadline = block.select_one(".deadline").get_text(strip=True) or None
            url = block.select_one("a.apply")['href']
            results.append(
                PhDPosition(
                    title=title,
                    university=self.metadata["university"],
                    department=department,
                    supervisors=supervisor,
                    topic=topic,
                    country=self.metadata["country"],
                    funding=funding,
                    deadline=deadline,
                    url=url,
                    category=self.metadata["categorizer"](topic, title),
                    scraped_from=self.metadata.get("source_name", self.name),
                )
            )
        return results


def sample_scrapers() -> List[BaseScraper]:
    """Return scrapers representing sources in Australia, Europe, and Canada."""

    def categorize(topic: str, title: str) -> Category:
        text = f"{topic} {title}".lower()
        imaging = any(k in text for k in ["imaging", "mri", "ct", "ultrasound", "radiology"])
        bioelectric = any(k in text for k in ["signal", "ecg", "eeg", "emg", "bioelectric"])
        ai = any(k in text for k in ["deep learning", "machine learning", "ai", "neural"])
        flags = [imaging, bioelectric, ai]
        if sum(flags) > 1:
            return Category.MIXED
        if imaging:
            return Category.IMAGING
        if bioelectric:
            return Category.BIOELECTRIC
        if ai:
            return Category.AI
        return Category.MIXED

    anu_html = """
    <section>
      <article class="position">
        <h2>PhD in Radiomics for Early Cancer Detection</h2>
        <div class="department">College of Engineering & Computer Science</div>
        <div class="supervisor">Dr. Alex Doe</div>
        <div class="topic">Deep learning-driven medical imaging</div>
        <div class="funding">Full scholarship available</div>
        <div class="deadline">2025-01-15</div>
        <a class="apply" href="https://anu.edu/phd/radiomics">Apply</a>
      </article>
      <article class="position">
        <h2>Biomedical Signal Processing for Cardiac Health</h2>
        <div class="department">School of Computing</div>
        <div class="supervisor">Prof. Casey Nguyen</div>
        <div class="topic">Multimodal ECG and wearable signal fusion</div>
        <div class="funding">Top-up stipend</div>
        <div class="deadline">2024-12-01</div>
        <a class="apply" href="https://anu.edu/phd/cardiac-signals">Apply</a>
      </article>
    </section>
    """

    tum_html = """
    <section>
      <article class="position">
        <h2>AI for Neuroimaging-based Disease Progression</h2>
        <div class="department">Graduate School of Information Science</div>
        <div class="supervisor">Dr. Lara Schmidt</div>
        <div class="topic">Graph neural networks for MRI longitudinal studies</div>
        <div class="funding">DFG-funded</div>
        <div class="deadline">2025-03-31</div>
        <a class="apply" href="https://tum.de/phd/neuroimaging">Apply</a>
      </article>
      <article class="position">
        <h2>Closed-loop Neurostimulation Control</h2>
        <div class="department">Department of Electrical Engineering</div>
        <div class="supervisor">Prof. Marie Keller</div>
        <div class="topic">Real-time EEG decoding and stimulation</div>
        <div class="funding">Tuition waiver + stipend</div>
        <div class="deadline"></div>
        <a class="apply" href="https://tum.de/phd/neurostimulation">Apply</a>
      </article>
    </section>
    """

    mcgill_html = """
    <section>
      <article class="position">
        <h2>Trustworthy AI for Radiotherapy Planning</h2>
        <div class="department">Department of Biomedical Engineering</div>
        <div class="supervisor">Dr. Nina Kapoor</div>
        <div class="topic">Interpretable deep learning for treatment planning</div>
        <div class="funding">Fully funded</div>
        <div class="deadline">2025-02-28</div>
        <a class="apply" href="https://mcgill.ca/phd/radiotherapy-ai">Apply</a>
      </article>
    </section>
    """

    metadata = [
        {"university": "Australian National University", "country": "Australia", "source_name": "ANU Graduate Research", "categorizer": categorize},
        {"university": "Technical University of Munich", "country": "Germany", "source_name": "TUM Grad School", "categorizer": categorize},
        {"university": "McGill University", "country": "Canada", "source_name": "McGill Graduate Studies", "categorizer": categorize},
    ]
    html_payloads = [anu_html, tum_html, mcgill_html]

    return [StaticHTMLScraper(html, meta) for html, meta in zip(html_payloads, metadata)]
