"""Several corpora in one project: each with its own paper list, ledger, records, overview text,
build and run state, so two fields are reviewed side by side without mixing."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import pipeline.run_papers as rp
from pipeline.corpus import layout
from pipeline.orchestrator import snapshot, stray_writes

FX = Path(__file__).parent / "fixtures"


def test_the_default_corpus_keeps_the_original_paths(tmp_path):
    """Without a corpus name the paper list, ledger, records, overview, build, run state and sources are where they always were."""
    lay = layout(tmp_path)
    assert lay.papers == tmp_path / "pipeline" / "papers.yaml"
    assert lay.ledger == tmp_path / "pipeline" / "completed.yaml"
    assert lay.overview == tmp_path / "overview" / "content.yaml"
    assert (lay.records, lay.build, lay.state, lay.sources) == ("records", "build", "pipeline_state", "corpus")


def test_a_named_corpus_has_a_folder_of_its_own(tmp_path):
    """A named corpus keeps its list, ledger, overview text and records in corpora/<name>/; its files, build and state in their own subfolders."""
    lay = layout(tmp_path, "cardio")
    assert lay.papers == tmp_path / "corpora" / "cardio" / "papers.yaml"
    assert lay.ledger == tmp_path / "corpora" / "cardio" / "completed.yaml"
    assert lay.overview == tmp_path / "corpora" / "cardio" / "overview.yaml"
    assert (lay.records, lay.build, lay.state, lay.sources) == (
        "corpora/cardio/records", "build/cardio", "pipeline_state/cardio", "corpus/cardio")


@pytest.mark.parametrize("bad", ["", "Cardio", "../x", "a/b", "9a", "cache"])
def test_a_corpus_name_is_a_plain_identifier(tmp_path, bad):
    """A corpus name must be lower-case letters, digits and _, start with a letter, and not clash with the build's own folders."""
    with pytest.raises(ValueError):
        layout(tmp_path, bad)


@pytest.fixture
def cardio(tmp_path, monkeypatch):
    """A project with a corpus named cardio of two papers; the pipeline's paths point at it."""
    for name in ("ROOT", "PAPERS", "LEDGER", "RECORDS", "BUILD", "OVERVIEW", "STATE"):
        monkeypatch.setattr(rp, name, getattr(rp, name))  # restored after the test
    d = tmp_path / "corpora" / "cardio"
    d.mkdir(parents=True)
    (d / "papers.yaml").write_text(yaml.safe_dump([
        {"id": "wk2009", "file": "corpus/cardio/wk.pdf", "pages": [1, 4]},
        {"id": "st1999", "file": "corpus/cardio/st.pdf", "pages": [1, 8], "relate_with": ["wk2009"]}]))
    monkeypatch.setattr(rp, "ROOT", tmp_path)
    rp.use_corpus("cardio")
    return tmp_path


def _writes(j):
    return [t for t in j.allowed_tools if t.startswith(("Write(", "Edit("))]


def test_a_named_corpus_reads_into_and_checks_only_its_own_records(cardio):
    """Every per-paper job of a named corpus is told, may write, and is gated on records under corpora/<name>/records/ only."""
    js = rp.jobs("m", 1, 1, 1)
    assert sorted(j.id for j in js["read"]) == ["read:st1999", "read:wk2009"]
    for j in js["read"] + js["audit"] + js["digitize"]:
        rid = j.id.split(":")[1]
        assert f"Edit(corpora/cardio/records/{rid}/**)" in _writes(j)
        assert all(f"corpora/cardio/records/{rid}/**" in t for t in _writes(j))
        assert f"validate corpora/cardio/records/{rid} " in " ".join(j.validate)
        assert f"`corpora/cardio/records/{rid}/`" in j.prompt and "`records/" not in j.prompt
        assert "corpora/cardio/completed.yaml" in j.writable


