#!/usr/bin/env python3
"""
Translate ICD-10 descriptions from English to Polish.

Input:  icd10cm-tabular-2022.csv  (columns: code, description)
Output: icd10cm-tabular-2022_PL.csv  (columns: code, description_pl)
"""

import csv
import sys
import time
from pathlib import Path


def count_existing_rows(path: Path) -> int:
    """Zwraca liczbę już zapisanych wierszy (bez nagłówka) w pliku PL."""
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8") as f:
        # Odejmujemy 1 za wiersz nagłówka, jeśli plik nie jest pusty
        lines = sum(1 for _ in f)
    return max(0, lines - 1)


def main() -> None:
    try:
        from deep_translator import GoogleTranslator  # type: ignore
    except ImportError:
        print("Installing deep-translator...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator"])
        from deep_translator import GoogleTranslator  # type: ignore

    src_csv = Path("icd10cm-tabular-2022.csv")
    out_csv = Path("icd10cm-tabular-2022_PL.csv")

    if not src_csv.exists():
        raise SystemExit(f"Nie znaleziono pliku wejściowego: {src_csv}")

    translator = GoogleTranslator(source="en", target="pl")

    already_done = count_existing_rows(out_csv)
    if already_done > 0:
        print(f"Znaleziono istniejący plik wyjściowy z {already_done} wierszami – wznawiam od kolejnego.")

    print(f"Czytam {src_csv}...")
    with src_csv.open("r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)

        # Jeśli plik PL nie istnieje, tworzymy go z nagłówkiem,
        # jeśli istnieje – dopisujemy bez ponownego nagłówka.
        mode = "a" if out_csv.exists() else "w"
        with out_csv.open(mode, newline="", encoding="utf-8") as f_out:
            fieldnames = ["code", "description_pl"]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)

            if mode == "w":
                writer.writeheader()

            for idx, row in enumerate(reader, start=1):
                # Pomijamy wiersze, które już zostały przetłumaczone
                if idx <= already_done:
                    continue

            code = (row.get("code") or "").strip()
            desc_en = (row.get("description") or "").strip()

                if not code:
                    continue

                if not desc_en:
                    desc_pl = ""
                else:
                    # Kilka prób tłumaczenia, żeby nie przerywać całego procesu
                    attempts = 0
                    while True:
                        try:
                            desc_pl = translator.translate(desc_en)
                            break
                        except Exception as e:  # pragma: no cover - network/runtime errors
                            attempts += 1
                            if attempts >= 3:
                                print(
                                    f"\nBłąd tłumaczenia wiersza {idx} ({code}) "
                                    f"po {attempts} próbach: {e} – zostawiam tekst po angielsku."
                                )
                                desc_pl = desc_en  # fallback: zostaw po angielsku
                                break
                            # Krótkie opóźnienie i ponowna próba
                            print(f"\nProblem z tłumaczeniem wiersza {idx} ({code}), próba {attempts} – czekam i próbuję ponownie...")
                            time.sleep(2.0)

                writer.writerow({"code": code, "description_pl": desc_pl})

                if idx % 100 == 0:
                    print(f"Przetłumaczono {idx} wierszy (łącznie w źródłowym CSV).")

    print(f"Gotowe. Zapisano: {out_csv}")


if __name__ == "__main__":
    main()

