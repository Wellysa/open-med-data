import csv
import json
from collections import deque
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://evsexplore.semantics.cancer.gov/evsexplore/welcome"
OUT_DIR = Path("evs")
PAGES_DIR = OUT_DIR / "pages"
MAX_PAGES = 500  # bezpieczny limit, można zwiększyć jeśli potrzeba


def fetch_html(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def normalize_url(base_url: str, href: str) -> str | None:
    """
    Zamień link względny na absolutny URL i usuń fragment (#anchor).
    Zwraca None, jeśli href nie jest sensownym linkiem.
    """
    if not href:
        return None
    href = href.strip()
    if href.startswith("mailto:") or href.startswith("javascript:"):
        return None
    abs_url = urljoin(base_url, href)
    abs_url, _ = urldefrag(abs_url)
    return abs_url


def is_internal_evs_url(url: str) -> bool:
    """
    Sprawdza, czy URL należy do domeny EVS Explore, aby nie wychodzić poza serwis.
    """
    parsed = urlparse(url)
    if not parsed.scheme or parsed.scheme not in ("http", "https"):
        return False
    if parsed.netloc != "evsexplore.semantics.cancer.gov":
        return False
    # opcjonalnie możemy ograniczyć się do ścieżek zawierających /evsexplore/
    return "/evsexplore/" in parsed.path


def extract_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        abs_url = normalize_url(base_url, a["href"])
        if not abs_url:
            continue
        if not is_internal_evs_url(abs_url):
            continue
        links.append(abs_url)
    return links


def parse_page(html: str, url: str) -> dict:
    """
    Ogólny parser strony EVS: tytuł, nagłówki, linki.
    Strukturę można rozszerzać po analizie DOM.
    """
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    headings = []
    for level in range(1, 7):
        for h in soup.find_all(f"h{level}"):
            text = h.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})

    links = extract_links(soup, url)

    return {
        "url": url,
        "title": title,
        "headings": headings,
        "links": links,
    }


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def slugify_url(url: str) -> str:
    """
    Tworzy prostą nazwę pliku na podstawie URL (bez znaków specjalnych).
    """
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path.endswith("/"):
        path = path[:-1] or "/"
    # zamień / na _
    slug = path.replace("/", "_")
    if not slug:
        slug = "root"
    # dodaj zakodowaną część query, jeśli istnieje
    if parsed.query:
        safe_query = parsed.query.replace("=", "-").replace("&", "_")
        slug = f"{slug}__{safe_query}"
    return slug


def save_page_assets(url: str, html: str, parsed: dict) -> None:
    slug = slugify_url(url)
    html_path = PAGES_DIR / f"{slug}.html"
    json_path = PAGES_DIR / f"{slug}.json"

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    save_json(parsed, json_path)


def write_index_csv(records: Iterable[dict], path: Path) -> None:
    """
    Zapisuje indeks wszystkich odwiedzonych stron (URL, tytuł, liczba nagłówków, liczba linków).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["url", "title", "n_headings", "n_links"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "url": rec.get("url", ""),
                    "title": rec.get("title", ""),
                    "n_headings": len(rec.get("headings", [])),
                    "n_links": len(rec.get("links", [])),
                }
            )


def crawl_evs(start_url: str = BASE_URL, max_pages: int = MAX_PAGES) -> None:
    """
    Prosty crawler przechodzący po wszystkich wewnętrznych stronach EVS Explore,
    zaczynając od strony powitalnej.
    """
    visited: set[str] = set()
    queue: deque[str] = deque([start_url])
    index_records: list[dict] = []

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        try:
            html = fetch_html(url)
        except Exception as exc:
            # zapisujemy informację o nieudanej próbie w indeksie
            index_records.append(
                {
                    "url": url,
                    "title": f"ERROR: {exc}",
                    "headings": [],
                    "links": [],
                }
            )
            visited.add(url)
            continue

        parsed = parse_page(html, url)
        save_page_assets(url, html, parsed)
        index_records.append(parsed)
        visited.add(url)

        for link in parsed["links"]:
            if link not in visited:
                queue.append(link)

    # indeks wszystkich odwiedzonych stron
    write_index_csv(index_records, OUT_DIR / "evs_pages_index.csv")


def main() -> None:
    crawl_evs()


if __name__ == "__main__":
    main()


