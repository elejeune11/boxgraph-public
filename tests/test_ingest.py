"""Ingest: a PDF becomes per-page text (and images) that citations are checked against."""

import json
import shutil
from pathlib import Path

import pytest

from boxgraph.ingest import ingest

CORPUS = Path(__file__).parents[1] / "corpus"
PDF = CORPUS / "2004_Erdmann.pdf"

needs_pdf = pytest.mark.skipif(not PDF.exists() or not shutil.which("pdftotext"), reason="needs corpus PDF and poppler")


@needs_pdf
def test_ingest_writes_text_per_page(tmp_path):
    """Ingest writes one text file per PDF page."""
    d = ingest(PDF, "erdmann2004", tmp_path, images=False)
    meta = json.loads((d / "ingest.json").read_text())
    assert meta["pages"] == 4
    assert (d / "text" / "page-001.txt").read_text().count("Erdmann") >= 1
    assert len(list((d / "text").glob("page-*.txt"))) == 4


@needs_pdf
def test_ingest_page_range_and_images(tmp_path):
    """Ingest honours a page range and renders page images."""
    d = ingest(PDF, "e", tmp_path, pages=(2, 3), images=True, dpi=40)
    meta = json.loads((d / "ingest.json").read_text())
    assert meta["page_range"] == [2, 3]
    assert sorted(p.name for p in (d / "text").glob("*.txt")) == ["page-002.txt", "page-003.txt"]
    assert sorted(p.name for p in (d / "pages").glob("*.png")) == ["page-002.png", "page-003.png"]


@needs_pdf
def test_ingest_never_overwrites_an_authored_record(tmp_path):
    """Re-ingesting never touches authored files."""
    d = ingest(PDF, "e", tmp_path, images=False)
    (d / "source.yaml").write_text("id: e\n")
    ingest(PDF, "e", tmp_path, images=False)
    assert (d / "source.yaml").read_text() == "id: e\n"


def test_missing_pdf(tmp_path):
    """A missing PDF is an error."""
    with pytest.raises(FileNotFoundError):
        ingest(tmp_path / "nope.pdf", "x", tmp_path)
