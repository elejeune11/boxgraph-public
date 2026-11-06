"""A corpus's list of papers (corpora/<name>/papers.yaml) and its ledger of finished jobs.

An entry in the corpus list:

  - id: smith2015            # lower case, letters, digits and _; becomes corpora/<name>/records/<id>/
    file: corpus/<name>/Smith.pdf   # under the project root
    pages: [1, 12]           # PDF pages that belong to the paper (supplement included)
    note: "..."              # optional: what the reader should know about the file
    relate_with: [bell1978]  # optional: records to relate it to, beyond those found

The ledger (corpora/<name>/completed.yaml) lists every job that passed its gate,
with its date and cost. It is committed with the records, so a fresh clone
knows what is done; the SQLite state in pipeline_state/<name>/ is only this
machine's progress within a run.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED = {"cache", "overview", "figures", "relate-check", "validate-check", "logs"}  # the build's and state's own folders


@dataclass(frozen=True)
class Layout:
    """Where one corpus keeps its files. Paths that agents and gates name are relative to the project
    root (records, build, state, sources); the files the pipeline reads and writes itself are absolute."""
    papers: Path     # the corpus list
    ledger: Path     # jobs that passed, committed with the records
    overview: Path   # the overview's words (optional)
    records: str     # committed records
    build: str       # the build's output (ignored by git)
    state: str       # this machine's run state (ignored by git)
    sources: str     # PDFs, released code and data (ignored by git)


def layout(root: Path, name: str | None = None) -> Layout:
    """A corpus lives in corpora/<name>/, with its sources, build and run state in a subfolder of their own, so
    corpora are reviewed side by side without mixing. Without a name, the same files sit at the root of a
    project that holds one corpus (tests use this); every corpus of this repository has a name."""
    root = Path(root)
    if name is None:
        return Layout(root / "pipeline" / "papers.yaml", root / "pipeline" / "completed.yaml",
                      root / "overview" / "content.yaml", "records", "build", "pipeline_state", "corpus")
    if not ID_RE.match(name) or name in RESERVED:
        raise ValueError(f"corpus name {name!r}: use lower-case letters, digits and _, starting with a letter "
                         f"(and not one of {', '.join(sorted(RESERVED))})")
    d = root / "corpora" / name
    return Layout(d / "papers.yaml", d / "completed.yaml", d / "overview.yaml", f"corpora/{name}/records",
                  f"build/{name}", f"pipeline_state/{name}", f"corpus/{name}")


def load_papers(path: Path) -> list[dict]:
    path = Path(path)
    return (yaml.safe_load(path.read_text()) or []) if path.exists() else []


def pdf_pages(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise RuntimeError(f"pdfinfo gave no page count for {pdf}")


KINDS = ("software", "dataset")  # besides papers: released code, released data


def missing_sources(papers: list[dict], root: Path, records: Path) -> list[dict]:
    """The sources whose file (a PDF, a code folder, a data file) is not under the project, each with
    the DOI or URL its record gives, so a fresh clone knows what to fetch. Never committed, they are
    supplied by whoever runs the build."""
    out = []
    for p in sorted(papers, key=lambda p: str(p.get("id"))):
        f = p.get("file")
        path = Path(root) / f if f else None
        if path is not None and (path.is_dir() if p.get("kind") == "software" else path.is_file()):
            continue
        src = Path(records) / str(p.get("id")) / "source.yaml"
        s = (yaml.safe_load(src.read_text()) or {}) if src.exists() else {}
        where = f"https://doi.org/{s['doi']}" if s.get("doi") else s.get("url") or ""
        out.append({"id": p.get("id"), "kind": p.get("kind") or "article", "file": f, "title": s.get("title"),
                    "where": where})
    return out


def check_papers(papers: list[dict], root: Path) -> list[str]:
    """Every problem with the corpus list, one line each; empty when it is sound. An entry is a paper
    (a PDF with a page range) or, with `kind: software` or `kind: dataset`, a paper's released code
    (a folder) or data (a file), with the `papers` it belongs to."""
    errs: list[str] = []
    seen: set[str] = set()
    ids = {p.get("id") for p in papers}
    for k, p in enumerate(papers, 1):
        pid = p.get("id")
        where = f"entry {k} ({pid})"
        if not isinstance(pid, str) or not ID_RE.match(pid):
            errs.append(f"{where}: id {pid!r} must be lower case letters, digits and _, starting with a letter")
        elif pid in seen:
            errs.append(f"{where}: duplicate id {pid}")
        seen.add(pid)
        kind = p.get("kind")
        f = p.get("file")
        path = Path(root) / f if f else None
        if kind is not None and kind not in KINDS:
            errs.append(f"{where}: kind {kind!r} is not one of {', '.join(KINDS)} (leave it out for a paper)")
            continue
        if kind == "software":
            if not f or not path.is_dir():
                errs.append(f"{where}: code folder {f} is missing (attach it with python -m pipeline.attach)")
        elif not f or not path.is_file():
            errs.append(f"{where}: file {f} is missing (put it under corpus/)")
        if kind in KINDS:
            linked = p.get("papers") or []
            if not linked:
                errs.append(f"{where}: name the papers this {kind} belongs to (`papers`)")
            for other in linked:
                if other not in ids:
                    errs.append(f"{where}: papers names {other}, which is not in the corpus list")
        else:
            pages = p.get("pages")
            if not (isinstance(pages, list) and len(pages) == 2 and all(isinstance(x, int) for x in pages)):
                errs.append(f"{where}: pages must be [first, last]")
            elif path is not None and path.is_file():
                n = pdf_pages(path)
                if not 1 <= pages[0] <= pages[1] <= n:
                    errs.append(f"{where}: pages {pages[0]}-{pages[1]} are outside the PDF's 1-{n}")
        for other in p.get("relate_with") or []:
            if other not in ids:
                errs.append(f"{where}: relate_with names {other}, which is not in the corpus list")
    return errs


def append_entry(papers_file: Path, entry: dict) -> None:
    """Append one entry to the corpus list, keeping the file's comments and layout."""
    papers_file = Path(papers_file)
    text = papers_file.read_text() if papers_file.exists() else ""
    if text.strip() in ("", "[]"):
        text = ""
    if text and not text.endswith("\n"):
        text += "\n"
    text += yaml.safe_dump([entry], sort_keys=False, allow_unicode=True, width=100, default_flow_style=None)
    papers_file.write_text(text)


