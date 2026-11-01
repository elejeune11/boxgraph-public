"""Which pairs of records get a relation job.

Relating every paper to every other grows as the square of the corpus. A
pair is related when there is a sign that the two papers' models meet:

- one cites the other (a reference linked to the record, or naming its
  first author and year);
- a model says it is described from the other record;
- two models have the same shape: an output of the same dimension and at
  least two dimensional inputs in common (a rate from a rate and a force);
- the corpus list asks for it (relate_with).

Each pair carries its reasons, which the relation job is given.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path

import yaml

from boxgraph.units import dimension_of


def _yaml(path: Path):
    return yaml.safe_load(path.read_text()) if path.exists() else None


NAMES = {"1 / [time]": "rate", "[mass] * [length] / [time] ** 2": "force", "[length]": "length", "[time]": "time",
         "[mass] * [length] ** 2 / [time] ** 2": "energy", "[mass] / [length] / [time] ** 2": "pressure",
         "[length] / [time]": "velocity", "[mass] / [time] ** 2": "stiffness", "[temperature]": "temperature",
         "[substance]": "amount", "[substance] / [length] ** 3": "concentration", "[mass]": "mass"}


def _name(dim: str) -> str:
    return NAMES.get(dim, dim)


def _dims(ports) -> set[str]:
    out = set()
    for p in (ports or {}).values():
        try:
            d = dimension_of(str(p.get("unit", "")))
        except Exception:  # a unit pint cannot parse says nothing about shape
            continue
        if d and d != "dimensionless":
            out.add(d)
    return out


def _surname(author: str) -> str:
    return re.split(r"[\s.]+", author.strip())[-1] if author.strip() else ""


class _Rec:
    def __init__(self, root: Path, rid: str):
        d = root / rid
        src = _yaml(d / "source.yaml") or {}
        self.id = rid
        self.year = str(src.get("year", ""))
        authors = src.get("authors") or []
        self.surname = _surname(authors[0]) if authors else ""
        self.refs = _yaml(d / "references.yaml") or []
        self.models = []
        for f in sorted((d / "models").glob("*/model.yaml")):
            m = _yaml(f) or {}
            self.models.append((m.get("id", f.parent.name), m.get("described_from"), _dims(m.get("inputs")),
                                _dims(m.get("outputs"))))

    def cites(self, other: _Rec) -> str | None:
        for r in self.refs:
            if r.get("source") == other.id:
                return f"{self.id} cites {other.id} ({r.get('id')})"
        if other.surname and other.year:
            pat = re.compile(rf"\b{re.escape(other.surname)}\b.*\b{re.escape(other.year)}\b", re.S)
            for r in self.refs:
                if pat.search(str(r.get("text", ""))):
                    return f"{self.id} cites {other.surname} {other.year} ({r.get('id')})"
        return None

    def described_from(self, other: _Rec) -> str | None:
        for mid, src, _, _ in self.models:
            if src == other.id:
                return f"{self.id}/{mid} is described from {other.id}"
        return None


def _same_shape(a: _Rec, b: _Rec) -> str | None:
    for (ma, _, ia, oa), (mb, _, ib, ob) in itertools.product(a.models, b.models):
        if oa & ob and len(ia & ib) >= 2:
            outs = ", ".join(sorted(map(_name, oa & ob)))
            ins = ", ".join(sorted(map(_name, ia & ib)))
            return f"{a.id}/{ma} and {b.id}/{mb} have the same shape ({outs} from {ins})"
    return None


def candidate_pairs(records_root: Path, ids: list[str], manual: dict[str, list[str]] | None = None
                    ) -> dict[tuple[str, str], list[str]]:
    """Pairs (sorted ids) of records that exist and show a sign of a relation, with the reasons."""
    root = Path(records_root)
    recs = {i: _Rec(root, i) for i in sorted(set(ids)) if (root / i / "source.yaml").exists()}
    out: dict[tuple[str, str], list[str]] = {}
    for a, b in itertools.combinations(sorted(recs), 2):
        ra, rb = recs[a], recs[b]
        reasons = [r for r in (ra.cites(rb), rb.cites(ra), ra.described_from(rb), rb.described_from(ra),
                               _same_shape(ra, rb)) if r]
        for x, y in ((a, b), (b, a)):
            if y in (manual or {}).get(x, []):
                reasons.append(f"the corpus list asks for it ({x}: relate_with)")
        if reasons:
            out[(a, b)] = reasons
    return out


SHAPE = "have the same shape"


def split_pairs(pairs: dict[tuple[str, str], list[str]]) -> tuple[dict, dict]:
    """The pairs to relate, and the pairs only listed for a person. A shared shape alone is a weak sign
    (any rate from a force and a rate has one): it is listed, not given a relation job. A citation, a
    model described from the other record, or a request in the corpus list is enough to relate."""
    run, listed = {}, {}
    for k, reasons in sorted(pairs.items()):
        (run if any(SHAPE not in r for r in reasons) else listed)[k] = reasons
    return run, listed