def test_a_named_corpus_relates_and_validates_within_its_own_records(cardio):
    """Pair jobs of a named corpus edit, check and test records under corpora/<name>/records/ and work in build/<name>/."""
    (r,) = rp.relate_jobs({("st1999", "wk2009"): ["asked"]}, "m", 1)
    (v,) = rp.validate_jobs({("st1999", "wk2009"): ["asked"]}, "m", 1)
    assert "Edit(corpora/cardio/records/st1999/relations.yaml)" in r.allowed_tools
    assert "relations corpora/cardio/records --only st1999,wk2009" in r.validate[2]
    assert "validations corpora/cardio/records --only st1999,wk2009" in v.validate[2]
    assert "Edit(corpora/cardio/records/wk2009/validations.yaml)" in v.allowed_tools
    assert "build/cardio/relate-check/st1999+wk2009/**" in r.writable
    assert "build/cardio/validate-check/st1999+wk2009/**" in v.writable
    for j in (r, v):
        assert "`records/" not in j.prompt and "corpora/cardio/records/" in j.prompt


def test_a_named_corpus_builds_its_own_synthesis_with_its_own_overview(cardio, monkeypatch):
    """The build of a named corpus reads only its records, writes build/<name>/, uses its own overview text and the shared model cache."""
    (cardio / "corpora" / "cardio" / "overview.yaml").write_text("intro: [A review.]\n")
    seen = {}

    def run(cmd, **kw):
        seen.update(cmd=cmd, cwd=kw.get("cwd"))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(rp.subprocess, "run", run)
    assert rp._build("Cardio") == 0
    cmd = seen["cmd"]
    assert cmd[1:5] == ["build", "corpora/cardio/records", "--out", "build/cardio"]
    assert cmd[cmd.index("--overview") + 1] == "corpora/cardio/overview.yaml" and seen["cwd"] == cardio
    assert cmd[cmd.index("--cache") + 1] == rp.CACHE  # the runs its agents and gates made are reused


def test_the_plan_of_a_named_corpus_lists_only_its_papers(tmp_path, monkeypatch, capsys):
    """`run_papers --corpus <name> --plan` plans that corpus's papers, from its own paper list and ledger."""
    for name in ("ROOT", "PAPERS", "LEDGER", "RECORDS", "BUILD", "OVERVIEW", "STATE"):
        monkeypatch.setattr(rp, name, getattr(rp, name))
    d = tmp_path / "corpora" / "cardio"
    d.mkdir(parents=True)
    (d / "papers.yaml").write_text(yaml.safe_dump([{"id": "wk2009", "file": "corpus/cardio/wk.pdf", "pages": [1, 4]}]))
    (d / "completed.yaml").write_text(yaml.safe_dump([{"job": "read:wk2009", "date": "2026-11-02", "cost_usd": 1.0}]))
    monkeypatch.setattr(rp, "ROOT", tmp_path)
    monkeypatch.setattr(rp, "check_papers", lambda *a: [])  # no PDF in the test
    assert rp.main(["--corpus", "cardio", "--plan"]) == 0
    out = capsys.readouterr().out
    assert "read:wk2009" in out and "done 2026-11-02" in out and "audit:wk2009" in out and "bell1978" not in out


def test_page_content_in_a_named_corpus_record_is_refused_and_its_page_folders_are_not_watched(tmp_path):
    """The write scan treats corpora/<name>/records/<id>/ as a record: page images there fail, its pages and text folders are not watched."""
    rec = tmp_path / "corpora" / "cardio" / "records" / "wk2009"
    (rec / "pages").mkdir(parents=True)
    (rec / "pages" / "page-001.png").write_bytes(b"x")
    before = snapshot(tmp_path)
    assert not any("/pages/" in p for p in before)
    (rec / "fig.png").write_bytes(b"x")
    bad = stray_writes(before, snapshot(tmp_path), ["corpora/cardio/records/wk2009/**"])
    assert len(bad) == 1 and "page content" in bad[0]


