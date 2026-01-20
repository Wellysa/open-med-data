from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    pdf_path = base_dir / "icd_o_3_pl.pdf"
    out_txt = base_dir / "content.txt"
    out_md = base_dir / "content.md"

    reader = PdfReader(str(pdf_path))

    with out_txt.open("w", encoding="utf-8") as ft, out_md.open("w", encoding="utf-8") as fm:
        fm.write("# ICD-O-3 (PL) — extracted text\n\n")
        fm.write("Source PDF: `icd_o_3_pl.pdf`\n\n")

        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            header = f"\n\n---\n\n## Page {i}\n\n"
            ft.write(header)
            ft.write(text)
            ft.write("\n")

            fm.write(header)
            fm.write("```\n")
            fm.write(text)
            fm.write("\n```\n")

    print(f"Pages: {len(reader.pages)}")
    print(f"Wrote: {out_txt}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()

