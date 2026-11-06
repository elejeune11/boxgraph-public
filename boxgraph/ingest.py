"""Ingest a PDF: per-page text for citation checks, page images for readers.

Writes, under records/<id>/:
  text/page-NNN.txt   text of each PDF page (1-based, absolute page numbers)
  pages/page-NNN.png  an image of each page (for equations OCR garbles)
  ingest.json         file, sha256, page count, page range
Never touches authored files (source.yaml, data.yaml, ...).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def _pages(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise RuntimeError(f"pdfinfo gave no page count for {pdf}")


def ingest(pdf: Path, sid: str, records_root: Path, pages: tuple[int, int] | None = None,
           images: bool = True, dpi: int = 110) -> Path:
    pdf = Path(pdf)
    if not pdf.exists():
        raise FileNotFoundError(pdf)
    for tool in ("pdfinfo", "pdftotext") + (("pdftoppm",) if images else ()):
        if shutil.which(tool) is None:
            raise RuntimeError(f"{tool} (poppler) is required")
    n = _pages(pdf)
    first, last = pages or (1, n)
    if not (1 <= first <= last <= n):
        raise ValueError(f"page range {first}-{last} outside 1-{n}")
    d = Path(records_root) / sid
    (d / "text").mkdir(parents=True, exist_ok=True)
    for p in range(first, last + 1):
        txt = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", str(pdf), "-"],
                             capture_output=True, text=True, check=True).stdout
        (d / "text" / f"page-{p:03d}.txt").write_text(txt)
    if images:
        (d / "pages").mkdir(exist_ok=True)
        for p in range(first, last + 1):
            stem = d / "pages" / f"page-{p:03d}"
            subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", str(dpi), "-png", "-singlefile",
                            str(pdf), str(stem)], check=True, capture_output=True)
    meta = {"file": pdf.name, "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pages": n,
            "page_range": [first, last], "dpi": dpi if images else None}
    (d / "ingest.json").write_text(json.dumps(meta, indent=1))
    return d
