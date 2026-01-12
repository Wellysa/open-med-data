from pathlib import Path


def convert_selected_pdfs(folder: Path) -> None:
    """
    Konwertuje wybrane pliki PDF w danym folderze do DOCX.
    Na razie konwertujemy tylko mniejszy plik `index_2020_v2.pdf`,
    żeby uniknąć bardzo długiej konwersji ogromnego pliku tablicowego.
    """
    try:
        from pdf2docx import Converter  # type: ignore
    except ImportError:
        print(
            "Brak biblioteki 'pdf2docx'. Zainstaluj ją poleceniem:\n"
            "    pip install pdf2docx\n"
        )
        return

    target_name = "index_2020_v2.pdf"
    pdf_path = folder / target_name

    if not pdf_path.exists():
        print(f"Nie znaleziono pliku {target_name} w folderze {folder}")
        return

    docx_path = pdf_path.with_suffix(".docx")
    print(f"Konwertuję {pdf_path.name} -> {docx_path.name}")

    cv = Converter(str(pdf_path))
    cv.convert(str(docx_path))
    cv.close()

    print("Gotowe.")


if __name__ == "__main__":
    base_folder = Path(__file__).resolve().parent
    convert_selected_pdfs(base_folder)

from pathlib import Path


def convert_all_pdfs_to_docx(folder: Path) -> None:
    try:
        from pdf2docx import Converter  # type: ignore
    except ImportError:
        print(
            "Brak biblioteki 'pdf2docx'. Zainstaluj ją poleceniem:\n"
            "    pip install pdf2docx\n"
        )
        return

    pdf_files = list(folder.glob("*.pdf"))
    if not pdf_files:
        print("Brak plików PDF w folderze:", folder)
        return

    for pdf in pdf_files:
        docx_path = pdf.with_suffix(".docx")
        print(f"Konwertuję {pdf.name} -> {docx_path.name}")
        cv = Converter(str(pdf))
        cv.convert(str(docx_path))
        cv.close()

    print("Gotowe.")


if __name__ == "__main__":
    base_folder = Path(__file__).resolve().parent
    convert_all_pdfs_to_docx(base_folder)

