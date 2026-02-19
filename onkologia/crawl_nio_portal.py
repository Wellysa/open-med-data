"""
crawl_nio_portal.py

Crawler portalu Narodowego Instytutu Onkologii (NIO) – https://nio.gov.pl

- Startuje od strony głównej i podąża za linkami w obrębie domeny nio.gov.pl
- Zapisuje treść każdej strony jako Markdown pod: onkologia/nio-portal/pages/<path>.md
- Co 10 minut wypisuje status: liczba zapisanych stron, rozmiar kolejki, upływający czas

Zależności: pip install requests beautifulsoup4
Użycie: python crawl_nio_portal.py
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Iterable, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://nio.gov.pl"
START_URLS = [
    "https://nio.gov.pl/",
    "https://nio.gov.pl/pacjenci-i-bliscy",
    "https://nio.gov.pl/profilaktyka-i-edukacja",
    "https://nio.gov.pl/nauka-i-ksztalcenie",
    "https://nio.gov.pl/instytut",
    "https://nio.gov.pl/kontakt",
]

OUTPUT_ROOT = Path(__file__).resolve().parent / "nio-portal" / "pages"

REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.5
MAX_PAGES = 4000
STATUS_INTERVAL_SEC = 600  # 10 minut


def same_site(url: str) -> bool:
    p = urlparse(url)
    base_netloc = urlparse(BASE_URL).netloc
    return p.netloc == base_netloc and p.scheme in ("http", "https")


def normalize_url(url: str) -> str:
    p = urlparse(url)
    p = p._replace(fragment="", query="")
    url2 = p.geturl()
    if url2.endswith("/") and url2.rstrip("/") != BASE_URL:
        url2 = url2.rstrip("/")
    return url2


def url_to_path(url: str) -> Path:
    p = urlparse(url)
    path = (p.path or "/").strip("/") or "index"
    parts = path.split("/")
    if not parts or parts == ["index"]:
        return OUTPUT_ROOT / "index.md"
    if len(parts) == 1:
        return OUTPUT_ROOT / parts[0] / "index.md"
    *dirs, last = parts
    return OUTPUT_ROOT.joinpath(*dirs) / f"{last}.md"


def clean_html_to_markdownish(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find(id="main") or soup.find(role="main") or soup.find("main") or soup.body
    if main is None:
        main = soup
    for tag_name in ("script", "style", "nav", "footer", "noscript", "header"):
        for t in main.find_all(tag_name):
            t.decompose()
    for level in [1, 2, 3]:
        for h in main.find_all(f"h{level}"):
            text = h.get_text(strip=True)
            if not text:
                h.decompose()
                continue
            h.replace_with(f"\n{'#' * level} {text}\n")
    for a in main.find_all("a"):
        href = a.get("href")
        text = a.get_text(strip=True)
        if href:
            full = urljoin(base_url, href)
            a.replace_with(f"[{text}]({full})" if text else f"<{full}>")
        else:
            a.replace_with(text)
    for img in main.find_all("img"):
        alt = img.get("alt") or ""
        src = img.get("src")
        full = urljoin(base_url, src) if src else ""
        img.replace_with(f"![{alt}]({full})" if full else f"![{alt}]")
    text = main.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_links(html: str, base_url: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        abs_url = urljoin(base_url, href)
        if not same_site(abs_url):
            continue
        yield abs_url


def crawl() -> None:
    session = requests.Session()
    session.headers.setdefault(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    visited: Set[str] = set()
    to_visit: Set[str] = {normalize_url(u) for u in START_URLS if same_site(u)}
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    start_time = time.monotonic()
    last_status_time = start_time
    pages_saved = 0

    while to_visit and pages_saved < MAX_PAGES:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        now = time.monotonic()
        if now - last_status_time >= STATUS_INTERVAL_SEC:
            elapsed_min = (now - start_time) / 60
            print(f"\n[NIO] === Status ({elapsed_min:.0f} min) === zapisane: {pages_saved}, kolejka: {len(to_visit)}, odwiedzono: {len(visited)}")
            last_status_time = now

        print(f"[NIO] Fetching {url}")
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as e:
            print(f"  ! Błąd: {e}")
            continue

        content_type = (resp.headers.get("Content-Type") or "").lower()
        out_path = url_to_path(url)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Jeśli to nie HTML (np. obraz/PDF), zapisz tylko metadane i URL.
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            header = (
                f"# {url}\n\n"
                f"(Snapshot z portalu NIO, crawl_nio_portal.py)\n\n"
                f"Content-Type: {content_type or 'unknown'}\n\n"
                f"To jest zasób binarny; nie parsuję HTML.\n"
            )
            out_path.write_text(header, encoding="utf-8")
        else:
            try:
                html = resp.text
                content = clean_html_to_markdownish(html, BASE_URL)
            except Exception as e:
                print(f"  ! Błąd parsera HTML: {e}")
                content = resp.text
            header = f"# {url}\n\n(Snapshot z portalu NIO, crawl_nio_portal.py)\n\n"
            out_path.write_text(header + content + "\n", encoding="utf-8")
        pages_saved += 1
        rel = out_path.relative_to(OUTPUT_ROOT.parent)
        print(f"  -> {rel}")

        for link in extract_links(html, url):
            norm = normalize_url(link)
            if norm not in visited:
                to_visit.add(norm)

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    elapsed = (time.monotonic() - start_time) / 60
    print(f"\n[NIO] Koniec. Zapisano {pages_saved} stron w {elapsed:.1f} min (limit {MAX_PAGES}).")


def main() -> None:
    crawl()


if __name__ == "__main__":
    main()
