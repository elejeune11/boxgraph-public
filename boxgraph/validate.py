"""Soundness of a record (02-boxgraph.md).

A record is sound when every value traces to the paper or is labelled as
added, every model that can be made to run does run, and units and
quantities agree. Soundness is about the record; whether the paper
reproduces is what the record reports, so a not-reproduced verdict is never
an error here.

Errors make a record unsound. Warnings are things a careful reader should
look at but that the design does not forbid.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

import networkx as nx

from . import precision as P
from . import units as U
from .engine import Builder, parse_tolerance
from .schema import AUTHORED_ORIGINS, ComparisonPurpose, Origin
from .sources import code_lines, read_cells, tree_digest
from .store import LoadedRecord, RecordLoadError, load_record


@dataclass
class Report:
    source: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def sound(self) -> bool:
        return not self.errors

    def text(self) -> str:
        lines = [f"{self.source}: {'SOUND' if self.sound else 'NOT SOUND'} ({len(self.errors)} errors, {len(self.warnings)} warnings)"]
        lines += [f"  ERROR   {e}" for e in self.errors]
        lines += [f"  warning {w}" for w in self.warnings]
        return "\n".join(lines)


# --------------------------------------------------------------------------
# Quotes: is the cited text on the cited page? Tolerant of OCR noise.
# --------------------------------------------------------------------------

_OCR_MAP = str.maketrans({
    "γ": "y", "ν": "v", "µ": "u", "μ": "u", "τ": "t", "κ": "k", "α": "a", "β": "b", "ε": "e",
    "ρ": "p", "ω": "w", "ι": "i", "ο": "o", "π": "n", "η": "n", "χ": "x", "δ": "d", "λ": "l",
    "0": "o", "1": "l", "|": "l", "!": "l", "5": "s",
})


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).lower().translate(_OCR_MAP)
    return re.sub(r"[^a-z0-9]", "", s)


def quote_on_page(quote: str, page: str, threshold: float = 0.8) -> bool:
    q, t = _norm(quote), _norm(page)
    if not q:
        return False
    if q in t:
        return True
    if len(q) < 6:
        return False
    n = len(q)
    step = max(1, n // 6)
    best = 0.0
    for i in range(0, max(1, len(t) - n + 1), step):
        window = t[i:i + int(n * 1.25)]
        r = SequenceMatcher(None, q, window, autojunk=False).ratio()
        if r > best:
            best = r
            if best >= threshold:
                return True
    return False


# --------------------------------------------------------------------------


def validate(lr: LoadedRecord, run: bool = True, cache_dir: Path | None = None) -> Report:
    rec = lr.record
    rep = Report(source=rec.source.id)
    E, W = rep.errors.append, rep.warnings.append

    # ---- something was read --------------------------------------------------
    if lr.path.name != rec.source.id:
        E(f"source id {rec.source.id!r} does not match the record's folder {lr.path.name!r}")
    if not rec.data and not rec.models:
        E("the record holds no data and no models: nothing has been read into it yet")

    # ---- ids --------------------------------------------------------------
    ids: dict[str, str] = {}
    groups = [("quantity", rec.quantities), ("datum", rec.data), ("added", rec.added), ("model", rec.models),
              ("run", rec.runs), ("comparison", rec.comparisons), ("refinement", rec.refinements),
              ("question", rec.questions), ("reference", rec.references), ("relation", rec.relations),
              ("figure", rec.figures)]
    for kind, items in groups:
        for it in items:
            key = it.id if kind != "quantity" else "quantity:" + it.id
            if key in ids:
                E(f"duplicate id {it.id!r} ({ids[key]} and {kind})")
            ids[key] = kind
    for r in rec.runs:
        for oid in r.outputs.values():
            if oid in ids:
                E(f"run {r.id}: output id {oid!r} collides with an existing {ids[oid]}")
            ids[oid] = "output"
    quantities = {q.id: q for q in rec.quantities}

    # ---- quantities ---------------------------------------------------------
    for q in rec.quantities:
        try:
            U.parse_dimension(q.dimension)
        except U.UnitError as e:
            E(f"quantity {q.id}: {e}")

    def check_unit(where: str, unit: str, qid: str):
        if qid not in quantities:
            E(f"{where}: unknown quantity {qid!r}")
            return
        try:
            if not U.unit_matches_dimension(unit, quantities[qid].dimension):
                E(f"{where}: unit {unit!r} has dimension {U.dimension_of(unit)}, but quantity {qid!r} is {quantities[qid].dimension}")
        except U.UnitError as e:
            E(f"{where}: {e}")

    # ---- code and data sources --------------------------------------------
    kind = rec.source.kind.value
    unpaged = kind in ("software", "dataset")
    what = "code" if kind == "software" else "data"
    src_path = lr.source_file() if unpaged else None
    if unpaged:
        if not rec.source.version:
            E(f"a {kind} source needs `version`: the digest of the {what} read (sha256:...) or a commit")
        if not rec.source.licence:
            E(f"a {kind} source needs `licence`: its SPDX id, or 'none stated'")
        if src_path is None:
            msg = f"the {what} ({rec.source.file!r}) was not found"
            (E if run else W)(msg if run else msg + "; its citations were checked for structure only")
        elif (rec.source.version or "").startswith("sha256:") and tree_digest(src_path) != rec.source.version:
            E(f"the {what} at {rec.source.file!r} changed since it was read (its digest is {tree_digest(src_path)}); "
              "read it again")

    # ---- citations --------------------------------------------------------
    page_lo, page_hi = (rec.source.page_range or [None, None])

    def check_citation(where: str, c):
        if c is None or c.none is not None:
            return
        if c.file is not None or c.sheet is not None:
            if c.file is not None and kind != "software":
                E(f"{where}: cites a file and lines, but this source is not code")
            if c.sheet is not None and kind != "dataset":
                E(f"{where}: cites a sheet and cells, but this source is not a dataset")
            if c.file is not None and src_path is not None:
                text = code_lines(src_path, c.file, c.lines)
                if text is None:
                    E(f"{where}: line(s) {c.lines} of {c.file} do not exist in the code")
                elif c.quote and not quote_on_page(c.quote, text):
                    E(f"{where}: quote not found on line(s) {c.lines} of {c.file}: {c.quote!r}")
            return
        if c.page is None:
            return
        if page_lo is not None and not (page_lo <= c.page <= page_hi):
            E(f"{where}: page {c.page} is outside this source's pages {page_lo}-{page_hi}")
        if not c.quote:
            W(f"{where}: citation has no quote, so it cannot be checked")
            return
        if not lr.has_text():
            return
        text = lr.page_text(c.page)
        if text is None:
            E(f"{where}: no text for page {c.page}")
        elif not quote_on_page(c.quote, text):
            E(f"{where}: quote not found on page {c.page}: {c.quote!r}")

    if not lr.has_text() and not unpaged:
        W("no extracted page text (text/); quotes were not checked")

    def check_cells(where: str, d):
        """A value cited from a spreadsheet must be what its cells hold, at the printed precision."""
        c = d.citation
        if c is None or c.sheet is None or src_path is None or not src_path.is_file():
            return
        try:
            cells = read_cells(src_path, c.sheet, c.cells)
        except (KeyError, ValueError, OSError) as e:
            E(f"{where}: cells {c.sheet}!{c.cells} cannot be read: {e}")
            return
        printed = [d.printed] if d.printed is not None else list(d.table.values) if d.table is not None else []
        if len(cells) != len(printed):
            E(f"{where}: cites {len(cells)} cell(s) in {c.sheet}!{c.cells} for {len(printed)} value(s)")
            return
        for text, cell in zip(printed, cells):
            if not isinstance(cell, (int, float)):
                E(f"{where}: cell in {c.sheet}!{c.cells} holds {cell!r}, not a number")
                continue
            try:
                ok = P.verdict(float(cell), P.parse(text)) == P.Verdict.reproduced
            except P.PrintedError:
                continue
            if not ok:
                E(f"{where}: printed {text!r}, but its cell in {c.sheet}!{c.cells} holds {cell}")

    # ---- data ---------------------------------------------------------------
    for d in rec.data:
        where = f"datum {d.id}"
        check_unit(where, d.unit, d.quantity)
        check_citation(where, d.citation)
        check_cells(where, d)
        if d.origin not in AUTHORED_ORIGINS:
            E(f"{where}: origin {d.origin.value!r} is given only by a run of the record, never written into it; "
              f"use one of {sorted(o.value for o in AUTHORED_ORIGINS)}")
        texts = [d.printed] if d.printed is not None else list(d.table.values) if d.table is not None else []
        if d.figure is not None:
            fr = next((f for f in rec.figures if f.id == d.figure), None)
            if fr is None:
                E(f"{where}: refers to unknown figure reading {d.figure!r}")
            elif fr.y.quantity != d.quantity:
                E(f"{where}: measures {d.quantity!r} but figure {fr.id} reads {fr.y.quantity!r} on its y axis")
            elif not U.same_dimension(d.unit, fr.y.unit):
                E(f"{where}: unit {d.unit!r} does not fit figure {fr.id}'s y axis unit {fr.y.unit!r}")
        if d.table is not None:
            check_unit(where + " (index)", d.table.index_unit, d.table.index_quantity)
            texts += d.table.index
        for t in texts:
            try:
                P.parse(t)
            except P.PrintedError as e:
                E(f"{where}: {e}")
        if d.tuned_to and d.tuned_to not in ids:
            E(f"{where}: tuned_to refers to unknown {d.tuned_to!r}")
        if d.from_datum and not d.from_source:
            E(f"{where}: from_datum needs from_source")
        for k in d.conditions:
            if k not in quantities:
                W(f"{where}: condition {k!r} is not a declared quantity")

    data_by_id = {d.id: d for d in rec.data}
    linked: set[str] = set()
    for link in rec.cited:
        where = f"cited.yaml {link.datum}"
        d = data_by_id.get(link.datum)
        if d is None:
            E(f"{where}: no datum {link.datum!r} in this record")
        elif not d.from_source and not link.from_source:
            E(f"{where}: neither datum {link.datum} nor the link says which source it comes from (from_source)")
        elif d.from_source and link.from_source and d.from_source != link.from_source:
            E(f"{where}: data.yaml says it comes from {d.from_source!r}; a link may not contradict it")
        elif d.from_datum and d.from_datum != link.from_datum:
            E(f"{where}: data.yaml already says it is {d.from_datum!r}; a link may not contradict it")
        if link.datum in linked:
            E(f"{where}: linked twice")
        linked.add(link.datum)

    for a in rec.added:
        where = f"added {a.id}"
        check_unit(where, a.unit, a.quantity)
        for t in [a.printed, *a.alternatives]:
            try:
                P.parse(t)
            except P.PrintedError as e:
                E(f"{where}: {e}")
        if not a.alternatives:
            W(f"{where}: no alternatives; an added input that matters should be run both ways")

    # ---- figure readings -----------------------------------------------------
    from . import digitize as D

    for fr in rec.figures:
        where = f"figure {fr.id}"
        if page_lo is not None and not (page_lo <= fr.page <= page_hi):
            E(f"{where}: page {fr.page} is outside this source's pages {page_lo}-{page_hi}")
        if fr.mode == "code":
            if not fr.code:
                E(f"{where}: mode code needs `code`, the reading code's path in the record")
            elif not (lr.path / fr.code).is_file():
                E(f"{where}: its code {fr.code!r} was not found in the record")
        for name, ax in (("x", fr.x), ("y", fr.y)):
            check_unit(f"{where} {name} axis", ax.unit, ax.quantity)
            if fr.mode == "code" and not ax.marks:
                continue  # the code calibrates the axis itself
            try:
                marks = [(p, P.parse(t).value) for p, t in ax.marks]
                cal = D.Axis(ax.scale, marks)
            except (P.PrintedError, D.CalibrationError) as e:
                E(f"{where} {name} axis: {e}")
                continue
            if cal.residual_px > 1.5:
                E(f"{where} {name} axis: the marks do not lie on one {ax.scale} scale (misfit {cal.residual_px:.1f} px); "
                  f"a label is probably attached to the wrong tick")
            if len(ax.marks) < 3:
                W(f"{where} {name} axis: only two marks; add a third mark, so a mislabelled tick would be caught")
        if fr.error_bars is not None:
            if fr.mode == "curve":
                E(f"{where}: error bars are read on markers or bars, not on a curve")
            if fr.error_bars_citation is None:
                E(f"{where}: error bars are {fr.error_bars!r}; cite where the paper says what the error bars are "
                  f"(`error_bars_citation`), or use `unstated` with a citation saying they are not described")
            else:
                check_citation(f"{where} error bars", fr.error_bars_citation)
        if fr.mode == "curve" and not fr.at:
            E(f"{where}: a curve reading needs the x positions to read (`at`)")
        for t in fr.at:
            try:
                P.parse(t)
            except P.PrintedError as e:
                E(f"{where}: {e}")
        if not any(d.figure == fr.id for d in rec.data):
            W(f"{where}: no datum uses this reading")
    if rec.figures and lr.source_file() is None:
        msg = f"figure readings need the source file, and {rec.source.file!r} was not found"
        # without running, only the readings' structure is checked: the PDF is never committed
        (E if run else W)(msg if run else msg + "; their structure was checked, their values were not read")

    # ---- models -------------------------------------------------------------
    question_about = {x for q in rec.questions for x in q.about}
    for m in rec.models:
        where = f"model {m.id}"
        check_citation(where, m.stated)
        for sym, port in {**m.inputs, **m.outputs}.items():
            check_unit(f"{where} port {sym}", port.unit, port.quantity)
        for b in m.built_from:
            if b not in ids or ids[b] != "model":
                E(f"{where}: built_from refers to unknown model {b!r}")
        if m.runnable:
            if m.id not in lr.model_code:
                E(f"{where}: runnable but has no model.py")
        elif m.id not in question_about:
            E(f"{where}: cannot be made runnable, so it needs an open question about it saying why")
        if m.runnable and not any(r.model == m.id for r in rec.runs):
            W(f"{where}: never run")
        if m.stochastic and "seed" not in m.settings:
            E(f"{where}: a model with randomness needs a `seed` among its settings, so its runs can be repeated")
        if m.stochastic and not any(
            ref.run in {r.id for r in rec.runs if r.model == m.id} for ref in rec.refinements
        ):
            W(f"{where}: stochastic, but no run of it is refined")
        if m.variant_of is not None:
            base = next((x for x in rec.models if x.id == m.variant_of), None)
            if base is None or base.id == m.id or base.variant_of is not None:
                E(f"{where}: a variant of {m.variant_of!r}, which is not a printed model of this record")
            if not m.corrections:
                E(f"{where}: a variant needs its corrections (equation, change, evidence)")
        elif m.corrections:
            E(f"{where}: corrections belong to a variant: name the printed model it corrects in variant_of")
        for k, cr in enumerate(m.corrections):
            for f in ("equation", "change", "evidence"):
                if not str(getattr(cr, f) or "").strip():
                    E(f"{where}: correction {k + 1} needs its {f}")

    built = nx.DiGraph((m.id, b) for m in rec.models for b in m.built_from)
    cycles = {tuple(c[c.index(min(c)):] + c[:c.index(min(c))]) for c in nx.simple_cycles(built)}
    for c in sorted(cycles):
        E(f"model {c[0]}: built_from forms a cycle: {' -> '.join([*c, c[0]])}")

    # ---- runs, comparisons, refinements --------------------------------------
    node_ids = {k for k, v in ids.items() if v in ("datum", "added", "output")}
    model_ids = {m.id for m in rec.models}
    # which nodes are curves: a table or figure datum, a swept run's outputs, a curve port's output
    models_by_id = {m.id: m for m in rec.models}
    is_curve = {d.id: d.table is not None or d.figure is not None for d in rec.data}
    for r in rec.runs:
        m = models_by_id.get(r.model)
        for sym, port in (m.outputs.items() if m else ()):
            is_curve[r.outputs.get(sym, f"{r.id}.{sym}")] = bool(r.sweep) or port.curve is not None

    def check_curve_ports(where, m, inputs):
        for sym, vid in inputs.items():
            port = m.inputs.get(sym) if m else None
            if port is None or vid not in is_curve:
                continue
            if port.curve and not is_curve[vid]:
                E(f"{where}: input {sym} takes a curve; {vid} is a single value")
            elif not port.curve and is_curve[vid]:
                E(f"{where}: input {sym} takes one number; {vid} is a curve "
                  "(sweep over its x values, or give the model a curve port)")

    for r in rec.runs:
        if r.model not in model_ids:
            E(f"run {r.id}: unknown model {r.model!r}")
        for sym, vid in {**r.inputs, **r.sweep}.items():
            if vid not in node_ids:
                E(f"run {r.id}: input {sym} refers to unknown {vid!r}")
        check_curve_ports(f"run {r.id}", models_by_id.get(r.model), r.inputs)
    for c in rec.comparisons:
        for side in (c.computed, c.printed):
            if side not in node_ids:
                E(f"comparison {c.id}: refers to unknown {side!r}")
    # ---- models against another record's measurements --------------------------
    quantity_ids = {q.id for q in rec.quantities}
    seen_v: set[str] = set()
    for v in rec.validations:
        where = f"validation {v.id}"
        if v.id in seen_v or v.id in {c.id for c in rec.comparisons}:
            E(f"{where}: id used twice")
        seen_v.add(v.id)
        if not v.basis.strip():
            E(f"{where}: say why the model is expected to predict the measurement (basis)")
        if v.purpose not in (ComparisonPurpose.validation, ComparisonPurpose.fit_quality):
            E(f"{where}: purpose must be validation, or fit_quality for a model fitted to that measurement")
        m = models_by_id.get(v.model)
        if m is None:
            E(f"{where}: unknown model {v.model!r}")
        else:
            if v.output not in m.outputs:
                E(f"{where}: model {m.id} has no output {v.output!r}")
            given = set(v.inputs) | set(v.sweep)
            missing, unknown = sorted(set(m.inputs) - given), sorted(given - set(m.inputs))
            if missing or unknown:
                E(f"{where}: inputs do not match model {m.id}: missing {missing}, unknown {unknown}")
        for sym, vid in {**v.inputs, **v.sweep}.items():
            if "/" not in vid and vid not in node_ids:
                E(f"{where}: input {sym} refers to unknown {vid!r}")
        check_curve_ports(where, models_by_id.get(v.model), {s: i for s, i in v.inputs.items() if "/" not in i})
        if v.against.count("/") != 1 or v.against.split("/")[0] in ("", rec.source.id):
            E(f"{where}: against must name a datum of another record, as '<record>/<datum>' (got {v.against!r})")
        for there, here in v.quantities.items():
            if there.count("/") != 1:
                E(f"{where}: quantities: {there!r} must be '<record>/<quantity>'")
            if here not in quantity_ids:
                E(f"{where}: quantities: {here!r} is not a quantity of this record")

    run_ids = {r.id for r in rec.runs}
    for ref in rec.refinements:
        if ref.run not in run_ids:
            E(f"refinement {ref.id}: unknown run {ref.run!r}")
        if not ref.tolerance_basis:
            E(f"refinement {ref.id}: the tolerance needs a stated basis")
        if len(ref.factors) < 2 or 1 not in ref.factors:
            E(f"refinement {ref.id}: needs at least two factors, one of them 1 (the paper's own setting); "
              f"got {ref.factors}")
        try:
            parse_tolerance(ref.tolerance)
        except ValueError as e:
            E(f"refinement {ref.id}: {e}")

    compared = {c.printed for c in rec.comparisons} | {c.computed for c in rec.comparisons}
    for d in rec.data:
        if d.origin in (Origin.predicted, Origin.derived) and d.id not in compared:
            W(f"datum {d.id}: a result the paper printed but is never compared with a run")
    if not any(c.purpose == ComparisonPurpose.reproduction for c in rec.comparisons) and rec.models:
        W("no reproduction comparisons: nothing in this paper is checked against itself")

    # ---- questions, references, relations ------------------------------------
    known = set(ids) | {q.id for q in rec.quantities} | {f"quantity:{q.id}" for q in rec.quantities}
    for q in rec.questions:
        for a in q.about:
            if a not in known and "/" not in a:
                E(f"question {q.id}: about unknown {a!r}")
        if q.citation:
            check_citation(f"question {q.id}", q.citation)
    for rel in rec.relations:
        for side in (rel.a, rel.b):
            if "/" not in side:
                E(f"relation {rel.id}: model ids must be global '<source>/<model>', got {side!r}")
        if rel.citation:
            check_citation(f"relation {rel.id}", rel.citation)

    # ---- every model that can run does run -----------------------------------
    if run and not rep.errors:
        b = Builder(lr, cache_dir=cache_dir).build()
        for p in b.problems:
            E(p)
        for w in b.warnings:
            W(w)
    return rep


def validate_path(path: str | Path, run: bool = True, cache_dir: Path | None = None) -> Report:
    try:
        lr = load_record(path)
    except RecordLoadError as e:
        rep = Report(source=Path(path).name)
        rep.errors.append(str(e))
        return rep
    return validate(lr, run=run, cache_dir=cache_dir)
