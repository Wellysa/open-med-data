EVS Explore scraper
====================

This folder contains data and scripts related to scraping terminology
content from the NCI EVS Explore site:
`https://evsexplore.semantics.cancer.gov/evsexplore/welcome`.

Initial goal:
- capture the main concepts metadata in a machine-readable format (CSV/JSON)
  for downstream use in the `open-med-data` project.

Scripts:
- `crawl_evs_explore.py` – basic HTML scraper for the landing page.
- `crawl_evs_api.py` – full scrape via the public REST API. It downloads:
  - terminologies list,
  - per-terminology metadata (associations, roles, properties, qualifiers, etc.),
  - subsets (if available),
  - all concepts (paginated, include=full) into `evs/api/concepts/<terminology>.jsonl`,
  - mapsets (global).
- `split_large_jsonl.py` – splits any `*.jsonl` in `evs/api/concepts/` larger than 80 MB into parts of ≤50 MB (e.g. `ncit.part001.jsonl`, `ncit.part002.jsonl`) so the repo can be pushed to GitHub (100 MB file limit). Run after a full API scrape if you hit push errors.

Large concept files in this repo are stored as part files (e.g. `chebi.part001.jsonl`, …). To rejoin locally: `cat evs/api/concepts/chebi.part*.jsonl > evs/api/concepts/chebi.jsonl` (Unix) or use the same order in PowerShell.

