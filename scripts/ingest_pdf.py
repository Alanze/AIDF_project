from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.app.ingestion.pdf_loader import extract_pages


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract page-level text from the insurance PDF.")
    parser.add_argument("--input", default="data/raw/FLEXI-ULife Prime Saver.pdf")
    parser.add_argument("--output", default="data/processed/pdf_pages.tmp.json")
    args = parser.parse_args()

    pages = extract_pages(args.input)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(pages)} pages to {output}")


if __name__ == "__main__":
    main()