def add_paper(papers_file: Path, root: Path, pdf: Path, pid: str, pages: tuple[int, int] | None = None,
              note: str = "", relate_with: list[str] | None = None) -> dict:
    """Append a checked entry to the corpus list; the PDF must already be under the root."""
    papers_file, root, pdf = Path(papers_file), Path(root).resolve(), Path(pdf).resolve()
    rel = pdf.relative_to(root).as_posix()
    n = pdf_pages(pdf)
    entry: dict = {"id": pid, "file": rel, "pages": list(pages) if pages else [1, n]}
    if note:
        entry["note"] = note
    if relate_with:
        entry["relate_with"] = list(relate_with)
    papers = load_papers(papers_file)
    errs = check_papers([*papers, entry], root)
    if errs:
        raise ValueError("; ".join(errs))
    append_entry(papers_file, entry)
    return entry


def load_completed(path: Path) -> dict[str, dict]:
    path = Path(path)
    if not path.exists():
        return {}
    return {r["job"]: r for r in yaml.safe_load(path.read_text()) or []}


def record_completed(path: Path, rows: list[dict]) -> None:
    done = load_completed(path)
    for r in rows:
        done[r["job"]] = dict(r)
    import os
    import tempfile

    path = Path(path)
    text = ("# Jobs that passed their gate; a run skips them (see pipeline/corpus.py).\n"
            + yaml.safe_dump([done[k] for k in sorted(done)], sort_keys=False))
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".tmp")
    with os.fdopen(fd, "w") as f:  # written whole, then swapped in: a killed run never leaves it cut short
        f.write(text)
    os.replace(tmp, path)


def forget_completed(path: Path, job_ids: list[str]) -> None:
    """Remove jobs from the ledger, so they run again."""
    done = load_completed(path)
    keep = [done[k] for k in sorted(done) if k not in set(job_ids)]
    Path(path).write_text("")  # record_completed rewrites the whole file from what is kept
    record_completed(path, keep)
