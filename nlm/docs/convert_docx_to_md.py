from pathlib import Path


def docx_to_markdown_text(docx_path: Path) -> str:
    """Prosta konwersja: każdy akapit jako osobna linia w Markdown."""
    try:
        from docx import Document  # type: ignore
    except ImportError:
        raise SystemExit(
            "Brak biblioteki 'python-docx'. Zainstaluj ją poleceniem:\n"
            "    pip install python-docx\n"
        )

    doc = Document(str(docx_path))
    lines: list[str] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        lines.append(text)

    return "\n\n".join(lines) + "\n"


def convert_all_docx_in_folder(folder: Path) -> None:
    targets = [
        "index_2020_v2.docx",
        "icd10cm-tabular-2022-April-1.docx",
    ]

    for name in targets:
        docx_path = folder / name
        if not docx_path.exists():
            print(f"Pomijam (brak pliku): {name}")
            continue

        md_path = docx_path.with_suffix(".md")
        print(f"Konwertuję {docx_path.name} -> {md_path.name}")
        md_text = docx_to_markdown_text(docx_path)
        md_path.write_text(md_text, encoding="utf-8")

    print("Gotowe (konwersja DOCX -> MD).")


if __name__ == "__main__":
    base_folder = Path(__file__).resolve().parent
    convert_all_docx_in_folder(base_folder)

