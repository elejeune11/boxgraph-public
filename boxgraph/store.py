"""Loading authored records from disk.

records/<source-id>/
  source.yaml                  the Source (with its reader)
  quantities.yaml data.yaml added.yaml runs.yaml comparisons.yaml
  refinements.yaml questions.yaml references.yaml relations.yaml
  figures.yaml cited.yaml validations.yaml     each a YAML list (any may be absent)
  models/<model-id>/model.yaml + model.py
  text/page-NNN.txt            extracted page text (git-ignored), for citation checks

Nothing is computed here. Order of loading never matters (principle 11).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .schema import Model, Record

LIST_FILES = {
    "quantities": "quantities.yaml",
    "data": "data.yaml",
    "added": "added.yaml",
    "runs": "runs.yaml",
    "comparisons": "comparisons.yaml",
    "refinements": "refinements.yaml",
    "questions": "questions.yaml",
    "references": "references.yaml",
    "relations": "relations.yaml",
    "figures": "figures.yaml",
    "cited": "cited.yaml",
    "validations": "validations.yaml",
}


class RecordLoadError(ValueError):
    pass


@dataclass
class LoadedRecord:
    path: Path
    record: Record
    model_code: dict[str, Path] = field(default_factory=dict)  # model id -> model.py

    @property
    def id(self) -> str:
        return self.record.source.id

    def page_text(self, page: int) -> str | None:
        f = self.path / "text" / f"page-{page:03d}.txt"
        return f.read_text(errors="replace") if f.exists() else None

    def has_text(self) -> bool:
        return (self.path / "text").is_dir()

    def source_file(self) -> Path | None:
        """The source's file (e.g. its PDF): absolute, or relative to the project
        root that holds records/<id>/."""
        f = self.record.source.file
        if not f:
            return None
        p = Path(f)
        if p.is_absolute():
            return p if p.exists() else None
        for base in (self.path.parent.parent, Path.cwd()):
            if (base / p).exists():
                return base / p
        return None

    def digest(self) -> str:
        """Content hash of the authored record, code included."""
        h = hashlib.sha256()
        h.update(json.dumps(self.record.model_dump(mode="json"), sort_keys=True).encode())
        for mid in sorted(self.model_code):
            h.update(mid.encode())
            h.update(self.model_code[mid].read_bytes())
        return h.hexdigest()[:16]


def _read_yaml(path: Path):
    try:
        with path.open() as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RecordLoadError(f"{path}: invalid YAML: {e}") from None


def load_record(path: str | Path) -> LoadedRecord:
    path = Path(path)
    src = path / "source.yaml"
    if not src.exists():
        raise RecordLoadError(f"{path}: no source.yaml")
    raw: dict = {"source": _read_yaml(src)}
    for key, fname in LIST_FILES.items():
        f = path / fname
        if f.exists():
            content = _read_yaml(f)
            if content is None:
                content = []
            if not isinstance(content, list):
                raise RecordLoadError(f"{f}: expected a YAML list")
            raw[key] = content
    models = []
    code: dict[str, Path] = {}
    mdir = path / "models"
    if mdir.is_dir():
        for d in sorted(p for p in mdir.iterdir() if p.is_dir()):
            my = d / "model.yaml"
            if not my.exists():
                raise RecordLoadError(f"{d}: no model.yaml")
            m = _read_yaml(my)
            if not isinstance(m, dict):
                raise RecordLoadError(f"{my}: expected a mapping")
            if m.get("id") != d.name:
                raise RecordLoadError(f"{my}: id {m.get('id')!r} must equal its directory name {d.name!r}")
            models.append(m)
            if (d / "model.py").exists():
                code[d.name] = d / "model.py"
    raw["models"] = models
    try:
        rec = Record.model_validate(raw)
    except Exception as e:  # pydantic ValidationError
        raise RecordLoadError(f"{path}: {e}") from None
    return LoadedRecord(path=path, record=rec, model_code=code)


def load_all(root: str | Path) -> list[LoadedRecord]:
    root = Path(root)
    out = []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and (p / "source.yaml").exists()):
        out.append(load_record(d))
    return out


def model_by_id(lr: LoadedRecord, mid: str) -> Model | None:
    for m in lr.record.models:
        if m.id == mid:
            return m
    return None
