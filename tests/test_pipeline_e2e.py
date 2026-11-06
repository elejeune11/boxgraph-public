"""The whole pipeline, end to end, with a fake agent: a corpus of two generated PDFs is
ingested, read, audited, digitized, related and built; a second run spends nothing; and a
paper whose reading fails is parked while the rest of the corpus goes on."""

import json
import shutil
import stat
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

import pipeline.run_papers as rp

FX = Path(__file__).parent / "fixtures"
needs_poppler = pytest.mark.skipif(shutil.which("pdftotext") is None, reason="needs poppler")

FAKE = textwrap.dedent('''\
    #!{python}
    # A fake `claude -p`: does each kind of job the way a careful agent would, instantly.
    import json, os, re, shutil, sys
    args = sys.argv[1:]
    prompt = args[args.index("-p") + 1]
    with open(os.environ["FAKE_LOG"], "a") as f:
        f.write(json.dumps({{"prompt": prompt[:80]}}) + "\\n")
    m = re.search(r"((?:corpora/[a-z0-9_]+/)?records)/([a-z][a-z0-9_]*)/", prompt)
    recs, rid = (m.group(1), m.group(2)) if m else ("records", None)
    if (prompt.startswith("Read the paper") or prompt.startswith("Read the code")) and rid != os.environ.get("FAKE_BAD"):
        shutil.copytree(os.path.join(os.environ["FAKE_FIXTURES"], rid), os.path.join(recs, rid), dirs_exist_ok=True)
    elif prompt.startswith("You are auditing"):
        open(os.path.join(recs, rid, "audit.md"), "w").write("Checked every value against its page.\\n")
    elif prompt.startswith("Read the figures"):
        open(os.path.join(recs, rid, "figures.md"), "w").write("No figure plots values.\\n")
    sid = args[args.index("--session-id") + 1] if "--session-id" in args else args[args.index("--resume") + 1]
    print(json.dumps({{"type": "result", "subtype": "success", "session_id": sid, "total_cost_usd": 0.25,
                      "num_turns": 2, "is_error": False}}))
''')


def _quotes(rec: Path) -> dict[int, list[str]]:
    """Every quote a fixture record cites, by page, so the generated PDF prints them."""
    pages: dict[int, list[str]] = {}

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("page"), int) and isinstance(x.get("quote"), str):
                pages.setdefault(x["page"], []).append(x["quote"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    for f in sorted(rec.rglob("*.yaml")):
        walk(yaml.safe_load(f.read_text()))
    return pages


def _pdf(path: Path, pages: dict[int, list[str]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(path) as pdf:
        for n in range(1, max(pages) + 1):
            fig = plt.figure(figsize=(8.5, 11))
            for i, q in enumerate(pages.get(n, [])):
                fig.text(0.08, 0.9 - 0.04 * i, q, fontsize=11)
            pdf.savefig(fig)
            plt.close(fig)


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    (root / "corpora" / "toys").mkdir(parents=True)
    (root / ".venv").mkdir()  # the gates call .venv/bin/...: point it at the interpreter running the tests (CI has no .venv)
    (root / ".venv" / "bin").symlink_to(Path(sys.executable).parent)
    papers = []
    for rid in ("toy", "toy2"):
        n = max(_quotes(FX / rid))
        _pdf(root / "corpus" / "toys" / f"{rid}.pdf", _quotes(FX / rid))
        papers.append({"id": rid, "file": f"corpus/toys/{rid}.pdf", "pages": [1, n]})
    papers[1]["relate_with"] = ["toy"]
    shutil.copytree(FX / "toycode_src", root / "corpus" / "code" / "toycode")  # the code released with toy
    papers.append({"id": "toycode", "kind": "software", "file": "corpus/code/toycode", "papers": ["toy"]})
    (root / "corpora" / "toys" / "papers.yaml").write_text(yaml.safe_dump(papers, sort_keys=False))
    fake = tmp_path / "claude"
    fake.write_text(FAKE.format(python=sys.executable))
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_LOG", str(log))
    monkeypatch.setenv("FAKE_FIXTURES", str(FX))
    for name in ("PAPERS", "LEDGER", "RECORDS", "BUILD", "OVERVIEW", "STATE"):
        monkeypatch.setattr(rp, name, getattr(rp, name))  # --corpus repoints them; restored after the test
    monkeypatch.setattr(rp, "ROOT", root)
    monkeypatch.chdir(root)
    return root, fake, log


def _calls(log: Path) -> list[dict]:
    return [json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []


@needs_poppler
def test_a_corpus_runs_end_to_end_and_a_second_run_spends_nothing(project, capsys):
    """Two papers and one paper's code go through ingest, read, audit, digitize, relate, validate and build; the ledger lists every
    job; the code's value that differs from the paper is a finding; a rerun runs no agent."""
    root, fake, log = project
    assert rp.main(["--corpus", "toys", "--agent", str(fake)]) == 0, capsys.readouterr().out
    done = rp.load_completed(root / "corpora" / "toys" / "completed.yaml")
    assert sorted(done) == ["audit:toy", "audit:toy2", "digitize:toy", "digitize:toy2", "read:toy", "read:toy2",
                            "read:toycode", "relate:toy+toy2", "relate:toy+toycode", "validate:toy+toy2",
                            "validate:toy+toycode"]
    syn = json.loads((root / "build" / "toys" / "synthesis.json").read_text())
    assert any(f["subject"] == "toycode/k0_code" and f["kind"] == "cited_value" for f in syn["findings"])
    assert (root / "build" / "toys" / "report.html").exists() and (root / "corpora" / "toys" / "records" / "toy" / "text").is_dir()
    assert (root / "pipeline_state" / "toys" / "state.db").exists()
    n = len(_calls(log))
    assert rp.main(["--corpus", "toys", "--agent", str(fake)]) == 0
    assert len(_calls(log)) == n


@needs_poppler
def test_a_paper_that_cannot_be_read_is_parked_and_the_rest_go_on(project, capsys, monkeypatch):
    """When one paper's reading fails, its later jobs are blocked, the other paper is finished, and the run exits 1 naming the job."""
    root, fake, log = project
    monkeypatch.setenv("FAKE_BAD", "toy2")
    rc = rp.main(["--corpus", "toys", "--agent", str(fake)])
    out = capsys.readouterr().out
    done = rp.load_completed(root / "corpora" / "toys" / "completed.yaml")
    assert rc == 1 and "read:toy2" in out and "needs a person" in out
    assert {"read:toy", "audit:toy", "digitize:toy"} <= set(done) and "read:toy2" not in done
    assert not any(j.startswith("relate:") and "toy2" in j for j in done) and "relate:toy+toycode" in done
