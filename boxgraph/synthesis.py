"""The Synthesis (04-synthesis.md): the whole graph read as a review.

Holds, for every sound record: verdicts; cross-paper checks wherever a
verified same-as relation lets one paper's model run on another's inputs;
checks of cited values (which need no relation); findings; implications;
and references ranked by how much they would settle.

Everything is recomputed from the records every time and sorted, so the
result never depends on the order papers were added (principle 11).
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path

import networkx as nx
import sympy as sp

from . import precision as P
from . import units as U
from .atlas import families as compute_families
from .atlas import test_relation
from .engine import Builder, BuildError, RecordBuild, execute
from .schema import ComparisonPurpose, Provenance
from .store import LoadedRecord, RecordLoadError, load_record, model_by_id
from .validate import validate


def g(sid: str, local: str) -> str:
    return f"{sid}/{local}"


def _datum(lr: LoadedRecord, did: str):
    return next((d for d in lr.record.data if d.id == did), None)


# --------------------------------------------------------------------------


def _load(root: Path) -> tuple[dict[str, LoadedRecord], dict[str, dict]]:
    records, papers = {}, {}
    for d in sorted(p for p in Path(root).iterdir() if p.is_dir() and (p / "source.yaml").exists()):
        try:
            lr = load_record(d)
        except RecordLoadError as e:
            papers[d.name] = {"id": d.name, "sound": False, "errors": [str(e)], "warnings": []}
            continue
        records[lr.id] = lr
    return records, papers


def _paper_summary(lr: LoadedRecord, b: RecordBuild, rep) -> dict:
    rec = lr.record
    verdicts = []
    for c in rec.comparisons:
        if b is None:  # not sound: nothing was built
            break
        cr = b.comparisons.get(c.id)
        pd = _datum(lr, c.printed)
        verdicts.append({
            "comparison": c.id, "purpose": c.purpose.value, "computed": c.computed, "printed": c.printed,
            "verdict": cr.verdict if cr and cr.ok else None, "error": None if cr is None or cr.ok else cr.error,
            "computed_value": cr.computed_value if cr else None, "printed_text": cr.printed_text if cr else None,
            "per_value": cr.per_value if cr else None, "computed_se": cr.computed_se if cr else None,
            "page": pd.citation.page if pd else None, "quote": pd.citation.quote if pd else None,
        })
    compared = {c.printed for c in rec.comparisons}
    cannot = []
    for d in rec.data:
        if d.origin.value in ("predicted", "derived") and d.id not in compared:
            cannot.append({"datum": d.id, "why": "printed result never compared with a run"})
    for m in rec.models:
        if not m.runnable:
            cannot.append({"model": m.id, "why": f"model cannot be run: {m.not_runnable_reason}"})
    for v in verdicts:
        if v["verdict"] == "no verdict":
            cannot.append({"comparison": v["comparison"], "why": "printed without a precision"})
        if v["error"]:
            cannot.append({"comparison": v["comparison"], "why": v["error"]})
    tally = {"reproduced": 0, "close": 0, "not reproduced": 0, "no verdict": 0, "error": 0}
    by_purpose: dict[str, dict[str, int]] = {}
    for v in verdicts:
        if v["purpose"] == "reproduction":
            tally[v["verdict"] or "error"] += 1
        t = by_purpose.setdefault(v["purpose"], {"reproduced": 0, "close": 0, "not reproduced": 0, "no verdict": 0, "error": 0})
        t[v["verdict"] or "error"] += 1
    data = {d.id: {"printed": d.printed if d.printed is not None else d.table.values if d.table is not None
                   else f"read from figure {d.figure}", "unit": d.unit,
                   "scale": d.scale, "quantity": d.quantity, "origin": d.origin.value, "page": d.citation.page,
                   "quote": d.citation.quote, "from_source": d.from_source} for d in rec.data}
    figure_data: dict[str, set[str]] = {}
    for d in rec.data:
        if d.figure is not None:
            figure_data.setdefault(d.figure, set()).add(d.id)
    added = {a.id: {"printed": a.printed, "unit": a.unit, "basis": a.basis, "alternatives": a.alternatives}
             for a in rec.added}
    models = {m.id: {"name": m.name, "equation": m.equation, "page": m.stated.page, "runnable": m.runnable,
                  "role": m.role.value} for m in rec.models}
    return {
        "tally": tally, "tally_by_purpose": dict(sorted(by_purpose.items())), "data": data, "added": added, "models": models,
        "id": rec.source.id, "kind": rec.source.kind.value, "title": rec.source.title, "authors": rec.source.authors,
        "year": rec.source.year, "venue": rec.source.venue,
        "reader": rec.source.reader.model_dump(), "digest": b.digest if b else None,
        "sound": rep.sound and not (b and b.problems), "errors": rep.errors + (b.problems if b else []),
        "warnings": rep.warnings, "verdicts": verdicts, "cannot_check": cannot,
        "refinements": list(b.refinements.values()) if b else [], "alternatives": b.alternatives if b else [],
        "figures": [{**{k: f.get(k) for k in ("id", "where", "what", "page", "readings", "skew_deg", "residual_px",
                                              "errors", "notes", "overlay")},
                     "used_by": [{"comparison": v["comparison"], "purpose": v["purpose"], "verdict": v["verdict"],
                                  "per_value": v["per_value"]}
                                 for v in verdicts if v["printed"] in figure_data.get(f["id"], ())]}
                    for f in (b.figures.values() if b else [])],
        "counts": {
            "data": len(rec.data), "added": len(rec.added), "models": len(rec.models), "runs": len(rec.runs),
            "comparisons": len(rec.comparisons), "questions": len(rec.questions), "references": len(rec.references),
        },
        "questions": [q.model_dump(mode="json") for q in rec.questions],
    }


# --------------------------------------------------------------------------
# Cited values
# --------------------------------------------------------------------------


def _from_source(lr: LoadedRecord, d) -> str | None:
    """The work a datum says it comes from, in data.yaml or in a later link in cited.yaml."""
    link = next((c for c in lr.record.cited if c.datum == d.id), None)
    return d.from_source or (link.from_source if link else None)


def _cited_record(lr: LoadedRecord, d) -> str:
    """The record a datum says it comes from: readers name the cited work by its reference id,
    and the reference says which record it is."""
    refs = {r.id: r.source for r in lr.record.references if r.source}
    src = _from_source(lr, d)
    return refs.get(src, src)


def _cited_link(lr: LoadedRecord, d):
    return next((c for c in lr.record.cited if c.datum == d.id), None)


def _cited_from(lr: LoadedRecord, d) -> str | None:
    """Which value of the cited record a datum is: from data.yaml, or named later in cited.yaml."""
    link = _cited_link(lr, d)
    return d.from_datum or (link.from_datum if link else None)


def _cited_values(records: dict[str, LoadedRecord], sound: set[str], builds: dict | None = None) -> list[dict]:
    out = []
    for sid in sorted(sound):
        lr = records[sid]
        for d in lr.record.data:
            from_source = _from_source(lr, d)
            if not from_source:
                continue
            src = _cited_record(lr, d)
            from_datum = _cited_from(lr, d)
            row = {"datum": g(sid, d.id), "from_source": from_source, "from_datum": from_datum,
                   "printed": d.printed, "page": d.citation.page}
            if src != from_source:
                row["cited_record"] = src
            if src not in records or src not in sound:
                row["status"] = "cited source not in the record"
            elif not from_datum:
                row["status"] = "cannot be checked: the record does not say which value in the cited source"
            else:
                cited = _datum(records[src], from_datum)
                if cited is None:
                    row["status"] = f"cited datum {from_datum!r} not found in {src}"
                elif d.printed is None or cited.printed is None:
                    row.update(_cited_table(lr, d, (builds or {}).get(sid), (builds or {}).get(src), from_datum, src, sid))
                else:
                    try:
                        mine = P.parse(d.printed).value
                        theirs = P.parse(cited.printed)
                        y = U.convert(mine, d.unit, cited.unit, d.scale, cited.scale)
                        link = _cited_link(lr, d)
                        if link and link.negated:  # a stated sign convention, applied and shown
                            y = -y
                            row["convention"] = f"opposite sign, as stated in cited.yaml: {link.evidence}"
                        row.update(status="checked", cited_printed=cited.printed, value_in_cited_units=y,
                                   verdict=P.verdict(y, theirs).value,
                                   correspondence=f"{g(sid, d.quantity)} ↔ {g(src, cited.quantity)}")
                    except (P.PrintedError, U.UnitError) as e:
                        row["status"] = f"cannot be checked: {e}"
            out.append(row)
    return sorted(out, key=lambda r: r["datum"])


def _cited_table(lr, d, mine_b, theirs_b, from_datum: str, src: str, sid: str) -> dict:
    """A table (a printed table, or a curve read from a figure) said to come from another source:
    the cited source's value at each shared x is judged against this datum's own precision (the
    printed digits, or a reading's interval), so a reading is checked against the data it shows."""
    if mine_b is None or theirs_b is None:
        return {"status": "cannot be checked: a record was not built"}
    mv, cv = mine_b.values.get(d.id), theirs_b.values.get(from_datum)
    if mv is None or cv is None or not mv.is_table or not cv.is_table:
        return {"status": "cannot be checked: a table can only be compared with a table"}
    if mv.index_quantity != cv.index_quantity:
        return {"status": f"cannot be checked: indexed by {mv.index_quantity!r} and {cv.index_quantity!r}"}
    link = _cited_link(lr, d)
    sign = -1.0 if link and link.negated else 1.0
    try:
        cx = [None if x is None else U.convert(x, cv.index_unit, mv.index_unit) for x in cv.index]
        per, theirs = [], []
        for x, pp in zip(mv.index, mv.printed_values):
            j = next((k for k, y in enumerate(cx) if x is not None and y is not None
                      and abs(x - y) <= 1e-9 * max(abs(x), abs(y), 1e-300)), None)
            yv = None if j is None or cv.values[j] is None else sign * U.convert(cv.values[j], cv.unit, mv.unit, cv.scale, mv.scale)
            theirs.append(yv)
            per.append(P.Verdict.no_verdict.value if yv is None or pp is None else P.verdict(yv, pp).value)
    except U.UnitError as e:
        return {"status": f"cannot be checked: {e}"}
    if all(v == P.Verdict.no_verdict.value for v in per):
        return {"status": "cannot be checked: no x value in common"}
    row = {"status": "checked", "per_value": per, "cited_values_here": theirs,
           "verdict": P.combine([P.Verdict(v) for v in per]).value,
           "cited_printed": f"{sum(v != P.Verdict.no_verdict.value for v in per)} values of {src}/{from_datum}",
           "correspondence": f"{g(sid, d.quantity)} ↔ {g(src, cv.quantity)}"}
    if sign < 0:
        row["convention"] = f"opposite sign, as stated in cited.yaml: {link.evidence}"
    return row


# --------------------------------------------------------------------------
# Cross-paper checks
# --------------------------------------------------------------------------


def _solve_inputs(rel, ma, mb, b_vals: dict[str, float], a_own: dict[str, float] | None):
    """Find a's inputs from b's values through the mapping. Inputs the
    mapping leaves free are taken from a's own run, labelled as added."""
    syms = {n: sp.Symbol(n, positive=True) for n in ma.inputs}
    eqs = []
    for bs, expr in rel.mapping.items():
        if bs in b_vals:
            eqs.append(sp.Eq(sp.sympify(expr, locals=syms), sp.nsimplify(b_vals[bs], rational=False)))
    names = list(ma.inputs)
    for k in range(len(names), 0, -1):
        for subset in combinations(names, k):
            free = [n for n in names if n not in subset]
            if free and (a_own is None or any(n not in a_own for n in free)):
                continue
            sub = {syms[n]: a_own[n] for n in free} if free else {}
            try:
                sol = sp.solve([e.subs(sub) for e in eqs], [syms[n] for n in subset], dict=True)
            except Exception:  # noqa: BLE001
                continue
            for s in sol:
                vals = {}
                ok = True
                for n in subset:
                    if syms[n] not in s:
                        ok = False
                        break
                    v = s[syms[n]]
                    if not v.is_number:
                        ok = False
                        break
                    vals[n] = float(v)
                if ok and all(v > 0 for v in vals.values()):
                    for n in free:
                        vals[n] = a_own[n]
                    return vals, free
    return None, None


def _comparisons_on(lr: LoadedRecord, out_id: str | None) -> list:
    return [c for c in lr.record.comparisons if c.computed == out_id]


def _own_verdict(builds: dict, sid: str, cid: str) -> str | None:
    cr = builds[sid][2].get(cid)
    return cr.verdict if cr and cr.ok else None


def _correspondences(rel, sa: str, ma, sb: str, mb) -> list[str]:
    """Every pairing of quantities a cross-paper run relies on: listed, never merged."""
    pairs = []
    for bs, expr in sorted(rel.mapping.items()):
        if bs not in mb.inputs:
            continue
        for asym in sorted(s.name for s in sp.sympify(expr).free_symbols):
            if asym in ma.inputs:
                pairs.append(f"{g(sb, mb.inputs[bs].quantity)} ↔ {g(sa, ma.inputs[asym].quantity)}")
    return sorted(set(pairs))


def _cross_checks(records, sound, rel_results, rels, evaluated, cache_dir=None) -> list[dict]:
    out = []
    for key in sorted(rel_results):
        res = rel_results[key]
        rel, rsrc = rels[key]
        if not (res.kind == "same_as" and res.status == "verified" and not res.too_plain):
            continue
        sa, ma_id = rel.a.split("/", 1)
        sb, mb_id = rel.b.split("/", 1)
        if sa not in sound or sb not in sound:
            continue
        la, lb = records[sa], records[sb]
        ma, mb = model_by_id(la, ma_id), model_by_id(lb, mb_id)
        if rel.output_map:
            (bo, ao), = rel.output_map.items()
        else:
            ao, bo = next(iter(ma.outputs)), next(iter(mb.outputs))
        builds = {sa: evaluated[sa], sb: evaluated[sb]}  # each record is evaluated once, in the build

        a_runs = sorted((r for r in la.record.runs if r.model == ma_id and not r.sweep), key=lambda r: r.id)
        a_own = None
        a_own_run = None
        for r in a_runs:
            rr = builds[sa][1].get(r.id)
            if rr and rr.ok:
                a_own, a_own_run = rr.inputs, r.id
                break

        # (1) a's model on b's inputs, against b's printed results
        for r in sorted(lb.record.runs, key=lambda r: r.id):
            if r.model != mb_id:
                continue
            rr = builds[sb][1].get(r.id)
            base = {"relation": g(rsrc, rel.id), "model": rel.a, "on_inputs_of": sb, "run": g(sb, r.id)}
            if r.sweep:
                out.append({**base, "status": "not checked: curves are not yet carried across papers"})
                continue
            if not rr or not rr.ok:
                continue
            vals, free = _solve_inputs(rel, ma, mb, rr.inputs, a_own)
            if vals is None:
                out.append({**base, "status": "not checked: the mapping cannot be inverted for these inputs"})
                continue
            try:
                y = execute(la.model_code[ma_id], [{"inputs": vals, "settings": dict(ma.settings)}],
                            cache_dir=cache_dir)[0][ao]
            except (BuildError, KeyError) as e:
                out.append({**base, "status": f"not checked: {e}"})
                continue
            out_id = rr.outputs.get(bo)
            for c in _comparisons_on(lb, out_id):
                pd = _datum(lb, c.printed)
                if pd is None or pd.printed is None:
                    continue
                pp = P.parse(pd.printed)
                yv = U.convert(y, ma.outputs[ao].unit, pd.unit, ma.outputs[ao].scale, pd.scale)
                out.append({**base, "status": "checked", "printed": g(sb, c.printed), "printed_text": pd.printed,
                            "computed_value": yv, "verdict": P.verdict(yv, pp).value,
                            "own_verdict": _own_verdict(builds, sb, c.id), "own_comparison": g(sb, c.id),
                            "correspondences": _correspondences(rel, sa, ma, sb, mb),
                            "added": [f"{n} = {vals[n]:.6g} taken from {g(sa, a_own_run)}: {sb} does not state it"
                                      for n in sorted(free)]})

        # (2) b's model on a's inputs, against a's printed results
        syms = {n: sp.Symbol(n, positive=True) for n in ma.inputs}
        funcs = {bs: sp.lambdify([syms[n] for n in ma.inputs], sp.sympify(e, locals=syms), "math")
                 for bs, e in rel.mapping.items()}
        for r in sorted(a_runs, key=lambda r: r.id):
            rr = builds[sa][1].get(r.id)
            if not rr or not rr.ok:
                continue
            b_in = {bs: f(*[rr.inputs[n] for n in ma.inputs]) for bs, f in funcs.items() if bs in mb.inputs}
            try:
                y = execute(lb.model_code[mb_id], [{"inputs": b_in, "settings": dict(mb.settings)}],
                            cache_dir=cache_dir)[0][bo]
            except (BuildError, KeyError) as e:
                out.append({"relation": g(rsrc, rel.id), "model": rel.b, "on_inputs_of": sa, "run": g(sa, r.id),
                            "status": f"not checked: {e}"})
                continue
            out_id = rr.outputs.get(ao)
            for c in _comparisons_on(la, out_id):
                pd = _datum(la, c.printed)
                if pd is None or pd.printed is None:
                    continue
                pp = P.parse(pd.printed)
                yv = U.convert(y, mb.outputs[bo].unit, pd.unit, mb.outputs[bo].scale, pd.scale)
                out.append({"relation": g(rsrc, rel.id), "model": rel.b, "on_inputs_of": sa, "run": g(sa, r.id),
                            "status": "checked", "printed": g(sa, c.printed), "printed_text": pd.printed,
                            "computed_value": yv, "verdict": P.verdict(yv, pp).value,
                            "own_verdict": _own_verdict(builds, sa, c.id), "own_comparison": g(sa, c.id),
                            "correspondences": _correspondences(rel, sa, ma, sb, mb),
                            "added": [f"{vid} is added in {sa}" for vid in rr.added_inputs]})
    return sorted(out, key=lambda x: (x["relation"], x["model"], x["run"], x.get("printed", "")))


# --------------------------------------------------------------------------
# The graph, for implications
# --------------------------------------------------------------------------


def cross_id(x: dict) -> str:
    """The global id of one cross-paper check."""
    return f"cross:{x['relation']}:{x['run']}:{x.get('printed', '-')}:{x['model']}"


def _graph(records, sound, cross) -> nx.DiGraph:
    G = nx.DiGraph()
    for sid in sorted(sound):
        rec = records[sid].record
        for d in rec.data:
            G.add_node(g(sid, d.id))
            if _from_source(records[sid], d) and _cited_from(records[sid], d):
                G.add_edge(g(_cited_record(records[sid], d), _cited_from(records[sid], d)), g(sid, d.id))
        for r in rec.runs:
            for vid in {**r.inputs, **r.sweep}.values():
                G.add_edge(g(sid, vid), g(sid, r.id))
            m = model_by_id(records[sid], r.model)
            for sym in (m.outputs if m else {}):
                G.add_edge(g(sid, r.id), g(sid, r.outputs.get(sym, f"{r.id}.{sym}")))
        for c in rec.comparisons:
            G.add_edge(g(sid, c.computed), g(sid, c.id))
            G.add_edge(g(sid, c.printed), g(sid, c.id))
    for x in cross:
        if x.get("status") == "checked":
            cid = cross_id(x)
            G.add_edge(x["run"], cid)
            G.add_edge(x["printed"], cid)
    return G


# --------------------------------------------------------------------------


def build_synthesis(root: str | Path, cache_dir: Path | None = None) -> dict:
    root = Path(root)
    records, papers = _load(root)
    builds: dict[str, RecordBuild] = {}
    sound: set[str] = set()
    for sid in sorted(records):
        lr = records[sid]
        rep = validate(lr, run=False)
        b = Builder(lr, cache_dir=cache_dir).build() if rep.sound else None
        builds[sid] = b
        papers[sid] = _paper_summary(lr, b, rep)
        if papers[sid]["sound"]:
            sound.add(sid)

    # relations: tested the same way, wherever they were entered
    rels, results = {}, {}
    for sid in sorted(sound):
        for rel in records[sid].record.relations:
            key = g(sid, rel.id)
            rels[key] = (rel, sid)
            results[key] = test_relation(rel, {k: records[k] for k in sound}, source=sid, cache_dir=cache_dir)
    # relation ids are local to a record; key them globally so two records never collide
    fams = compute_families([r.model_copy(update={"id": k}) for k, (r, _) in rels.items()], results)

    cited = _cited_values(records, sound, builds)
    evaluated = {sid: (builds[sid].values, builds[sid].runs, builds[sid].comparisons) for sid in sound}
    cross = _cross_checks(records, sound, results, rels, evaluated, cache_dir)
    G = _graph(records, sound, cross)

    def implications_of(node: str) -> list[str]:
        return sorted(nx.descendants(G, node)) if node in G else []

    # ---- findings -----------------------------------------------------------
    findings = []
    for sid in sorted(sound):
        lr, b = records[sid], builds[sid]
        for c in lr.record.comparisons:
            cr = b.comparisons.get(c.id)
            if c.purpose == ComparisonPurpose.reproduction and cr and cr.ok and cr.verdict == "not reproduced":
                pd = _datum(lr, c.printed)
                findings.append({
                    "kind": "not_reproduced", "subject": g(sid, c.printed), "source": sid,
                    "detail": _not_reproduced_detail(cr, pd, b.values.get(c.printed)),
                    "page": pd.citation.page if pd else None, "quote": pd.citation.quote if pd else None,
                    "trace": sorted({g(sid, c.id), g(sid, c.computed), g(sid, c.printed)}),
                })
        for ref in b.refinements.values():
            if ref.get("belongs_to") == "numerics":
                findings.append({
                    "kind": "belongs_to_numerics", "subject": g(sid, ref["id"]), "source": sid,
                    "detail": (f"output {ref['output']} of {ref['run']} keeps changing as {ref['setting']} is refined "
                               f"(last change {_fmt(ref['changes'][-1])} > tolerance {ref['tolerance']})")
                    if not ref["settles"] else
                              (f"output {ref['output']} of {ref['run']} settles as {ref['setting']} is refined, but at "
                               f"{_fmt(ref['series'][-1]['value'])}, a change of {_shift(ref)} from "
                               f"{_fmt(ref['series'][0]['value'])} at the paper's setting (tolerance {ref['tolerance']})"),
                    "trace": [g(sid, ref["run"])],
                })
        for alt in b.alternatives:
            if alt["verdict_changes"]:
                findings.append({
                    "kind": "depends_on_added_input", "subject": g(sid, alt["added"]), "source": sid,
                    "detail": f"with {alt['added']} = {alt['alternative']} instead of {alt['baseline']}: " + "; ".join(
                        f"{c['comparison']} {c['baseline']} → {c['alternative']}" for c in alt["verdict_changes"]),
                    "trace": sorted(g(sid, c["comparison"]) for c in alt["verdict_changes"]),
                })
    for key in sorted(results):
        res = results[key]
        rel, sid = rels[key]
        if res.status == "refuted" and rel.provenance == Provenance.stated:
            findings.append({
                "kind": "refuted_relation", "subject": key, "source": sid,
                "detail": f"{sid} states {rel.a} {res.kind.replace('_', ' ')} {rel.b}; the test refutes it: {res.detail}",
                "page": rel.citation.page if rel.citation else None, "quote": rel.citation.quote if rel.citation else None,
                "trace": [rel.a, rel.b],
            })
    for x in cross:
        if x.get("status") == "checked" and x["verdict"] == "not reproduced" and x.get("own_verdict") in ("reproduced", "close"):
            findings.append({
                "kind": "family_conflict", "subject": x["printed"], "source": x["on_inputs_of"],
                "detail": f"{x['model']} on the inputs of {x['run']} gives {_fmt(x['computed_value'])}, printed {x['printed_text']}, "
                          f"though the paper's own model reproduces it",
                "trace": sorted([x["relation"], x["run"], x["printed"]]),
            })
    for c in cited:
        if c.get("verdict") == "not reproduced":
            findings.append({
                "kind": "cited_value", "subject": c["datum"], "source": c["datum"].split("/")[0],
                "detail": f"printed {c['printed']}, said to come from {c.get('cited_record', c['from_source'])}, "
                          f"which prints {c['cited_printed']}" + (f" ({c['convention']})" if c.get("convention") else ""),
                "page": c["page"], "trace": [c["datum"], g(c.get("cited_record", c["from_source"]), c["from_datum"])],
            })
    findings = _group(findings)
    for f in findings:
        f["implicates"] = [n for n in implications_of(f["subject"]) if n not in f.get("trace", [])]
    findings.sort(key=lambda f: (f["kind"], f["subject"]))

    # ---- references ---------------------------------------------------------
    refs = []
    for sid in sorted(sound):
        rec = records[sid].record
        for r in rec.references:
            settle = sorted(g(sid, q.id) for q in rec.questions if r.id in q.about or (r.source and r.source in q.about))
            refs.append({"source": sid, "id": r.id, "label": r.label, "text": r.text, "cites": r.source,
                         "in_record": bool(r.source and r.source in sound), "would_settle": settle})
    refs.sort(key=lambda r: (-len(r["would_settle"]), r["in_record"], r["source"], r["label"]))

    return {
        "papers": dict(sorted(papers.items())),
        "relations": [results[k].to_json() | {"key": k} for k in sorted(results)],
        "families": fams,
        "cross_checks": cross,
        "cited_values": cited,
        "findings": findings,
        "references": refs,
        "implications_of": implications_of,
        "builds": {sid: b.to_json() for sid, b in sorted(builds.items()) if b is not None},
    }


def _shift(ref: dict) -> str:
    """The change from the paper's setting, as a percentage when the tolerance is relative."""
    if str(ref["tolerance"]).strip().endswith("%"):
        return f"{ref['shift'] * 100:.0f}%"
    return _fmt(ref["shift"])


def _not_reproduced_detail(cr, pd, value=None) -> str:
    """What does not follow: for a table or a figure curve, the failing points by their index."""
    if not cr.per_value or pd is None or (pd.table is None and value is None):
        return f"printed {cr.printed_text}; the paper's own model and inputs give {_fmt(cr.computed_value)}"
    if pd.table is not None:
        iq, iu, idx = pd.table.index_quantity, pd.table.index_unit, list(pd.table.index)
    else:
        iq, iu, idx = value.index_quantity, value.index_unit, [f"{x:g}" for x in value.index]
    bad = [i for i, v in enumerate(cr.per_value) if v == "not reproduced"]
    rest = [v for i, v in enumerate(cr.per_value) if i not in bad and v != "no verdict"]
    unit = "" if iu in ("", "1", "dimensionless") else f" {iu}"
    rows = "; ".join(f"at {iq} = {idx[i]}{unit}, printed "
                     f"{cr.printed_text[i]}, computed {_fmt(cr.computed_value[i])}" for i in bad)
    tail = ""
    if rest:
        tail = (f"; the {len(rest)} other values reproduce" if all(v == "reproduced" for v in rest)
                else f"; of the {len(rest)} other values, " + ", ".join(
                    f"{rest.count(k)} {k}" for k in ("reproduced", "close") if rest.count(k)))
    return f"{rows}{tail}"


def _group(findings: list[dict]) -> list[dict]:
    """One finding per (kind, subject). The details of every comparison or
    alternative behind it become its evidence; traces are merged."""
    groups: dict[tuple, dict] = {}
    for f in sorted(findings, key=lambda f: (f["kind"], f["subject"], f["detail"])):
        key = (f["kind"], f["subject"])
        if key not in groups:
            groups[key] = {**f, "evidence": [f["detail"]], "trace": list(f.get("trace", []))}
        else:
            g = groups[key]
            g["evidence"].append(f["detail"])
            g["trace"] = sorted(set(g["trace"]) | set(f.get("trace", [])))
            g["page"] = g.get("page") or f.get("page")
    for g in groups.values():
        if len(g["evidence"]) > 1:
            g["detail"] = f"{g['evidence'][0]} (and {len(g['evidence']) - 1} more lines of evidence)"
    return list(groups.values())


def _fmt(x) -> str:
    if isinstance(x, list):
        return "[" + ", ".join(_fmt(v) for v in x) + "]"
    if isinstance(x, float):
        return f"{x:.4g}"
    return str(x)


def to_json(syn: dict) -> dict:
    """The synthesis as plain data, without per-record builds and helpers."""
    return {k: v for k, v in syn.items() if not callable(v) and k != "builds"}
