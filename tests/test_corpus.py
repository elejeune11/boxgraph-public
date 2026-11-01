"""The corpus list and the ledger of finished jobs (pipeline/corpus.py).

Adding papers must fail early on a bad entry, and work already done must
not be redone on another machine: the ledger is committed with the records."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from pipeline.corpus import add_paper, check_papers, load_completed, load_papers, record_completed

needs_poppler = pytest.mark.skipif(shutil.which("pdfinfo") is None, reason="needs poppler")
ROOT = Path(__file__).resolve().parents[1]


def _pdf(path: Path, pages: int = 3) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(path) as pdf:
        for i in range(pages):
            fig = plt.figure()
            fig.text(0.5, 0.5, f"page {i + 1}")
            pdf.savefig(fig)
            plt.close(fig)
    return path


@needs_poppler
def test_a_sound_corpus_list_has_no_errors(tmp_path):
    """Entries with a unique id, an existing PDF and a page range inside it pass the check."""
    _pdf(tmp_path / "corpus" / "a.pdf")
    ps = [{"id": "smith2015", "file": "corpus/a.pdf", "pages": [1, 3]}]
    assert check_papers(ps, tmp_path) == []


@needs_poppler
def test_bad_corpus_entries_are_named(tmp_path):
    """A duplicate or malformed id, a missing PDF, a page range outside the PDF and an unknown relate_with are each reported."""
    _pdf(tmp_path / "corpus" / "a.pdf")
    ps = [{"id": "smith2015", "file": "corpus/a.pdf", "pages": [1, 3]},
          {"id": "smith2015", "file": "corpus/a.pdf", "pages": [1, 3]},
          {"id": "Bad-Id", "file": "corpus/a.pdf", "pages": [1, 3]},
          {"id": "lee2019", "file": "corpus/missing.pdf", "pages": [1, 2]},
          {"id": "kim2020", "file": "corpus/a.pdf", "pages": [2, 9]},
          {"id": "wu2021", "file": "corpus/a.pdf", "pages": [1, 3], "relate_with": ["nobody"]}]
    errs = check_papers(ps, tmp_path)
    for word in ("duplicate", "Bad-Id", "missing.pdf", "2-9", "nobody"):
        assert any(word in e for e in errs), (word, errs)


@needs_poppler
def test_adding_a_paper_appends_a_checked_entry(tmp_path):
    """add_paper appends an entry with the PDF's full page range by default and keeps the file's comments."""
    _pdf(tmp_path / "corpus" / "a.pdf", pages=4)
    pf = tmp_path / "papers.yaml"
    pf.write_text("# the corpus\n- id: old2000\n  file: corpus/a.pdf\n  pages: [1, 4]\n")
    e = add_paper(pf, tmp_path, tmp_path / "corpus" / "a.pdf", "new2020", note="a cover page first")
    assert e == {"id": "new2020", "file": "corpus/a.pdf", "pages": [1, 4], "note": "a cover page first"}
    text = pf.read_text()
    assert text.startswith("# the corpus") and [p["id"] for p in load_papers(pf)] == ["old2000", "new2020"]
    assert "- id: new2020\n  file: corpus/a.pdf\n  pages: [1, 4]\n" in text  # written as people write it
    with pytest.raises(ValueError, match="duplicate"):
        add_paper(pf, tmp_path, tmp_path / "corpus" / "a.pdf", "new2020")
    assert [p["id"] for p in load_papers(pf)] == ["old2000", "new2020"]


@needs_poppler
def test_the_add_command_copies_a_pdf_into_the_corpus(tmp_path):
    """`python -m pipeline.add` copies a PDF from elsewhere into corpus/ and registers it."""
    src = _pdf(tmp_path / "elsewhere" / "Paper.pdf", pages=2)
    (tmp_path / "pipeline").mkdir()
    (tmp_path / "pipeline" / "papers.yaml").write_text("[]\n")
    r = subprocess.run([sys.executable, "-m", "pipeline.add", str(src), "--id", "new2020", "--root", str(tmp_path)],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "corpus" / "Paper.pdf").exists()
    assert load_papers(tmp_path / "pipeline" / "papers.yaml")[0]["file"] == "corpus/Paper.pdf"


def test_the_ledger_records_finished_jobs_and_merges(tmp_path):
    """Finished jobs are written to the ledger sorted by id; a later write adds to it and updates a job run again."""
    f = tmp_path / "completed.yaml"
    assert load_completed(f) == {}
    record_completed(f, [{"job": "read:b", "date": "2026-10-30", "cost_usd": 3.0},
                         {"job": "audit:b", "date": "2026-10-30", "cost_usd": 1.0}])
    record_completed(f, [{"job": "read:b", "date": "2026-10-31", "cost_usd": 4.0},
                         {"job": "read:a", "date": "2026-10-31", "cost_usd": 2.0}])
    got = load_completed(f)
    assert list(got) == ["audit:b", "read:a", "read:b"] and got["read:b"]["date"] == "2026-10-31"
    assert [r["job"] for r in yaml.safe_load(f.read_text())] == ["audit:b", "read:a", "read:b"]


def test_the_repository_ledger_covers_the_corpus_already_read():
    """The committed ledger lists every per-paper job of every committed record, so a fresh clone does not redo them."""
    r = subprocess.run(["git", "ls-files", "records"], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        pytest.skip("not a git checkout")
    committed = {f.split("/")[1] for f in r.stdout.splitlines() if f.endswith("/source.yaml")}
    done = load_completed(ROOT / "pipeline" / "completed.yaml")
    for p in load_papers(ROOT / "pipeline" / "papers.yaml"):
        if p["id"] in committed:  # a record still being read is not committed yet
            from pipeline.run_papers import stages_of

            for stage in stages_of(p):  # a paper: read, audit, digitize; its released code or data: read
                assert f"{stage}:{p['id']}" in done, (stage, p["id"])


def test_the_ledger_is_written_whole_or_not_at_all(tmp_path, monkeypatch):
    """The ledger is replaced in one step, so a run killed while writing it never leaves it cut short."""
    import os

    f = tmp_path / "completed.yaml"
    record_completed(f, [{"job": "read:a", "date": "2026-10-31", "cost_usd": 1.0}])
    calls = []
    real = os.replace
    monkeypatch.setattr(os, "replace", lambda a, b: calls.append((a, b)) or real(a, b))
    record_completed(f, [{"job": "read:b", "date": "2026-10-31", "cost_usd": 1.0}])
    assert calls and Path(calls[0][1]) == f and sorted(load_completed(f)) == ["read:a", "read:b"]


def test_code_and_data_entries_are_checked_too(tmp_path):
    """A software entry names a folder, a dataset entry a file, and each names papers in the list; no page range."""
    _pdf(tmp_path / "corpus" / "a.pdf")
    (tmp_path / "corpus" / "code" / "smith_code").mkdir(parents=True)
    (tmp_path / "corpus" / "code" / "smith_code" / "run.m").write_text("x = 1;\n")
    ps = [{"id": "smith2015", "file": "corpus/a.pdf", "pages": [1, 3]},
          {"id": "smith_code", "kind": "software", "file": "corpus/code/smith_code", "papers": ["smith2015"]},
          {"id": "smith_data", "kind": "dataset", "file": "corpus/data/missing.xlsx", "papers": ["nobody"]},
          {"id": "odd", "kind": "poster", "file": "corpus/a.pdf"}]
    errs = check_papers(ps, tmp_path)
    assert not any("smith_code" in e for e in errs), errs
    assert any("missing.xlsx" in e for e in errs) and any("nobody" in e for e in errs) and any("poster" in e for e in errs)


def test_the_attach_command_registers_code_and_data_safely(tmp_path):
    """`python -m pipeline.attach` copies code (a zip or a folder) or data into corpus/ and lists it with its papers;
    a zip whose paths leave its folder is refused."""
    import zipfile

    (tmp_path / "pipeline").mkdir()
    _pdf(tmp_path / "corpus" / "a.pdf")
    (tmp_path / "pipeline" / "papers.yaml").write_text("- {id: smith2015, file: corpus/a.pdf, pages: [1, 3]}\n")
    z = tmp_path / "up" / "code.zip"
    z.parent.mkdir()
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("smith_code/run.m", "x = 1;\n")
        f.writestr("__MACOSX/._run.m", "junk")
    run = [sys.executable, "-m", "pipeline.attach"]
    r = subprocess.run([*run, str(z), "--id", "smith_code", "--kind", "software", "--papers", "smith2015",
                        "--root", str(tmp_path)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "corpus" / "code" / "smith_code" / "run.m").exists()
    assert not (tmp_path / "corpus" / "code" / "smith_code" / "__MACOSX").exists()
    e = load_papers(tmp_path / "pipeline" / "papers.yaml")[-1]
    assert e == {"id": "smith_code", "kind": "software", "file": "corpus/code/smith_code", "papers": ["smith2015"]}
    bad = tmp_path / "up" / "bad.zip"
    with zipfile.ZipFile(bad, "w") as f:
        f.writestr("../escape.txt", "x")
    r = subprocess.run([*run, str(bad), "--id", "bad_code", "--kind", "software", "--papers", "smith2015",
                        "--root", str(tmp_path)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode != 0 and not (tmp_path / "escape.txt").exists()
    x = tmp_path / "up" / "data.xlsx"
    x.write_bytes(b"PK")
    r = subprocess.run([*run, str(x), "--id", "smith_data", "--kind", "dataset", "--papers", "smith2015",
                        "--root", str(tmp_path)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0 and (tmp_path / "corpus" / "data" / "smith_data.xlsx").exists()


def test_missing_sources_lists_what_a_fresh_clone_lacks_and_where_to_get_it(tmp_path):
    """The sources whose files are not under corpus/ are listed with the DOI or URL their record gives, so a fresh clone knows what to fetch."""
    from pipeline.corpus import missing_sources

    (tmp_path / "corpus" / "code" / "here_code").mkdir(parents=True)
    rec = tmp_path / "records"
    for rid, extra in (("gone", "doi: 10.1000/xyz\n"), ("gone_code", "url: https://example.org/code\n"), ("here_code", "")):
        (rec / rid).mkdir(parents=True)
        (rec / rid / "source.yaml").write_text(f"id: {rid}\nkind: article\ntitle: {rid} title\n{extra}")
    papers = [{"id": "gone", "file": "corpus/gone.pdf", "pages": [1, 2]},
              {"id": "gone_code", "kind": "software", "file": "corpus/code/gone_code", "papers": ["gone"]},
              {"id": "here_code", "kind": "software", "file": "corpus/code/here_code", "papers": ["gone"]}]
    out = missing_sources(papers, tmp_path, tmp_path / "records")
    assert [m["id"] for m in out] == ["gone", "gone_code"]
    assert out[0]["where"] == "https://doi.org/10.1000/xyz" and out[0]["file"] == "corpus/gone.pdf"
    assert out[1]["where"] == "https://example.org/code" and out[1]["title"] == "gone_code title"