def _pdf(path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure().savefig(path)
    plt.close("all")
    return path


needs_poppler = pytest.mark.skipif(shutil.which("pdfinfo") is None, reason="needs poppler")


@needs_poppler
def test_adding_a_paper_to_a_named_corpus_lists_it_there(tmp_path):
    """`pipeline.add --corpus <name>` copies the PDF into corpus/<name>/ and appends it to that corpus's paper list only."""
    from pipeline import add

    src = _pdf(tmp_path / "in" / "wk.pdf")
    assert add.main([str(src), "--id", "wk2009", "--corpus", "cardio", "--root", str(tmp_path)]) == 0
    entries = yaml.safe_load((tmp_path / "corpora" / "cardio" / "papers.yaml").read_text())
    assert [e["id"] for e in entries] == ["wk2009"] and entries[0]["file"] == "corpus/cardio/wk.pdf"
    assert (tmp_path / "corpus" / "cardio" / "wk.pdf").is_file()
    assert not (tmp_path / "pipeline" / "papers.yaml").exists()


@needs_poppler
def test_attaching_code_to_a_named_corpus_lists_it_there(tmp_path):
    """`pipeline.attach --corpus <name>` puts released code under corpus/<name>/code/ and lists it in that corpus only."""
    from pipeline import attach

    d = tmp_path / "corpora" / "cardio"
    d.mkdir(parents=True)
    _pdf(tmp_path / "corpus" / "cardio" / "wk.pdf")
    (d / "papers.yaml").write_text(yaml.safe_dump([{"id": "wk2009", "file": "corpus/cardio/wk.pdf", "pages": [1, 1]}]))
    code = tmp_path / "src"
    code.mkdir()
    (code / "wk.py").write_text("R = 1.0\n")
    assert attach.main([str(code), "--id", "wk_code", "--kind", "software", "--papers", "wk2009",
                        "--corpus", "cardio", "--root", str(tmp_path)]) == 0
    entries = yaml.safe_load((d / "papers.yaml").read_text())
    assert entries[-1]["file"] == "corpus/cardio/code/wk_code" and (tmp_path / "corpus/cardio/code/wk_code/wk.py").is_file()


def test_the_command_line_entry_points_accept_a_corpus():
    """add, attach and run_papers all document a --corpus option."""
    for mod in ("pipeline.add", "pipeline.attach", "pipeline.run_papers"):
        r = subprocess.run([sys.executable, "-m", mod, "--help"], capture_output=True, text=True,
                           cwd=Path(__file__).resolve().parents[1])
        assert "--corpus" in r.stdout, mod


@pytest.mark.parametrize("path", ["corpora/cardio/records/wk2009/text/page-001.txt",
                                  "corpora/cardio/records/wk2009/pages/page-001.png",
                                  "corpora/cardio/records/wk2009/figwork/a.png", "corpus/cardio/wk.pdf",
                                  "build/cardio/report.html", "pipeline_state/cardio/state.db"])
def test_page_content_sources_and_builds_of_a_named_corpus_are_never_committed(path):
    """Git ignores a named corpus's page text, page images, figure work, PDFs, build and run state, as it does the default's."""
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run(["git", "check-ignore", "-q", "--no-index", path], cwd=root)
    if r.returncode == 128:
        pytest.skip("not a git checkout")
    assert r.returncode == 0, path


@pytest.mark.parametrize("module", ["pipeline.run_papers", "pipeline.add", "pipeline.attach"])
def test_every_pipeline_command_names_its_corpus(module):
    """The pipeline's commands work on a named corpus in corpora/<name>/: run without --corpus, each stops and says so."""
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    args = {"pipeline.run_papers": ["--plan"], "pipeline.add": ["x.pdf", "--id", "x"],
            "pipeline.attach": ["x.zip", "--id", "x", "--kind", "software", "--papers", "y"]}[module]
    r = subprocess.run([sys.executable, "-m", module, *args], capture_output=True, text=True, cwd=root)
    assert r.returncode != 0 and "--corpus" in r.stderr, (r.returncode, r.stderr[-400:])


def test_the_repository_keeps_every_corpus_in_corpora():
    """No corpus lives at the project root: no records/, pipeline/papers.yaml or overview/ outside corpora/<name>/."""
    root = Path(__file__).resolve().parents[1]
    assert not (root / "records").exists() and not (root / "pipeline" / "papers.yaml").exists()
    assert not (root / "overview").exists()
