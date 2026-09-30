from pathlib import Path

import pdfplumber


def extract_pages(pdf_path: str) -> list[dict[str, object]]:
    path = Path(pdf_path)
    pages: list[dict[str, object]] = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            pages.append(
                {
                    "page": index,
                    "text": page.extract_text(x_tolerance=1, y_tolerance=3) or "",
                }
            )
    return pages
