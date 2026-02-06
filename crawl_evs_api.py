"""
Full EVS Explore scraper using the public REST API.

It fetches:
- list of terminologies
- per-terminology metadata blocks (associations, roles, properties, qualifiers, etc.)
- all concepts (paginated) with include=full into JSONL files

Outputs are saved under `evs/api/`.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter, Retry


BASE_API = "https://evsexplore.semantics.cancer.gov/evsexplore/api/v1"
OUT_DIR = Path("evs") / "api"
CONCEPTS_DIR = OUT_DIR / "concepts"
PAGE_SIZE = 500  # adjust if needed; 500 keeps request count reasonable
SLEEP_BETWEEN_PAGES = 0.05  # gentle pacing to avoid hammering the API
INCLUDE_ORDER = ["full", "summary", "minimal"]


def make_session() -> requests.Session:
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


SESSION = make_session()


def get_json(path: str, **params: Any) -> Any:
    url = f"{BASE_API}/{path.lstrip('/')}"
    resp = SESSION.get(url, params=params or None, timeout=60)
    resp.raise_for_status()
    return resp.json()


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_terminologies() -> list[dict]:
    terms = get_json("metadata/terminologies")
    save_json(terms, OUT_DIR / "terminologies.json")
    return terms


def fetch_metadata_blocks(terminology: str) -> None:
    term_dir = OUT_DIR / "metadata" / terminology
    endpoints = {
        "metadata": f"metadata/{terminology}",
        "associations": f"metadata/{terminology}/associations?include=summary",
        "roles": f"metadata/{terminology}/roles?include=summary",
        "properties": f"metadata/{terminology}/properties?include=summary",
        "qualifiers": f"metadata/{terminology}/qualifiers?include=summary",
        "termTypes": f"metadata/{terminology}/termTypes",
        "synonymSources": f"metadata/{terminology}/synonymSources",
        "synonymTypes": f"metadata/{terminology}/synonymTypes",
        "definitionSources": f"metadata/{terminology}/definitionSources",
        "definitionTypes": f"metadata/{terminology}/definitionTypes",
        "welcomeText": f"metadata/{terminology}/welcomeText",
    }
    for name, path in endpoints.items():
        out_path = term_dir / f"{name}.json"
        try:
            data = get_json(path)
        except Exception as exc:  # pragma: no cover - defensive logging
            save_json({"error": str(exc), "endpoint": path}, out_path)
            continue
        save_json(data, out_path)


def fetch_mapsets() -> None:
    """Mapsets are global (not per terminology)."""
    try:
        data = get_json("mapset", include="minimal")
    except Exception as exc:  # pragma: no cover
        save_json({"error": str(exc), "endpoint": "mapset"}, OUT_DIR / "mapsets.error.json")
        return
    save_json(data, OUT_DIR / "mapsets.json")


def fetch_subsets(terminology: str) -> None:
    """
    Subsets are per terminology; some terminologies may return 404/empty.
    """
    term_dir = OUT_DIR / "subsets" / terminology
    try:
        data = get_json(f"subset/{terminology}", include="minimal")
    except Exception as exc:  # pragma: no cover
        save_json({"error": str(exc), "endpoint": f"subset/{terminology}"}, term_dir / "subset.error.json")
        return
    save_json(data, term_dir / "subset.json")


def fetch_concepts(terminology: str, page_size: int = PAGE_SIZE) -> None:
    """
    Streams all concepts for a terminology to JSONL.
    """
    CONCEPTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CONCEPTS_DIR / f"{terminology}.jsonl"
    meta_path = CONCEPTS_DIR / f"{terminology}_meta.json"

    from_record = 0
    total = None
    pages = 0
    include_used = None
    probe_errors: dict[str, str] = {}

    def probe_include() -> tuple[str, dict]:
        for inc in INCLUDE_ORDER:
            try:
                resp = get_json(
                    f"concept/{terminology}/search",
                    include=inc,
                    pageSize=1,
                    fromRecord=0,
                )
                return inc, resp
            except Exception as exc:  # pragma: no cover - fallback logic
                probe_errors[inc] = str(exc)
        raise RuntimeError(f"Could not fetch concepts for {terminology}")

    try:
        include_used, first_resp = probe_include()
    except Exception as exc:  # pragma: no cover - log and stop
        save_json(
            {"error": str(exc), "probe_errors": probe_errors},
            meta_path,
        )
        return

    with out_path.open("w", encoding="utf-8") as f:
        # first page
        concepts = first_resp.get("concepts", [])
        total = first_resp.get("total")
        for concept in concepts:
            f.write(json.dumps(concept, ensure_ascii=False) + "\n")
        from_record += len(concepts)
        if concepts:
            pages += 1

        # remaining pages
        while True:
            if total is not None and from_record >= total:
                break

            try:
                resp = get_json(
                    f"concept/{terminology}/search",
                    include=include_used,
                    pageSize=page_size,
                    fromRecord=from_record,
                )
            except requests.HTTPError as exc:  # pragma: no cover - runtime fallback
                msg = ""
                if exc.response is not None:
                    try:
                        msg = exc.response.json().get("message", "")
                    except Exception:
                        msg = exc.response.text
                if "license restriction" in msg.lower() and page_size > 10:
                    page_size = 10
                    continue
                save_json(
                    {
                        "error": str(exc),
                        "message": msg,
                        "include": include_used,
                        "page_size": page_size,
                        "from_record": from_record,
                    },
                    meta_path,
                )
                return
            concepts = resp.get("concepts", [])
            if not concepts:
                break

            for concept in concepts:
                f.write(json.dumps(concept, ensure_ascii=False) + "\n")

            from_record += len(concepts)
            pages += 1

            time.sleep(SLEEP_BETWEEN_PAGES)

    save_json(
        {
            "terminology": terminology,
            "total": total,
            "page_size": page_size,
            "include": include_used,
            "pages": pages,
            "probe_errors": probe_errors,
        },
        meta_path,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    terms = fetch_terminologies()
    fetch_mapsets()

    for term in terms:
        terminology = term["terminology"]
        fetch_metadata_blocks(terminology)
        fetch_subsets(terminology)
        fetch_concepts(terminology)


if __name__ == "__main__":
    main()

