"""Attach a paper's released code or data to the corpus.

  python -m pipeline.attach code.zip --id smith_code --kind software --papers smith2015 [--url URL] [--note "..."]
  python -m pipeline.attach path/to/folder --id smith_code --kind software --papers smith2015
  python -m pipeline.attach SourceData.xlsx --id smith_data --kind dataset --papers smith2015

Code goes to corpus/code/<id>/ (a zip is unpacked safely: no path may leave the folder, no
links, at most 200 MB), data to corpus/data/<id>.<ext>. Neither is ever committed. The entry is
checked and appended to pipeline/papers.yaml; the next run reads it into records/<id>/ and
relates it to its papers.
"""

from __future__ import annotations

import argparse
import shutil
import stat
import sys
import zipfile
from pathlib import Path

from pipeline.corpus import append_entry, check_papers, load_papers

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 200 * 1024 * 1024
JUNK = ("__MACOSX/", ".DS_Store", ".git/")


def unpack(zip_path: Path, dest: Path) -> None:
    """Unpack a zip into dest, refusing any member that would leave it, any link, and archives over
    the size limit. A single top-level folder is unwrapped."""
    with zipfile.ZipFile(zip_path) as z:
        members = [m for m in z.infolist() if not any(j in m.filename for j in JUNK)]
        if sum(m.file_size for m in members) > MAX_BYTES:
            raise ValueError(f"the archive unpacks to more than {MAX_BYTES // 2**20} MB")
        for m in members:
            target = (dest / m.filename).resolve()
            if dest.resolve() not in target.parents and target != dest.resolve():
                raise ValueError(f"{m.filename!r} would be written outside the code folder")
            if stat.S_ISLNK(m.external_attr >> 16):
                raise ValueError(f"{m.filename!r} is a link")
        tops = {m.filename.split("/")[0] for m in members}
        strip = len(tops) == 1 and all("/" in m.filename for m in members if not m.is_dir())
        dest.mkdir(parents=True, exist_ok=False)
        for m in members:
            if m.is_dir():
                continue
            name = m.filename.split("/", 1)[1] if strip else m.filename
            out = dest / name
            out.parent.mkdir(parents=True, exist_ok=True)
            with z.open(m) as src, open(out, "wb") as f:
                shutil.copyfileobj(src, f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="a .zip or folder of code, or a data file")
    ap.add_argument("--id", required=True, help="record id, e.g. smith_code")
    ap.add_argument("--kind", required=True, choices=["software", "dataset"])
    ap.add_argument("--papers", required=True, help="comma-separated ids of the papers it belongs to")
    ap.add_argument("--url", default="", help="where it is published")
    ap.add_argument("--note", default="", help="what the reader should know about it")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    src = Path(a.path).resolve()
    if not src.exists():
        print(f"no such file or folder: {src}")
        return 1
    papers_file = root / "pipeline" / "papers.yaml"
    if a.kind == "software":
        dest = root / "corpus" / "code" / a.id
        if dest.exists():
            print(f"{dest} already exists; choose another id or remove it")
            return 1
        try:
            if src.is_dir():
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__MACOSX", ".git", ".DS_Store"))
            elif zipfile.is_zipfile(src):
                unpack(src, dest)
            else:
                dest.mkdir(parents=True)
                shutil.copy2(src, dest / src.name)
        except (ValueError, zipfile.BadZipFile, OSError) as e:
            shutil.rmtree(dest, ignore_errors=True)
            print(f"not attached: {e}")
            return 1
    else:
        dest = root / "corpus" / "data" / f"{a.id}{src.suffix.lower()}"
        if dest.exists():
            print(f"{dest} already exists; choose another id or remove it")
            return 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    entry = {"id": a.id, "kind": a.kind, "file": dest.relative_to(root).as_posix(),
             "papers": [x for x in a.papers.split(",") if x]}
    if a.url:
        entry["url"] = a.url
    if a.note:
        entry["note"] = a.note
    errs = check_papers([*load_papers(papers_file), entry], root)
    if errs:
        shutil.rmtree(dest, ignore_errors=True) if dest.is_dir() else dest.unlink(missing_ok=True)
        print("not attached:", *errs, sep="\n  ")
        return 1
    append_entry(papers_file, entry)
    print(f"attached {a.id} ({a.kind}): {entry['file']}, for {', '.join(entry['papers'])}")
    print(f"next: python -m pipeline.run_papers --plan --papers {a.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
