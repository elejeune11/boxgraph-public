"""Add a paper to the corpus list.

  python -m pipeline.add path/to/Paper.pdf --id smith2015 [--pages 1-12] [--note "..."] [--relate-with bell1978]

Copies the PDF into corpus/ if it is elsewhere, checks the entry, and appends
it to pipeline/papers.yaml. Then run the pipeline for it:

  python -m pipeline.run_papers --papers smith2015
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from pipeline.corpus import add_paper

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--id", required=True, help="record id, e.g. smith2015 (lower case, letters, digits, _)")
    ap.add_argument("--pages", help="first-last PDF pages that belong to the paper (default: all)")
    ap.add_argument("--note", default="", help="what the reader should know about the file")
    ap.add_argument("--relate-with", default="", help="comma-separated record ids to relate it to")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    pdf = Path(a.pdf).resolve()
    if not pdf.is_file():
        print(f"no such file: {pdf}")
        return 1
    corpus = root / "corpus"
    if corpus not in pdf.parents:
        corpus.mkdir(exist_ok=True)
        dest = corpus / pdf.name
        if dest.exists():
            print(f"{dest} already exists; rename the PDF or remove the old one")
            return 1
        shutil.copy2(pdf, dest)
        pdf = dest
    pages = tuple(int(x) for x in a.pages.split("-")) if a.pages else None
    try:
        e = add_paper(root / "pipeline" / "papers.yaml", root, pdf, a.id, pages=pages, note=a.note,
                      relate_with=[x for x in a.relate_with.split(",") if x])
    except ValueError as err:
        print(f"not added: {err}")
        return 1
    print(f"added {e['id']}: {e['file']} pages {e['pages'][0]}-{e['pages'][1]}")
    print(f"next: python -m pipeline.run_papers --plan --papers {e['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
