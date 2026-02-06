#!/usr/bin/env python3
"""
Convert the Markdown ICD-10-CM tabular list into a simple CSV file
with columns: code, description.

We parse the already-extracted text from:
    nlm/docs/icd10cm-tabular-2022-April-1.md
so that everything działa wewnątrz Cursora bez parsowania PDF.
"""

import csv
import re
from pathlib import Path


CODE_RE = re.compile(r"^([A-Z]\d{2}(?:\.[A-Z0-9]{1,4})?)\s+(.+)$")


def extract_codes_from_md(md_path: Path) -> list[dict[str, str]]:
    """
    Bardzo prosty parser:
    - bierzemy linie zaczynające się od wzorca kodu ICD-10,
    - opis to tekst po kodzie w tej samej linii.

    Dzięki temu dostajemy czystą tabelę code -> short description.
    """
    codes: list[dict[str, str]] = []

    with md_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            m = CODE_RE.match(line)
            if not m:
                continue

            code = m.group(1).strip()
            desc = m.group(2).strip()

            # Odfiltruj zakresy typu "A00-A09"
            if "-" in code:
                continue

            codes.append({"code": code, "description": desc})

    return codes


def main() -> None:
    md_path = Path("nlm/docs/icd10cm-tabular-2022-April-1.md")
    out_csv = Path("icd10cm-tabular-2022-from-md.csv")

    if not md_path.exists():
        raise SystemExit(f"Nie znaleziono pliku Markdown: {md_path}")

    print(f"Czytam {md_path}...")
    codes = extract_codes_from_md(md_path)
    print(f"Znalazłem {len(codes)} kodów ICD-10.")

    print(f"Zapisuję CSV do {out_csv}...")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["code", "description"])
        writer.writeheader()
        for row in codes:
            writer.writerow(row)

    print("Gotowe.")


if __name__ == "__main__":
    main()

