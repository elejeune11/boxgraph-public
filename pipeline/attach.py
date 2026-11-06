"""Attach a paper's released code or data to the corpus.

  python -m pipeline.attach code.zip --corpus motor_clutch --id smith_code --kind software --papers smith2015
  python -m pipeline.attach path/to/folder --corpus motor_clutch --id smith_code --kind software --papers smith2015
  python -m pipeline.attach SourceData.xlsx --corpus motor_clutch --id smith_data --kind dataset --papers smith2015

Code goes to corpus/<name>/code/<id>/ (a zip or tar.gz is unpacked safely: no path may leave the
folder, no links, at most 200 MB), data to corpus/<name>/data/<id>.<ext>. Neither is ever committed.
The entry is checked and appended to corpora/<name>/papers.yaml; the next run reads it into
corpora/<name>/records/<id>/ and relates it to its papers.
"""

from __future__ import annotations

import argparse
import shutil
import stat
import sys
import tarfile
import zipfile
from pathlib import Path

from pipeline.corpus import append_entry, check_papers, layout, load_papers

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 200 * 1024 * 1024
JUNK = ("__MACOSX/", ".DS_Store", ".git/")


def is_archive(path: Path) -> bool:
    name = path.name.lower()
    return zipfile.is_zipfile(path) or name.endswith((".tar.gz", ".tgz", ".tar")) and tarfile.is_tarfile(path)


def _members(archive):
    """(name, size, is_dir, is_link, open) for every member of a zip or tar archive."""
    if isinstance(archive, zipfile.ZipFile):
        return [(m.filename, m.file_size, m.is_dir(), stat.S_ISLNK(m.external_attr >> 16),
                 (lambda m=m: archive.open(m))) for m in archive.infolist()]
    return [(m.name + ("/" if m.isdir() else ""), m.size, m.isdir(), not (m.isfile() or m.isdir()),
             (lambda m=m: archive.extractfile(m))) for m in archive.getmembers()]


def unpack(archive_path: Path, dest: Path) -> None:
    """Unpack a zip or a tar(.gz) into dest, refusing any member that would leave it, any link or
    special file, and archives over the size limit. A single top-level folder is unwrapped."""
    archive_path = Path(archive_path)
    opener = zipfile.ZipFile if zipfile.is_zipfile(archive_path) else tarfile.open
    with opener(archive_path) as z:
        members = [m for m in _members(z) if not any(j in m[0] for j in JUNK)]
        if sum(m[1] for m in members) > MAX_BYTES:
            raise ValueError(f"the archive unpacks to more than {MAX_BYTES // 2**20} MB")
        for name, _, _, link, _ in members:
            target = (dest / name).resolve()
            if dest.resolve() not in target.parents and target != dest.resolve():
                raise ValueError(f"{name!r} would be written outside the code folder")
            if link:
                raise ValueError(f"{name!r} is a link or a special file")
        files = [m for m in members if not m[2]]
        tops = {m[0].split("/")[0] for m in members}
        strip = len(tops) == 1 and all("/" in m[0] for m in files)
        dest.mkdir(parents=True, exist_ok=False)
        for name, _, _, _, open_member in files:
            out = dest / (name.split("/", 1)[1] if strip else name)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open_member() as src, open(out, "wb") as f:
                shutil.copyfileobj(src, f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="a .zip, .tar.gz or folder of code, or a data file")
    ap.add_argument("--id", required=True, help="record id, e.g. smith_code")
    ap.add_argument("--kind", required=True, choices=["software", "dataset"])
    ap.add_argument("--papers", required=True, help="comma-separated ids of the papers it belongs to")
    ap.add_argument("--url", default="", help="where it is published")
    ap.add_argument("--note", default="", help="what the reader should know about it")
    ap.add_argument("--corpus", required=True, help="the corpus, kept in corpora/<name>/")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    try:
        lay = layout(root, a.corpus)
    except ValueError as e:
        print(e)
        return 1
    lay.papers.parent.mkdir(parents=True, exist_ok=True)
    src = Path(a.path).resolve()
    if not src.exists():
        print(f"no such file or folder: {src}")
        return 1
    papers_file = lay.papers
    if a.kind == "software":
        dest = root / lay.sources / "code" / a.id
        if dest.exists():
            print(f"{dest} already exists; choose another id or remove it")
            return 1
        try:
            if src.is_dir():
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__MACOSX", ".git", ".DS_Store"))
            elif is_archive(src):
                unpack(src, dest)
            else:
                dest.mkdir(parents=True)
                shutil.copy2(src, dest / src.name)
        except (ValueError, zipfile.BadZipFile, tarfile.TarError, OSError) as e:
            shutil.rmtree(dest, ignore_errors=True)
            print(f"not attached: {e}")
            return 1
    else:
        dest = root / lay.sources / "data" / f"{a.id}{src.suffix.lower()}"
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
    print(f"next: python -m pipeline.run_papers{' --corpus ' + a.corpus if a.corpus else ''} --plan --papers {a.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
