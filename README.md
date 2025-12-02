# PhD Scout

Automated CLI for collecting and curating PhD opportunities in medical imaging, biomedical signal processing / bioelectric engineering, and AI for medical applications across Australia, Europe, and Canada.

## Features
- **Automated scraping** via modular scraper classes (currently static demo sources for ANU, TUM, and McGill) using BeautifulSoup for HTML parsing.
- **Normalization** of deadlines, categories (Imaging, Bioelectric, AI, Mixed), and deduplication across sources.
- **Filtering** by country, category, funding availability, and deadline.
- **Export** results to JSON or CSV, or view in a Markdown table.
- **Refresh** command to re-run scrapers, merge or replace stored data, and handle scraper errors gracefully.

## Quickstart
1. Install dependencies (Python 3.11+ recommended):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the initial scrape:
   ```bash
   python main.py refresh
   ```
3. List positions with optional filters:
   ```bash
   python main.py list --country Canada --category AI --funded-only
   ```
4. Export filtered data:
   ```bash
   python main.py export --fmt csv --country Germany
   ```

Data is stored locally at `data/positions.json`; exports are written to `exports/`.

## Architecture
- `main.py`: Typer CLI entrypoint with `refresh`, `list`, `export`, and `sources` commands.
- `phd_scout/models.py`: Data model + category enum.
- `phd_scout/scrapers/`: Base scraper plus static HTML scrapers illustrating how to add universities.
- `phd_scout/normalize.py`: Deadline normalization, categorization, and deduplication.
- `phd_scout/query.py`: Filter helpers for country, category, funding, and deadlines.
- `phd_scout/exporters.py`: JSON/CSV export and table rendering.
- `phd_scout/pipeline.py`: Runs scrapers with error isolation and cleaning.
- `phd_scout/storage.py`: Simple JSON persistence.

## Extending the system
- **Add a new source**: create a new scraper subclass in `phd_scout/scrapers/` that implements `scrape()` and returns `PhDPosition` objects. Register it in `sample_scrapers()` (or your own source registry) to be picked up by `refresh`.
- **Add a new country**: include the country name in the scraper metadata so filters pick it up automatically.
- **Add keyword-based alerts**: hook into the `refresh` command to compare new results against saved ones and trigger notifications (email/webhook) when a keyword appears in `title` or `topic`.
- **Add AI-ranking of positions**: after `run_scrapers`, pass positions through a ranking module that scores opportunities using embeddings or rule-based heuristics, then sort results before saving/exporting.
- **Schedule continuous updates**: run `python main.py refresh` via cron or a CI workflow to keep `data/positions.json` current.

## Error handling
Scraper failures are logged to the console, and remaining scrapers continue to run. Deadlines are parsed across multiple formats and left untouched if parsing fails. Deduplication uses a normalized key of `title|university|supervisors` to collapse overlap across multiple sources.

## Notes
The included scrapers use static HTML payloads to keep the project runnable offline. Replace these payloads with real HTTP requests when deploying, while reusing the same parsing and normalization pipeline.
