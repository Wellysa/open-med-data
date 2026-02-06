"""
download_loinc_kb.py

Simple scraper for the LOINC Knowledge Base (`https://loinc.org/kb`).

It crawls all pages under `/kb/` (respecting the same host and path prefix)
and saves them as Markdown-ish text files under `loinc/kb/full/`,
mirroring the URL structure.

Requirements:
    pip install requests beautifulsoup4

Usage:
    python download_loinc_kb.py
"""

import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://loinc.org"
KB_ROOT = "https://loinc.org/kb/"

# Output dir is relative to this script location
OUTPUT_ROOT = Path(__file__).resolve().parent / "kb" / "full"

# Basic polite crawling settings
REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.5  # seconds


def is_kb_url(url: str) -> bool:
    """Return True if URL is within the LOINC Knowledge Base (/kb/)."""
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in ("http", "https"):
        return False
    if parsed.netloc != urlparse(BASE_URL).netloc:
        return False

    # Only keep /kb/ paths (including nested)
    return parsed.path.startswith("/kb/")


def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments and trailing slashes."""
    parsed = urlparse(url)
    # strip fragment and query
    parsed = parsed._replace(fragment="", query="")
    normalized = parsed.geturl()
    # remove trailing slash (except for root /kb/)
    if normalized.endswith("/") and normalized != KB_ROOT.rstrip("/"):
        normalized = normalized.rstrip("/")
    return normalized


def url_to_path(url: str) -> Path:
    """
    Map a KB URL to a local file path under OUTPUT_ROOT.

    Examples:
        https://loinc.org/kb -> kb/full/index.md
        https://loinc.org/kb/users-guide -> kb/full/users-guide/index.md
        https://loinc.org/kb/users-guide/introduction ->
            kb/full/users-guide/introduction.md
    """
    parsed = urlparse(url)
    path = parsed.path

    # Strip leading '/kb'
    if path.startswith("/kb"):
        path_rel = path[len("/kb") :]
    else:
        path_rel = path

    if not path_rel or path_rel == "/":
        # Root KB page
        return OUTPUT_ROOT / "index.md"

    # Drop leading '/'
    if path_rel.startswith("/"):
        path_rel = path_rel[1:]

    parts = path_rel.split("/")

    if len(parts) == 1:
        # e.g. /kb/faq -> faq/index.md
        return OUTPUT_ROOT / parts[0] / "index.md"

    # e.g. /kb/users-guide/introduction -> users-guide/introduction.md
    *dirs, last = parts
    return OUTPUT_ROOT.joinpath(*dirs) / f"{last}.md"


def extract_main_content(html: str) -> str:
    """
    Extract the human-readable content from a KB page and return as plain text.

    For now we keep it simple: take the main body text and headings, remove
    navigation chrome as best as we can, and return text with basic spacing.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Many KB pages have their main content inside an element with id "main"
    # or within an article. Fall back to <body>.
    main = soup.find(id="main") or soup.find("article") or soup.body
    if main is None:
        main = soup

    # Remove scripts/styles/nav/footers to reduce noise.
    for tag_name in ("script", "style", "nav", "footer", "noscript", "header"):
        for t in main.find_all(tag_name):
            t.decompose()

    # Convert links to "text (URL)" format to preserve destinations.
    for a in main.find_all("a"):
        href = a.get("href")
        text = a.get_text(strip=True)
        if href:
            full = urljoin(BASE_URL, href)
            a.replace_with(f"{text} ({full})" if text else full)
        else:
            a.replace_with(text)

    # Get text with reasonable separators.
    text = main.get_text(separator="\n", strip=True)

    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def fetch(url: str) -> str:
    """Fetch URL and return HTML text."""
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def crawl_kb(seed_urls=None):
    """
    Crawl the LOINC KB starting from KB_ROOT and optional extra seeds.

    Saves each page to OUTPUT_ROOT mirroring the URL structure.
    """
    if seed_urls is None:
        seed_urls = [KB_ROOT]

    visited = set()
    to_visit = {normalize_url(u) for u in seed_urls if is_kb_url(u)}

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    session = requests.Session()

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        print(f"[KB] Fetching {url}")
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as e:
            print(f"  ! Error fetching {url}: {e}")
            continue

        html = resp.text
        text = extract_main_content(html)

        out_path = url_to_path(url)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            f"# {url}\n\n"
            f"(Snapshot from LOINC Knowledge Base, downloaded by download_loinc_kb.py)\n\n"
            f"{text}\n",
            encoding="utf-8",
        )
        print(f"  -> Saved to {out_path.relative_to(OUTPUT_ROOT.parent)}")

        # Discover more KB links on the page.
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            abs_url = urljoin(url, href)
            if not is_kb_url(abs_url):
                continue
            norm = normalize_url(abs_url)
            if norm not in visited:
                to_visit.add(norm)

        time.sleep(SLEEP_BETWEEN_REQUESTS)


def main():
    # Start from the main KB entry point; the crawler will follow internal links.
    crawl_kb(seed_urls=[KB_ROOT])


if __name__ == "__main__":
    main()

