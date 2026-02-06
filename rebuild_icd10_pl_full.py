#!/usr/bin/env python3
"""
Zbuduj pełny plik icd10cm-tabular-2022_PL.csv na podstawie:
- icd10cm-tabular-2022.csv       (angielska wersja, komplet kodów)
- icd10cm-tabular-2022_PL.csv   (częściowo przetłumaczona wersja)

Wynik:
- nadpisany icd10cm-tabular-2022_PL.csv z WSZYSTKIMI kodami.
  Jeśli dla kodu istnieje polskie tłumaczenie, używamy go,
  w przeciwnym razie wstawiamy opis angielski jako description_pl.
"""

import csv
from pathlib import Path


def main() -> None:
    src_en = Path("icd10cm-tabular-2022.csv")
    src_pl_partial = Path("icd10cm-tabular-2022_PL.csv")

    if not src_en.exists():
        raise SystemExit(f"Brak pliku źródłowego EN: {src_en}")

    # Wczytaj już przetłumaczone kody (jeśli plik istnieje)
    existing_pl: dict[str, str] = {}
    if src_pl_partial.exists():
        with src_pl_partial.open("r", encoding="utf-8") as f_pl:
            reader_pl = csv.DictReader(f_pl)
            for row in reader_pl:
                code = (row.get("code") or "").strip()
                desc_pl = (row.get("description_pl") or "").strip()
                if code:
                    existing_pl[code] = desc_pl

    print(f"Załadowano {len(existing_pl)} istniejących tłumaczeń PL.")

    # Zbuduj nowy, kompletny plik PL
    tmp_out = Path("icd10cm-tabular-2022_PL_full.tmp.csv")
    with src_en.open("r", encoding="utf-8") as f_en, tmp_out.open(
        "w", newline="", encoding="utf-8"
    ) as f_out:
        reader_en = csv.DictReader(f_en)
        fieldnames = ["code", "description_pl"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        count_total = 0
        count_from_pl = 0
        count_from_en = 0

        for row in reader_en:
            code = (row.get("code") or "").strip()
            desc_en = (row.get("description") or "").strip()
            if not code:
                continue

            if code in existing_pl and existing_pl[code]:
                desc_pl = existing_pl[code]
                count_from_pl += 1
            else:
                desc_pl = desc_en  # fallback: póki co opis angielski
                count_from_en += 1

            writer.writerow({"code": code, "description_pl": desc_pl})
            count_total += 1

    # Podmień stary plik PL nowym, kompletnym
    tmp_out.replace(src_pl_partial)

    print(
        f"Gotowe. Łącznie zapisano {count_total} kodów; "
        f"{count_from_pl} z istniejących tłumaczeń PL, "
        f"{count_from_en} z opisem EN jako fallback."
    )


if __name__ == "__main__":
    main()

