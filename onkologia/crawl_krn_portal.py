"""
crawl_krn_portal.py

Crawler portalu Krajowego Rejestru Nowotworów.

Zakres:
- Startuje od kilku stron wejściowych (strona główna, nowotwory, baza wiedzy, raporty)
- Podąża za linkami w obrębie domeny `onkologia.org.pl` i ścieżki `/pl`
- Zapisuje treść każdej strony jako plik Markdown‑owy pod:

    onkologia/krn-portal/pages/<path>.md

  np.:
    https://onkologia.org.pl/pl       -> pages/index.md
    https://onkologia.org.pl/pl/raporty -> pages/raporty/index.md
    https://onkologia.org.pl/pl/nowotwory-pluca-i-oplucnej-czym-sa
        -> pages/nowotwory-pluca-i-oplucnej-czym-sa.md

Zależności:
    pip install requests beautifulsoup4

Użycie:
    python crawl_krn_portal.py
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Iterable, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://onkologia.org.pl"
START_URLS = [
    "https://onkologia.org.pl/pl",
    "https://onkologia.org.pl/pl/nowotwory",
    "https://onkologia.org.pl/pl/baza-wiedzy-portalu",
    "https://onkologia.org.pl/pl/raporty",
]

OUTPUT_ROOT = Path(__file__).resolve().parent / "krn-portal" / "pages"

REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.5  # sekundy – bądźmy grzeczni
MAX_PAGES = 2000  # twardy limit bezpieczeństwa


def same_site(path: str) -> bool:
    """Zachowaj tylko ścieżki pod /pl (oraz ewentualne podstrony) na tej samej domenie."""
    # większość treści portalu jest pod /pl
    return path.startswith("/pl")


def normalize_url(url: str) -> str:
    """Uprość URL: usuń fragmenty, zapytania, trailing slash, ujednolić."""
    p = urlparse(url)
    p = p._replace(fragment="", query="")
    url2 = p.geturl()
    # usuwamy końcowe /, ale zostawiamy samo `/pl`
    if url2.endswith("/") and url2 not in (f"{BASE_URL}/pl", f"{BASE_URL}/pl/"):
        url2 = url2.rstrip("/")
    return url2


def url_to_path(url: str) -> Path:
    """
    Zamapuj URL na ścieżkę pliku Markdown pod OUTPUT_ROOT.
    """
    p = urlparse(url)
    path = p.path

    # Spodziewamy się czegoś w rodzaju /pl/...; usuwamy wiodące /
    if path.startswith("/"):
        path = path[1:]

    # Jeśli to dokładnie /pl lub /pl/, traktuj jako index.md
    if path in ("pl", "pl/"):
        return OUTPUT_ROOT / "index.md"

    parts = path.split("/")

    # Jeśli ostatni segment jest pusty, to katalog -> index.md
    if not parts[-1]:
        parts = parts[:-1]

    # Jeśli mamy tylko "pl/<coś>", zdecyduj:
    if len(parts) == 2:
        # /pl/raporty -> raporty/index.md
        section = parts[1]
        return OUTPUT_ROOT / section / "index.md"

    # /pl/a/b/c -> a/b/c.md (bez wiodącego pl)
    if parts[0] == "pl":
        parts = parts[1:]

    *dirs, last = parts
    return OUTPUT_ROOT.joinpath(*dirs) / f"{last}.md"


def clean_html_to_markdownish(html: str, base_url: str) -> str:
    """
    Wyciągnij główną treść strony i zamień na prosty tekst Markdown‑owy.
    Nie próbujemy perfekcyjnego parsowania – ważne, żeby było czytelne.
    """
    soup = BeautifulSoup(html, "html.parser")

    # spróbuj znaleźć główny kontener (Drupal/Wordpress zwykle mają #main lub role=main)
    main = soup.find(id="main") or soup.find(role="main") or soup.find("main") or soup.body
    if main is None:
        main = soup

    # usuń powtarzalne elementy (nawigacja, stopka, skrypty)
    for tag_name in ("script", "style", "nav", "footer", "noscript", "header"):
        for t in main.find_all(tag_name):
            t.decompose()

    # zachowaj nagłówki h1-h3 jako Markdown
    for level in [1, 2, 3]:
        for h in main.find_all(f"h{level}"):
            text = h.get_text(strip=True)
            if not text:
                h.decompose()
                continue
            prefix = "#" * level
            h.replace_with(f"\n{prefix} {text}\n")

    # linki: tekst (URL)
    for a in main.find_all("a"):
        href = a.get("href")
        text = a.get_text(strip=True)
        if href:
            full = urljoin(base_url, href)
            repl = f"[{text}]({full})" if text else f"<{full}>"
            a.replace_with(repl)
        else:
            a.replace_with(text)

    # obrazy: zostaw tylko alt + src jako tekst
    for img in main.find_all("img"):
        alt = img.get("alt") or ""
        src = img.get("src")
        if src:
            full = urljoin(base_url, src)
            desc = f"![{alt}]({full})"
        else:
            desc = f"![{alt}]"
        img.replace_with(desc)

    text = main.get_text(separator="\n", strip=True)
    # uporządkuj puste linie
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_links(html: str, base_url: str) -> Iterable[str]:
    """Wyciągnij linki do dalszego crawlowania w obrębie /pl."""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # pomiń mailto, tel itp.
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        abs_url = urljoin(base_url, href)
        p = urlparse(abs_url)
        if p.netloc != urlparse(BASE_URL).netloc:
            continue
        if not same_site(p.path):
            continue
        yield abs_url


def crawl() -> None:
    session = requests.Session()
    visited: Set[str] = set()
    to_visit: Set[str] = {normalize_url(u) for u in START_URLS}

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    pages_count = 0

    while to_visit and pages_count < MAX_PAGES:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)
        pages_count += 1

        print(f"[KRN] Fetching {url}")
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as e:
            print(f"  ! Error fetching {url}: {e}")
            continue

        html = resp.text
        content = clean_html_to_markdownish(html, BASE_URL)

        out_path = url_to_path(url)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        header = f"# {url}\n\n(Snapshot from KRN portal, downloaded by crawl_krn_portal.py)\n\n"
        out_path.write_text(header + content + "\n", encoding="utf-8")
        rel = out_path.relative_to(OUTPUT_ROOT.parent)
        print(f"  -> Saved to {rel}")

        for link in extract_links(html, url):
            norm = normalize_url(link)
            if norm not in visited:
                to_visit.add(norm)

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print(f"[KRN] Done. Visited {len(visited)} pages (limit {MAX_PAGES}).")


def main() -> None:
    crawl()


if __name__ == "__main__":
    main()

