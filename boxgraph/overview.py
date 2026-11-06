"""The overview: a page for showing the Synthesis to someone seeing it for the first time.

It leads with a graph of the sources (papers, released code, data), placed by year and
joined by what was tested between them: relations between their models, values one
takes from another, one model run on another's inputs. Each source has a view of its
own: what was checked, its models and their relations, its open questions. A few case
studies walk one thread each from the page to a verdict; their text is written by a
person (content outside this package), and every number in them comes from the build.

The page is one HTML file with its data embedded; nothing is loaded from elsewhere
except fonts. Everything is sorted, so the same Synthesis gives the same page.
"""

from __future__ import annotations

import html
import json
import math
import shutil
from collections import Counter, defaultdict
from pathlib import Path

PURPOSES = {
    "reproduction": "A result the source prints, recomputed from its own model and inputs.",
    "validation": "A model's prediction against measurements.",
    "consistency": "Two values that should agree, compared.",
    "approximation": "A simpler model against the one it approximates.",
    "fit_quality": "A fitted curve against the data it was fitted to.",
}
# a comparison computed by a corrected variant of a misprinted model is kept apart from the paper as printed
PURPOSES |= {f"{p}, corrected": f"{d[:-1]}, computed with a corrected variant of a misprinted model: what the stated correction explains."
             for p, d in list(PURPOSES.items())}
VERDICTS = ("reproduced", "close", "not reproduced", "no verdict")
EVIDENCE = ("comparison", "relation", "cited", "cross_check", "validation", "figure", "refinement", "family", "question")


class CaseStudyError(ValueError):
    """A case study names something the build does not have."""


def _src(key: str) -> str:
    return key.split("/", 1)[0]


def _fmt(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        vals = [_fmt(x) for x in v[:6]]
        return "[" + ", ".join(vals) + (", …" if len(v) > 6 else "") + "]"
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def _cited_record(c: dict) -> str | None:
    return c.get("cited_record") or c.get("from_source")


def _label(p: dict, sid: str) -> str:
    """A source's short name: authors and year, with ', code' or ', data' for released code and data."""
    last = lambda n: str(n).split()[-1] if str(n).split() else str(n)  # noqa: E731
    a = p.get("authors") or []
    who = sid if not a else last(a[0]) if len(a) == 1 else f"{last(a[0])} & {last(a[1])}" if len(a) == 2 else f"{last(a[0])} et al."
    who += {"software": ", code", "dataset": ", data"}.get(p.get("kind") or "", "")
    return who + (f" {p['year']}" if p.get("year") else "")


def _labels(papers: dict) -> dict[str, str]:
    """Labels that two sources share are told apart as in a reference list (Shi 2013a, Shi 2013b)."""
    by: dict[str, list[str]] = defaultdict(list)
    for sid in sorted(papers):
        by[_label(papers[sid], sid)].append(sid)
    out = {}
    for lab, ids in by.items():
        for i, sid in enumerate(ids):
            out[sid] = lab if len(ids) == 1 else lab + "abcdefghijklmnopqrstuvwxyz"[i] if lab[-1:].isdigit() else f"{lab} ({sid})"
    return out


def overview_data(syn: dict) -> dict:
    """The sources, the links between them, and the families, as the page shows them."""
    papers = syn["papers"]
    rel_of = defaultdict(list)  # "src/model" -> relations to models of other sources
    links: dict[tuple, dict] = {}

    def link(a, b, kind):
        a, b = sorted((a, b))
        return links.setdefault((a, b, kind), {"a": a, "b": b, "kind": kind})

    for r in sorted(syn["relations"], key=lambda r: (r.get("key") or "", r["a"], r["b"], r["kind"])):
        sa, sb = _src(r["a"]), _src(r["b"])
        if sa == sb or sa not in papers or sb not in papers:
            continue
        x = link(sa, sb, "relation")
        x.setdefault("status", Counter())[r["status"]] += 1
        x.setdefault("kinds", Counter())[r["kind"]] += 1
        for here, other in ((r["a"], r["b"]), (r["b"], r["a"])):
            rel_of[here].append({"other": other, "kind": r["kind"], "status": r["status"],
                                 "stated": r.get("provenance") == "stated"})

    taken = defaultdict(set)  # source -> sources it takes checked values from
    for c in sorted(syn["cited_values"], key=lambda c: c["datum"]):
        s, t = _src(c["datum"]), _cited_record(c)
        if c.get("status") != "checked" or t not in papers or t == s:
            continue
        taken[s].add(t)
        x = link(s, t, "cited")
        v = c.get("verdict")
        x["agree"] = x.get("agree", 0) + (v in ("reproduced", "close"))
        x["differ"] = x.get("differ", 0) + (v == "not reproduced")
        x["unjudged"] = x.get("unjudged", 0) + (v not in ("reproduced", "close", "not reproduced"))

    for c in sorted(syn["cross_checks"], key=lambda c: (c["relation"], c.get("run") or "")):
        s, t = _src(c["model"]), c.get("on_inputs_of")
        if c.get("status") != "checked" or t not in papers or s not in papers or s == t:
            continue
        x = link(s, t, "cross_check")
        x.setdefault("verdicts", Counter())[c.get("verdict") or "no verdict"] += 1

    for v in sorted(syn.get("validations", []), key=lambda v: v["id"]):
        s, t_ = v["record"], v["against_record"]
        if v.get("status") != "checked" or t_ not in papers or s not in papers or s == t_:
            continue
        x = link(s, t_, "validation")
        x.setdefault("verdicts", Counter())[v.get("verdict") or "no verdict"] += 1

    sources = []
    labels = _labels(papers)
    for sid in sorted(papers, key=lambda k: (papers[k].get("year") or 0, k)):
        p = papers[sid]
        kind = p.get("kind") or "article"
        pv = p.get("variants") or {}
        models = [{"id": mid, "name": m.get("name"), "role": m.get("role"), "variant_of": (pv.get(mid) or {}).get("of"),
                   "relations": sorted(rel_of.get(f"{sid}/{mid}", []), key=lambda r: (r["other"], r["kind"], r["status"]))}
                  for mid, m in sorted(p.get("models", {}).items())]
        variants = [{"model": mid, "of": v["of"],
                     "corrections": [{k: c.get(k) for k in ("equation", "change", "evidence")} for c in v.get("corrections", [])],
                     "tally": {k: v.get("tally", {}).get(k, 0) for k in VERDICTS}}
                    for mid, v in sorted(pv.items())]
        verdicts = [{"comparison": v["comparison"], "purpose": v["purpose"], "printed": v.get("printed_text"),
                     "computed": _fmt(v.get("computed_value")), "verdict": v.get("verdict") or "no verdict",
                     "page": v.get("page")}
                    for v in sorted(p.get("verdicts", []), key=lambda v: (v["purpose"], v["comparison"]))]
        sources.append({
            "id": sid, "label": labels[sid], "kind": kind, "title": p.get("title"), "authors": p.get("authors") or [],
            "year": p.get("year"), "venue": p.get("venue"),
            "tally": p.get("tally", {}), "by_purpose": p.get("tally_by_purpose", {}),
            "checked": {v: sum(tp.get(v, 0) for tp in (p.get("tally_by_purpose") or {}).values()) for v in VERDICTS},
            "counts": p.get("counts", {}), "models": models, "variants": variants, "verdicts": verdicts,
            "questions": [{"id": q["id"], "kind": q.get("kind"), "text": q.get("text")} for q in p.get("questions", [])],
            "of": sorted(taken[sid]) if kind in ("software", "dataset") else [],
            "takes_from": sorted(taken[sid]),
        })

    out_links = []
    for k in sorted(links):
        x = dict(links[k])
        for f in ("status", "kinds", "verdicts"):
            if f in x:
                x[f] = dict(sorted(x[f].items()))
        out_links.append(x)
    families = sorted(({"models": sorted(f), "sources": sorted({_src(m) for m in f})} for f in syn["families"]),
                      key=lambda f: f["models"])
    return {"sources": sources, "links": out_links, "families": families}


def _weight(x: dict) -> float:
    return sum(x.get("status", {}).values()) + x.get("agree", 0) + x.get("differ", 0) + x.get("unjudged", 0) \
        + sum(x.get("verdicts", {}).values())


def layout(data: dict, width: float = 1000, height: float = 520, margin: float = 60) -> dict:
    """Positions for the graph: x by year (each year one column, in order), y relaxed towards the
    sources each one is linked to, with no two nodes overlapping. Deterministic."""
    srcs = sorted(data["sources"], key=lambda s: s["id"])
    if not srcs:
        return {}
    r = {s["id"]: round(min(26.0, 9.0 + 3.0 * math.sqrt(len(s["models"]))), 1) for s in srcs}
    years = sorted({s["year"] if s["year"] is not None else 10**6 for s in srcs})
    col = {y: i for i, y in enumerate(years)}
    gap = 10.0
    rmax = max(r.values())
    width = max(width, 2 * margin + (len(years) - 1) * (2 * rmax + gap))
    step = (width - 2 * margin) / max(len(years) - 1, 1)
    x = {s["id"]: margin + col[s["year"] if s["year"] is not None else 10**6] * step if len(years) > 1 else width / 2
         for s in srcs}
    columns = defaultdict(list)
    for s in srcs:
        columns[x[s["id"]]].append(s["id"])

    nbr = defaultdict(dict)
    for lk in data["links"]:
        w = _weight(lk)
        for a, b in ((lk["a"], lk["b"]), (lk["b"], lk["a"])):
            nbr[a][b] = nbr[a].get(b, 0) + w
    for s in srcs:  # code and data sit with the papers they belong to
        for p in s["of"]:
            nbr[s["id"]][p] = nbr[s["id"]].get(p, 0) + 50
            nbr[p][s["id"]] = nbr[p].get(s["id"], 0) + 50

    ids = [s["id"] for s in srcs]
    # start spread over the height (golden-ratio steps, so the start does not depend on luck)
    y = {i: margin + (height - 2 * margin) * ((k * 0.6180339887) % 1.0) for k, i in enumerate(ids)}
    for it in range(400):
        cool = 1.0 - it / 400
        force = {i: 0.0 for i in ids}
        for a_i, a in enumerate(ids):  # sources push each other apart, most when close
            for b in ids[a_i + 1:]:
                dx, dy = x[a] - x[b], y[a] - y[b]
                d2 = dx * dx + dy * dy + 1.0
                f = 60000.0 / d2 * (dy / math.sqrt(d2) if abs(dy) > 1e-9 else (1 if a < b else -1))
                force[a] += f
                force[b] -= f
        for a in ids:  # linked sources pull together; everything drifts to the middle
            for b, w in sorted(nbr.get(a, {}).items()):
                force[a] += 0.004 * math.log1p(w) * (y[b] - y[a])
            force[a] += 0.003 * (height / 2 - y[a])
        for a in ids:
            y[a] += max(-20.0, min(20.0, force[a])) * cool
            y[a] = min(height - margin / 2, max(margin / 2, y[a]))
    for cx in sorted(columns):  # no overlaps within a column, kept on the canvas
        col_ids = sorted(columns[cx], key=lambda i: (y[i], i))
        for a, b in zip(col_ids, col_ids[1:]):
            lo = y[a] + r[a] + r[b] + gap
            if y[b] < lo:
                y[b] = lo
        over = y[col_ids[-1]] + r[col_ids[-1]] - (height - 20)
        if over > 0:
            for i in col_ids:
                y[i] -= over
        under = 20 - (y[col_ids[0]] - r[col_ids[0]])
        if under > 0:
            for i in col_ids:
                y[i] += under
    return {s["id"]: {"x": round(x[s["id"]], 1), "y": round(y[s["id"]], 1), "r": r[s["id"]]} for s in srcs}


def full_graph(data: dict, syn: dict) -> dict:
    """The full view: every source and every model, each model hanging from its source; every tested
    relation between two models; and, between sources, the checked cited values and cross-paper runs."""
    srcs = {s["id"]: s for s in data["sources"]}
    nodes = [{"id": sid, "type": "source", "kind": s["kind"]} for sid, s in sorted(srcs.items())]
    edges = []
    for sid, s in sorted(srcs.items()):
        for m in s["models"]:
            mid = f"{sid}/{m['id']}"
            nodes.append({"id": mid, "type": "model", "source": sid, "name": m.get("name"), "role": m.get("role")})
            edges.append({"kind": "member", "a": sid, "b": mid})
    ids = {n["id"] for n in nodes}
    rels = sorted({(r["a"], r["b"], r["kind"], r["status"]) for r in syn["relations"]
                   if r["a"] in ids and r["b"] in ids})
    edges += [{"kind": "relation", "a": a, "b": b, "relation": k, "status": st} for a, b, k, st in rels]
    for lk in data["links"]:
        if lk["kind"] in ("cited", "cross_check", "validation"):
            edges.append({k: lk[k] for k in lk if k in ("kind", "a", "b", "agree", "differ", "unjudged", "verdicts")})
    nodes.sort(key=lambda n: n["id"])
    edges.sort(key=lambda e: (e["kind"], e["a"], e["b"], e.get("relation", ""), e.get("status", "")))
    return {"nodes": nodes, "edges": edges}


def full_layout(g: dict, width: float = 1000, height: float = 640, margin: float = 24) -> dict:
    """Positions for the full view, deterministic: sources start on an ellipse in id order, models
    around their source; then a fixed number of force steps (every node repels every other, edges pull
    their ends together, a model most strongly to its source) spreads them out."""
    import numpy as np

    ids = [n["id"] for n in g["nodes"]]
    if not ids:
        return {}
    k = {i: n for n, i in enumerate(ids)}
    node = {n["id"]: n for n in g["nodes"]}
    srcs = [n["id"] for n in g["nodes"] if n["type"] == "source"]
    pos = np.zeros((len(ids), 2))
    order = sorted(srcs)
    for j, s in enumerate(order):  # sources on a wide ellipse, in id order
        a = 2 * math.pi * j / max(len(order), 1)
        pos[k[s]] = (width / 2 + 0.38 * width * math.cos(a), height / 2 + 0.36 * height * math.sin(a))
    count = defaultdict(int)
    for n in g["nodes"]:
        if n["type"] == "model":
            c = count[n["source"]]
            count[n["source"]] += 1
            a = 2.399963 * c  # golden angle
            rr = 14 + 7 * math.sqrt(c)
            pos[k[n["id"]]] = pos[k[n["source"]]] + (rr * math.cos(a), rr * math.sin(a))
    ea = np.array([k[e["a"]] for e in g["edges"]], dtype=int)
    eb = np.array([k[e["b"]] for e in g["edges"]], dtype=int)
    w = np.array([3.0 if e["kind"] == "member" else 0.6 if e["kind"] == "relation" else 0.3 for e in g["edges"]])
    kk = 0.85 * math.sqrt((width - 2 * margin) * (height - 2 * margin) / len(ids))  # Fruchterman-Reingold
    temp0 = width / 10
    centre = np.array([width / 2, height / 2])
    steps = 400
    for it in range(steps):
        d = pos[:, None, :] - pos[None, :, :]
        dist = np.sqrt((d ** 2).sum(-1)) + 0.01
        disp = (d / dist[..., None] * (kk * kk / dist)[..., None]).sum(1)
        if len(ea):
            v = pos[ea] - pos[eb]
            ln = np.sqrt((v ** 2).sum(-1)) + 0.01
            pull = (v / ln[:, None]) * (w * ln * ln / kk)[:, None]
            np.add.at(disp, ea, -pull)
            np.add.at(disp, eb, pull)
        disp += 3.0 * (centre - pos)  # keeps loosely joined groups from drifting apart
        temp = temp0 * (1 - it / steps) + 0.5
        ln = np.sqrt((disp ** 2).sum(-1)) + 1e-9
        pos += disp / ln[:, None] * np.minimum(ln, temp)[:, None]
    lo, hi = pos.min(0), pos.max(0)  # unbounded while it runs; scaled to the canvas at the end
    span = np.maximum(hi - lo, 1e-9)
    side = 4 * margin  # room for a source's label beside it
    pos = np.array([side, margin]) + (pos - lo) / span * np.array([width - 2 * side, height - 2 * margin])
    rad = {i: (7.0 if node[i]["type"] == "source" else 3.0) for i in ids}
    return {i: {"x": round(float(pos[k[i], 0]), 1), "y": round(float(pos[k[i], 1]), 1), "r": rad[i]} for i in ids}


def _evidence(syn: dict, ref: str, outdir: Path, case: str) -> dict:
    kind, _, key = (part.strip() for part in ref.partition(":"))
    if kind not in EVIDENCE or not key:
        raise CaseStudyError(f"case study {case}: {ref!r} is not one of {', '.join(EVIDENCE)} followed by a name")
    papers = syn["papers"]
    if kind == "comparison":
        sid, _, cid = key.partition("/")
        v = next((v for v in papers.get(sid, {}).get("verdicts", []) if v["comparison"] == cid), None)
        if v is None:
            raise CaseStudyError(f"case study {case}: comparison {key} is not in the build")
        se = v.get("computed_se")
        return {"kind": kind, "source": sid, "id": cid, "purpose": v["purpose"], "printed": v.get("printed_text"),
                "computed": _fmt(v.get("computed_value")), "computed_2se": _fmt(2 * se) if isinstance(se, float) else None,
                "verdict": v.get("verdict") or "no verdict", "per_value": v.get("per_value"),
                "page": v.get("page"), "quote": v.get("quote")}
    if kind == "relation":
        r = next((r for r in sorted(syn["relations"], key=lambda r: (r["status"] != "verified", r["a"], r["b"]))
                  if r.get("key") == key), None)
        if r is None:
            raise CaseStudyError(f"case study {case}: relation {key} is not in the build")
        return {"kind": kind, "id": key, "relation": r["kind"], "a": r["a"], "b": r["b"], "status": r["status"],
                "stated": r.get("provenance") == "stated", "method": r.get("method"), "detail": r.get("detail")}
    if kind == "cited":
        c = next((c for c in syn["cited_values"] if c["datum"] == key), None)
        if c is None:
            raise CaseStudyError(f"case study {case}: cited value {key} is not in the build")
        sid, _, did = key.partition("/")
        frm = _cited_record(c)
        unit = papers.get(sid, {}).get("data", {}).get(did, {}).get("unit")
        cited_unit = papers.get(frm, {}).get("data", {}).get(c.get("from_datum") or "", {}).get("unit")
        return {"kind": kind, "datum": key, "from": frm, "from_datum": c.get("from_datum"),
                "unit": unit, "cited_unit": cited_unit,
                "printed": c.get("printed"), "cited_printed": c.get("cited_printed"), "status": c.get("status"),
                "verdict": c.get("verdict") or "no verdict", "page": c.get("page"), "convention": c.get("convention")}
    if kind == "cross_check":
        x = next((x for x in sorted(syn["cross_checks"], key=lambda x: x.get("run") or "") if x["relation"] == key), None)
        if x is None:
            raise CaseStudyError(f"case study {case}: cross-paper check {key} is not in the build")
        return {"kind": kind, "relation": key, "model": x["model"], "on_inputs_of": x.get("on_inputs_of"),
                "printed": x.get("printed_text"), "computed": _fmt(x.get("computed_value")),
                "verdict": x.get("verdict") or "no verdict", "added": x.get("added") or [],
                "correspondences": x.get("correspondences") or []}
    if kind == "validation":
        x = next((x for x in syn.get("validations", []) if x["id"] == key), None)
        if x is None:
            raise CaseStudyError(f"case study {case}: validation {key} is not in the build")
        return {"kind": kind, "id": key, "model": x["model"], "against": x["against"], "status": x["status"],
                "basis": x.get("basis"), "printed": x.get("printed_text"), "computed": _fmt(x.get("computed_value")),
                "verdict": x.get("verdict") or "no verdict", "per_value": x.get("per_value"),
                "correspondences": x.get("correspondences") or [], "added": x.get("added") or []}
    if kind == "refinement":
        sid, _, rid = key.partition("/")
        r = next((r for r in papers.get(sid, {}).get("refinements", []) if r["id"] == rid), None)
        if r is None:
            raise CaseStudyError(f"case study {case}: refinement {key} is not in the build")
        return {"kind": kind, "source": sid, "id": rid, "run": r.get("run"), "setting": r.get("setting"),
                "output": r.get("output"), "tolerance": r.get("tolerance"), "tolerance_basis": r.get("tolerance_basis"),
                "series": [{"setting": x["setting"], "value": x["value"]} for x in r.get("series", [])],
                "settles": r.get("settles"), "shift": _fmt(r.get("shift")), "belongs_to": r.get("belongs_to")}
    if kind == "family":
        fam = next((f for f in syn["families"] if key in f), None)
        if fam is None:
            raise CaseStudyError(f"case study {case}: no family holds the model {key}")
        models = []
        for m in sorted(fam):
            sid, _, mid = m.partition("/")
            md = papers.get(sid, {}).get("models", {}).get(mid, {})
            models.append({"key": m, "source": sid, "name": md.get("name"), "equation": md.get("equation"),
                           "page": md.get("page")})
        inside = [r for r in syn["relations"] if r["kind"] == "same_as" and r["a"] in fam and r["b"] in fam]
        return {"kind": kind, "models": models, "tested": len(inside),
                "verified": sum(r["status"] == "verified" for r in inside),
                "stated": sum(r.get("provenance") == "stated" for r in inside)}
    if kind == "question":
        sid, _, qid = key.partition("/")
        q = next((q for q in papers.get(sid, {}).get("questions", []) if q["id"] == qid), None)
        if q is None:
            raise CaseStudyError(f"case study {case}: question {key} is not in the build")
        return {"kind": kind, "source": sid, "id": qid, "question_kind": q.get("kind"), "text": q.get("text")}
    sid, _, fid = key.partition("/")
    f = next((f for f in papers.get(sid, {}).get("figures", []) if f["id"] == fid), None)
    if f is None or not f.get("overlay") or not Path(f["overlay"]).exists():
        raise CaseStudyError(f"case study {case}: figure {key} has no overlay in the build")
    name = f"img/{sid}-{fid}.png"
    (outdir / "img").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(f["overlay"], outdir / name)
    return {"kind": kind, "source": sid, "id": fid, "where": f.get("where"), "what": f.get("what"),
            "page": f.get("page"), "image": name}


def _case_studies(syn: dict, content: dict, outdir: Path) -> list[dict]:
    out = []
    for cs in content.get("case_studies") or []:
        steps = [{"text": st.get("text", ""),
                  "evidence": _evidence(syn, st["show"], outdir, cs["id"]) if st.get("show") else None}
                 for st in cs.get("steps", [])]
        out.append({"id": cs["id"], "title": cs.get("title", ""), "summary": cs.get("summary", ""),
                    "teaches": cs.get("teaches", ""), "sources": cs.get("sources", []), "steps": steps})
    return out


def render_overview(syn: dict, outdir: str | Path, title: str = "Synthesis overview", content: dict | None = None) -> Path:
    """Write the overview page (index.html, and img/ for case-study figures) into outdir."""
    outdir = Path(outdir)
    if (outdir / "img").exists():
        shutil.rmtree(outdir / "img")
    outdir.mkdir(parents=True, exist_ok=True)
    content = content or {}
    title = content.get("title") or title  # the overview's text may name the page
    data = overview_data(syn)
    data["positions"] = layout(data)
    data["full"] = full_graph(data, syn)
    data["full"]["positions"] = full_layout(data["full"])
    data["case_studies"] = _case_studies(syn, content, outdir)
    data["intro"] = content.get("intro") or []
    data["links_out"] = content.get("links") or []
    data["purposes"] = PURPOSES
    data["title"] = title
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (_PAGE.replace("__TITLE__", html.escape(title))
            .replace("__DATA__", payload))
    path = outdir / "index.html"
    path.write_text(page)
    return path


_PAGE = r"""<title>__TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a timeline of sources as the opening figure, then case studies and the source list; views by #hash. */
:root {
  --paper: #f7f8f6; --panel: #ffffff; --ink: #1d2733; --muted: #5b6672; --rule: #d8dde2; --grid: #e9ecee;
  --accent: #1f6f78; --accent-soft: #dcecee; --link: #3b4a5a; --cited: #8a6d1f;
  --ok: #2f7d4a; --near: #b07a12; --off: #b0473a; --none: #9aa3ab;
  --display: "Newsreader", "Iowan Old Style", Georgia, serif;
  --body: "Public Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #13181d; --panel: #1a2128; --ink: #e4e8ec; --muted: #9aa5b0; --rule: #2e3943; --grid: #1f272e;
  --accent: #6cc3cc; --accent-soft: #1d3a3e; --link: #a9b8c6; --cited: #d8b65a;
  --ok: #6cc28a; --near: #e0ad4a; --off: #e88576; --none: #6d7882; color-scheme: dark } }
:root[data-theme="dark"] {
  --paper: #13181d; --panel: #1a2128; --ink: #e4e8ec; --muted: #9aa5b0; --rule: #2e3943; --grid: #1f272e;
  --accent: #6cc3cc; --accent-soft: #1d3a3e; --link: #a9b8c6; --cited: #d8b65a;
  --ok: #6cc28a; --near: #e0ad4a; --off: #e88576; --none: #6d7882; color-scheme: dark }
body { background: var(--paper); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.55; }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 36px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 44px; }
h1, h2, h3 { font-family: var(--display); font-weight: 600; text-wrap: balance; margin: 0; letter-spacing: -0.005em; }
h1 { font-size: clamp(30px, 4vw, 42px); line-height: 1.1; }
h2 { font-size: 24px; }
h3 { font-size: 18px; }
p { margin: 0; }
a { color: var(--accent); }
a:focus-visible, button:focus-visible, [tabindex]:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.eyebrow { font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.lede { display: grid; gap: 12px; max-width: 70ch; color: var(--ink); font-size: 16px; }
.lede p:first-child { font-family: var(--display); font-size: 21px; line-height: 1.4; }
.lede.plain p:first-child { font-family: var(--body); font-size: 16px; line-height: 1.55; }
.muted { color: var(--muted); }
.mono { font-family: var(--mono); font-size: 0.86em; }
section { display: grid; gap: 16px; min-width: 0; }
.head { display: grid; gap: 14px; }

/* the graph */
.figure { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 20px; align-items: start; }
@media (max-width: 900px) { .figure { grid-template-columns: minmax(0, 1fr); } }
.canvas { background: var(--panel); border: 1px solid var(--rule); border-radius: 8px; overflow-x: auto; min-width: 0; }
.canvas svg { display: block; min-width: 760px; width: 100%; height: auto; }
.canvas text { font-family: var(--body); fill: var(--muted); }
.yr { font-family: var(--mono); font-size: 11px; }
.gl { stroke: var(--grid); stroke-width: 1; }
.lk { fill: none; stroke-linecap: round; transition: opacity .15s; }
.lk.relation { stroke: var(--link); }
.lk.cited { stroke: var(--cited); stroke-dasharray: 5 4; }
.lk.cross_check { stroke: var(--accent); stroke-dasharray: 1 4; }
.lk.validation { stroke: var(--accent); stroke-dasharray: 8 3 2 3; }
.nd { cursor: pointer; }
.nd .shape { fill: var(--panel); stroke: var(--ink); stroke-width: 1.5; transition: stroke-width .15s; }
.nd text.lb { font-size: 11.5px; fill: var(--ink); font-weight: 500; pointer-events: none; }
.nd:hover .shape, .nd.on .shape { stroke-width: 3; }
.nd:focus { outline: none; }
.nd:focus-visible .shape { stroke: var(--accent); stroke-width: 3; }
.dim { opacity: 0.12; }
.sat { fill: var(--accent); }
.satl { stroke: var(--accent); stroke-width: 1; opacity: .55; fill: none; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 18px; font-size: 13px; color: var(--muted); align-items: center; }
.legend span { display: inline-flex; gap: 7px; align-items: center; }
.legend svg { overflow: visible; }
.graphhead { display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; justify-content: space-between; }
.seg { display: inline-flex; border: 1px solid var(--rule); border-radius: 999px; overflow: hidden; background: var(--panel); }
.seg button { font: inherit; font-size: 13px; border: 0; background: transparent; color: var(--ink); padding: 5px 14px; cursor: pointer; }
.seg button + button { border-left: 1px solid var(--rule); }
.seg button[aria-pressed="true"] { background: var(--accent-soft); color: var(--ink); font-weight: 600; }
.mb { stroke: var(--rule); stroke-width: 0.8; }
.rl { stroke-width: 1.1; opacity: .8; }
.rl.st-verified { stroke: var(--link); }
.rl.st-not_verified, .rl.st-refuted { stroke: var(--off); }
.rl.st-unverifiable { stroke: var(--none); stroke-dasharray: 3 3; }
.nd.md .shape { fill: var(--accent); stroke: none; }
.nd.md:hover .shape, .nd.md.on .shape { stroke: var(--ink); stroke-width: 1.5; }
.mdkey { fill: var(--accent); }
.panel { background: var(--panel); border: 1px solid var(--rule); border-radius: 8px; padding: 18px; display: grid; gap: 12px;
  min-width: 0; align-content: start; }
.panel h3 { font-size: 17px; }
.panel ul { margin: 0; padding-left: 18px; display: grid; gap: 4px; font-size: 13.5px; }

/* verdict bars */
.bar { display: flex; height: 10px; border-radius: 3px; overflow: hidden; background: var(--grid); min-width: 80px; }
.bar i { display: block; height: 100%; }
.v-reproduced { background: var(--ok); } .v-close { background: var(--near); }
.v-not-reproduced { background: var(--off); } .v-no-verdict { background: var(--none); }
.pill { display: inline-block; font-size: 12px; font-weight: 600; padding: 1px 9px; border-radius: 999px; color: var(--paper); white-space: nowrap; }
.key { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 12.5px; color: var(--muted); }
.key span { display: inline-flex; gap: 6px; align-items: center; }
.key i { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }

/* case studies */
.cases { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
.case { display: grid; gap: 10px; align-content: start; padding: 18px; border: 1px solid var(--rule); border-radius: 8px;
  background: var(--panel); color: var(--ink); text-decoration: none; }
.case:hover { border-color: var(--accent); }
.case .teaches { font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); font-weight: 600; }
.pending { padding: 18px; border: 1px dashed var(--rule); border-radius: 8px; color: var(--muted); }

/* tables */
.tbl { overflow-x: auto; border: 1px solid var(--rule); border-radius: 8px; background: var(--panel); }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--rule); vertical-align: top; }
th { font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
tr:last-child td { border-bottom: 0; }
td.num { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
tbody tr.go { cursor: pointer; } tbody tr.go:hover td { background: var(--accent-soft); }

/* detail views */
.back { font-size: 14px; }
.meta { display: flex; flex-wrap: wrap; gap: 6px 16px; color: var(--muted); font-size: 14px; }
.purposes { display: grid; gap: 12px; }
.fix { display: grid; gap: 10px; padding: 14px 0; border-top: 1px solid var(--rule); }
.purpose { display: grid; grid-template-columns: 140px minmax(0, 1fr) 300px; gap: 14px; align-items: center; }
@media (max-width: 700px) { .purpose { grid-template-columns: minmax(0, 1fr); gap: 4px; } }
.purpose .what { font-size: 13px; color: var(--muted); }
.counts { font-size: 13px; font-variant-numeric: tabular-nums; color: var(--muted); }
details { border: 1px solid var(--rule); border-radius: 8px; background: var(--panel); }
details > summary { cursor: pointer; padding: 12px 16px; font-weight: 600; }
details > div { padding: 0 16px 16px; display: grid; gap: 10px; }
.q { display: grid; gap: 4px; padding: 10px 0; border-top: 1px solid var(--rule); font-size: 14px; }
.q:first-child { border-top: 0; }
.steps { display: grid; gap: 22px; counter-reset: step; max-width: 860px; }
.step { display: grid; grid-template-columns: 34px minmax(0, 1fr); gap: 14px; }
.step::before { counter-increment: step; content: counter(step); font-family: var(--display); font-size: 22px; color: var(--accent); }
.step > div { display: grid; gap: 10px; min-width: 0; }
.ev { border: 1px solid var(--rule); border-left: 3px solid var(--accent); border-radius: 6px; background: var(--panel);
  padding: 12px 14px; display: grid; gap: 8px; font-size: 14px; min-width: 0; }
.ev .row { display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: baseline; }
.ev .big { font-family: var(--mono); font-size: 15px; color: var(--ink); }
.ev img { border: 1px solid var(--rule); border-radius: 4px; }
.ev .detail { color: var(--muted); font-size: 13px; overflow-wrap: anywhere; }
footer { color: var(--muted); font-size: 13px; display: grid; gap: 6px; border-top: 1px solid var(--rule); padding-top: 18px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap" id="app"></div>
<script type="application/json" id="ov-data">__DATA__</script>
<script>
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("ov-data").textContent);
  var S = {}; D.sources.forEach(function (s) { S[s.id] = s; });
  var app = document.getElementById("app");
  var esc = function (t) { return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) {
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); };
  var VERD = ["reproduced", "close", "not reproduced", "no verdict"];
  var vclass = function (v) { return "v-" + String(v || "no verdict").replace(/ /g, "-"); };
  var pill = function (v) { return '<span class="pill ' + vclass(v) + '">' + esc(v || "no verdict") + "</span>"; };
  var kindName = {article: "paper", software: "released code", dataset: "source data", this_work: "this work"};
  var relName = {same_as: "same model", reduces_to: "reduces to", derived_from: "derived from",
                 scales_as: "scales as", approximated_by: "approximated by"};
  var statusName = {verified: "verified", not_verified: "not verified", refuted: "refuted", unverifiable: "could not be tested"};

  function short(s) { return s.label || baseShort(s); }
  function baseShort(s) {
    var a = s.authors || [];
    var last = function (n) { var p = String(n).trim().split(/\s+/); return p[p.length - 1]; };
    var who = a.length === 0 ? s.id : a.length === 1 ? last(a[0]) : a.length === 2 ? last(a[0]) + " & " + last(a[1]) : last(a[0]) + " et al.";
    if (s.kind === "software") who += ", code";
    if (s.kind === "dataset") who += ", data";
    return who + (s.year ? " " + s.year : "");
  }
  function bar(t) {
    var n = VERD.reduce(function (a, v) { return a + (t[v] || 0); }, 0);
    if (!n) return '<div class="bar" title="nothing compared"></div>';
    return '<div class="bar" role="img" aria-label="' + VERD.map(function (v) { return (t[v] || 0) + " " + v; }).join(", ") + '">' +
      VERD.map(function (v) { return t[v] ? '<i class="' + vclass(v) + '" style="width:' + (100 * t[v] / n) + '%"></i>' : ""; }).join("") + "</div>";
  }
  function counts(t) {
    return VERD.map(function (v) { return (t[v] || 0) + " " + v; }).join(" · ");
  }
  var KEY = '<div class="key">' + VERD.map(function (v) { return '<span><i class="' + vclass(v) + '"></i>' + v + "</span>"; }).join("") + "</div>";

  // ---------- the graph ----------
  function graph() {
    var P = D.positions, ids = Object.keys(P);
    var W = 0, H = 520;
    ids.forEach(function (i) { W = Math.max(W, P[i].x + 70); });
    W = Math.max(W, 1000);
    var years = {}; D.sources.forEach(function (s) { if (s.year) years[P[s.id].x] = s.year; });
    var g = ['<svg viewBox="0 0 ' + W + " " + (H + 30) + '" role="img" aria-label="Sources placed by year and joined by what was tested between them">'];
    Object.keys(years).forEach(function (x) {
      g.push('<line class="gl" x1="' + x + '" y1="14" x2="' + x + '" y2="' + (H - 6) + '"/>');
      g.push('<text class="yr" x="' + x + '" y="' + (H + 18) + '" text-anchor="middle">' + years[x] + "</text>");
    });
    var seen = {};
    D.links.forEach(function (l, i) {
      var a = P[l.a], b = P[l.b]; if (!a || !b) return;
      var pair = l.a + "|" + l.b; var k = seen[pair] = (seen[pair] || 0) + 1;
      var n = (l.status ? Object.values(l.status).reduce(function (x, y) { return x + y; }, 0) : 0) +
              (l.agree || 0) + (l.differ || 0) + (l.unjudged || 0) +
              (l.verdicts ? Object.values(l.verdicts).reduce(function (x, y) { return x + y; }, 0) : 0);
      var w = Math.min(5, 1 + Math.log2(1 + n));
      var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2, dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1;
      var bend = (k - 2) * 26 + (a.x === b.x ? 60 : 0);
      var cx = mx - dy / len * bend, cy = my + dx / len * bend;
      g.push('<path class="lk ' + l.kind + '" data-a="' + esc(l.a) + '" data-b="' + esc(l.b) + '" stroke-width="' + w.toFixed(2) +
             '" d="M' + a.x + " " + a.y + " Q" + cx.toFixed(1) + " " + cy.toFixed(1) + " " + b.x + " " + b.y + '"><title>' + esc(linkText(l)) + "</title></path>");
    });
    g.push('<g id="sats"></g>');
    D.sources.forEach(function (s) {
      var p = P[s.id], r = p.r, shape;
      if (s.kind === "software") shape = '<rect class="shape" x="' + (p.x - r * 0.86) + '" y="' + (p.y - r * 0.86) + '" width="' + (r * 1.72) + '" height="' + (r * 1.72) + '" rx="3"/>';
      else if (s.kind === "dataset") shape = '<path class="shape" d="M' + p.x + " " + (p.y - r) + " L" + (p.x + r) + " " + p.y + " L" + p.x + " " + (p.y + r) + " L" + (p.x - r) + " " + p.y + ' Z"/>';
      else shape = '<circle class="shape" cx="' + p.x + '" cy="' + p.y + '" r="' + r + '"/>';
      g.push('<g class="nd" tabindex="0" role="button" data-id="' + esc(s.id) + '" aria-label="' + esc(short(s)) + '">' +
             shape +
             '<text class="lb" x="' + p.x + '" y="' + (p.y + r + 14) + '" text-anchor="middle">' + esc(short(s)) + "</text></g>");
    });
    g.push("</svg>");
    return g.join("");
  }
  function linkText(l) {
    var A = short(S[l.a]), B = short(S[l.b]);
    if (l.kind === "relation") return A + " – " + B + ": " + Object.keys(l.status).map(function (k) { return l.status[k] + " " + (statusName[k] || k); }).join(", ") + " model relation(s) tested";
    if (l.kind === "cited") return A + " – " + B + ": values taken from one and checked against the other: " + (l.agree || 0) + " agree, " + (l.differ || 0) + " differ" + (l.unjudged ? ", " + l.unjudged + " without a verdict" : "");
    if (l.kind === "validation") return A + " – " + B + ": a model of one judged against measurements of the other (" + Object.keys(l.verdicts).map(function (k) { return l.verdicts[k] + " " + k; }).join(", ") + ")";
    return A + " – " + B + ": a model of one run on the inputs of the other (" + Object.keys(l.verdicts).map(function (k) { return l.verdicts[k] + " " + k; }).join(", ") + ")";
  }
  function panelFor(id) {
    var s = S[id];
    var rels = [];
    s.models.forEach(function (m) { m.relations.forEach(function (r) { rels.push([m, r]); }); });
    var byOther = {};
    rels.forEach(function (x) { var o = x[1].other.split("/")[0]; (byOther[o] = byOther[o] || []).push(x); });
    var rows = Object.keys(byOther).sort().map(function (o) {
      var xs = byOther[o], ver = xs.filter(function (x) { return x[1].status === "verified"; }).length;
      return "<li>" + esc(short(S[o])) + ": " + xs.length + " relation" + (xs.length > 1 ? "s" : "") + " tested, " + ver + " verified</li>";
    }).join("");
    var from = (s.takes_from || []).map(function (t) { return esc(short(S[t])); }).join(", ");
    return '<div class="eyebrow">' + esc(kindName[s.kind] || s.kind) + "</div>" +
      "<h3>" + esc(s.title) + "</h3>" +
      '<div class="muted">' + esc((s.authors || []).join(", ")) + (s.year ? " · " + s.year : "") + "</div>" +
      bar(s.checked) + '<div class="counts">' + counts(s.checked) + "</div>" +
      "<div>" + s.models.length + " model" + (s.models.length === 1 ? "" : "s") + ", " + (s.counts.data || 0) + " values, " + s.questions.length + " open questions</div>" +
      (rows ? '<div><div class="eyebrow">Models related to</div><ul>' + rows + "</ul></div>" : "") +
      (from ? '<div><div class="eyebrow">Takes checked values from</div><div>' + from + "</div></div>" : "") +
      '<a href="#source-' + esc(s.id) + '">Open the full view of this source</a>';
  }
  var VIEW = "full";
  try { var saved = localStorage.getItem("overview-view"); if (saved === "full" || saved === "sources") VIEW = saved; } catch (e) {}
  function shapeFor(kind, x, y, r) {
    if (kind === "software") return '<rect class="shape" x="' + (x - r * 0.86) + '" y="' + (y - r * 0.86) + '" width="' + (r * 1.72) + '" height="' + (r * 1.72) + '" rx="2"/>';
    if (kind === "dataset") return '<path class="shape" d="M' + x + " " + (y - r) + " L" + (x + r) + " " + y + " L" + x + " " + (y + r) + " L" + (x - r) + " " + y + ' Z"/>';
    return '<circle class="shape" cx="' + x + '" cy="' + y + '" r="' + r + '"/>';
  }
  function fullGraph() {
    var F = D.full, P = F.positions, W = 1000, H = 640, N = {};
    F.nodes.forEach(function (n) { N[n.id] = n; });
    var g = ['<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Every source and model, joined by everything that was tested between them">'];
    F.edges.forEach(function (e) {
      var a = P[e.a], b = P[e.b]; if (!a || !b) return;
      var cls = e.kind === "member" ? "mb" : e.kind === "relation" ? "rl st-" + e.status : "lk " + e.kind;
      var tip = e.kind === "relation" ? e.a + " " + (relName[e.relation] || e.relation) + " " + e.b + " (" + (statusName[e.status] || e.status) + ")"
        : e.kind === "member" ? "" : linkText(e);
      g.push('<line class="' + cls + '" data-a="' + esc(e.a) + '" data-b="' + esc(e.b) + '" x1="' + a.x + '" y1="' + a.y + '" x2="' + b.x + '" y2="' + b.y + '">' + (tip ? "<title>" + esc(tip) + "</title>" : "") + "</line>");
    });
    F.nodes.forEach(function (n) {
      var p = P[n.id];
      if (n.type === "model") {
        g.push('<g class="nd md" tabindex="0" role="button" data-id="' + esc(n.id) + '" aria-label="' + esc(n.name || n.id) + '"><circle class="shape" cx="' + p.x + '" cy="' + p.y + '" r="' + p.r + '"/><title>' + esc((n.name || n.id) + " (" + short(S[n.source]) + ")") + "</title></g>");
      }
    });
    F.nodes.forEach(function (n) {
      var p = P[n.id];
      if (n.type === "source") {
        g.push('<g class="nd" tabindex="0" role="button" data-id="' + esc(n.id) + '" aria-label="' + esc(short(S[n.id])) + '">' + shapeFor(n.kind, p.x, p.y, p.r) +
               '<text class="lb" x="' + p.x + '" y="' + (p.y - p.r - 5) + '" text-anchor="middle">' + esc(short(S[n.id])) + "</text></g>");
      }
    });
    g.push("</svg>");
    return g.join("");
  }
  function modelPanel(id) {
    var sid = id.split("/")[0], mid = id.split("/").slice(1).join("/"), s = S[sid];
    var m = s.models.filter(function (x) { return x.id === mid; })[0] || {relations: []};
    var rels = D.full.edges.filter(function (e) { return e.kind === "relation" && (e.a === id || e.b === id); });
    return '<div class="eyebrow">Model · ' + esc(m.role || "") + "</div><h3>" + esc(m.name || mid) + "</h3>" +
      '<div class="muted">From <a href="#source-' + esc(sid) + '">' + esc(short(s)) + '</a> · <span class="mono">' + esc(mid) + "</span></div>" +
      (rels.length ? '<div><div class="eyebrow">Relations tested</div><ul>' + rels.map(function (e) {
        var other = e.a === id ? e.b : e.a, dir = e.a === id ? (relName[e.relation] || e.relation) : (relName[e.relation] || e.relation) + " (from the other side)";
        return "<li>" + esc(dir) + ' <span class="mono">' + esc(other) + "</span> · " + esc(statusName[e.status] || e.status) + "</li>"; }).join("") + "</ul></div>"
        : '<p class="muted">No relation to another model was tested.</p>');
  }
  function select(id) {
    var svg = app.querySelector(".canvas svg"); if (!svg) return;
    var near = {}; near[id] = 1;
    svg.querySelectorAll("[data-a]").forEach(function (e) {
      var on = e.dataset.a === id || e.dataset.b === id;
      if (on) { near[e.dataset.a] = 1; near[e.dataset.b] = 1; }
      e.classList.toggle("dim", !on);
    });
    if (VIEW === "full" && S[id]) {  // a source: its models, and what they are related to
      svg.querySelectorAll("[data-a]").forEach(function (e) {
        if (e.dataset.a === id || e.dataset.b === id) return;
        var mine = e.dataset.a.split("/")[0] === id || e.dataset.b.split("/")[0] === id;
        if (mine) { near[e.dataset.a] = 1; near[e.dataset.b] = 1; e.classList.remove("dim"); }
      });
    }
    svg.querySelectorAll(".nd").forEach(function (e) {
      e.classList.toggle("dim", !near[e.dataset.id]); e.classList.toggle("on", e.dataset.id === id);
    });
    var sats = svg.querySelector("#sats");
    if (sats && S[id]) {  // the sources view: the selected source opens into its models
      var P = D.positions, p = P[id], s = S[id], out = [], ms = s.models, n = ms.length;
      ms.forEach(function (m, i) {
        var a = -Math.PI / 2 + 2 * Math.PI * i / Math.max(n, 1), R = p.r + 16;
        var mx = p.x + R * Math.cos(a), my = p.y + R * Math.sin(a);
        m.relations.forEach(function (r) { var q = P[r.other.split("/")[0]]; if (q) out.push('<path class="satl" d="M' + mx.toFixed(1) + " " + my.toFixed(1) + " L" + q.x + " " + q.y + '"><title>' + esc(m.name + " — " + (relName[r.kind] || r.kind) + " — " + r.other + " (" + (statusName[r.status] || r.status) + ")") + "</title></path>"); });
        out.push('<circle class="sat" cx="' + mx.toFixed(1) + '" cy="' + my.toFixed(1) + '" r="3.2"><title>' + esc(m.name || m.id) + "</title></circle>");
      });
      sats.innerHTML = out.join("");
    }
    app.querySelector(".panel").innerHTML = S[id] ? panelFor(id) : modelPanel(id);
  }
  function clearSel() {
    var svg = app.querySelector(".canvas svg");
    svg.querySelectorAll(".dim").forEach(function (e) { e.classList.remove("dim"); });
    svg.querySelectorAll(".nd").forEach(function (e) { e.classList.remove("on"); });
    var sats = svg.querySelector("#sats"); if (sats) sats.innerHTML = "";
    app.querySelector(".panel").innerHTML = defaultPanel();
  }
  function defaultPanel() {
    if (VIEW === "full") {
      var nm = D.full.nodes.filter(function (n) { return n.type === "model"; }).length;
      var nr = D.full.edges.filter(function (e) { return e.kind === "relation"; }).length;
      return '<div class="eyebrow">How to read this</div>' +
        "<p>Everything at once: " + D.sources.length + " sources (larger marks) and their " + nm + " models (small dots), each model joined to its source by a faint line.</p>" +
        "<p>The " + nr + " relations tested between models are drawn between their dots: verified (dark), not verified or refuted (red), or not testable (grey). Between sources, dashed lines are values one takes from another, checked; dotted lines are a model run on another source's inputs; dash-dot lines are a model judged against another source's measurements.</p>" +
        "<p>Select a source or a model to follow its connections.</p>";
    }
    return '<div class="eyebrow">How to read this</div>' +
      "<p>Each mark is a source: a paper (circle), the code released with one (square), or its source data (diamond). Sources are placed by year, left to right.</p>" +
      "<p>Lines join sources where something was tested between them: a relation between their models (solid), a value one takes from the other, checked against it (dashed), one model run on the other's inputs (dotted), or one model judged against the other's measurements (dash-dot). Thicker lines carry more checks.</p>" +
      "<p>Select a source to see what connects it, and its models around it. " + D.links.length + " links in all.</p>";
  }
  function legend() {
    var line = function (cls, w) { return '<svg width="26" height="10"><line x1="0" y1="5" x2="26" y2="5" class="' + cls + '" stroke-width="' + w + '"/></svg>'; };
    if (VIEW === "full") return '<span><svg width="12" height="10"><circle cx="6" cy="5" r="3" class="mdkey"/></svg>a model</span>' +
      "<span>" + line("mb", 1) + "model of a source</span><span>" + line("rl st-verified", 1.5) + "relation verified</span>" +
      "<span>" + line("rl st-not_verified", 1.5) + "not verified or refuted</span><span>" + line("rl st-unverifiable", 1.5) + "not testable</span>" +
      "<span>" + line("lk cited", 2) + "values taken and checked</span><span>" + line("lk cross_check", 2) + "a model run on another's inputs</span>" + "<span>" + line("lk validation", 2) + "a model against another's measurements</span>";
    return "<span>" + line("lk relation", 2) + "model relations tested</span><span>" + line("lk cited", 2) + "values taken and checked</span><span>" + line("lk cross_check", 2) + "a model run on another's inputs</span>" + "<span>" + line("lk validation", 2) + "a model against another's measurements</span>";
  }
  function renderGraph() {
    app.querySelector(".canvas").innerHTML = VIEW === "full" ? fullGraph() : graph();
    app.querySelector(".panel").innerHTML = defaultPanel();
    app.querySelector(".legend").innerHTML = legend();
    ["full", "sources"].forEach(function (v) { app.querySelector("#view-" + v).setAttribute("aria-pressed", VIEW === v ? "true" : "false"); });
    app.querySelectorAll(".canvas .nd").forEach(function (e) {
      e.addEventListener("click", function () { select(e.dataset.id); });
      e.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); select(e.dataset.id); } });
    });
    app.querySelector(".canvas svg").addEventListener("click", function (ev) { if (ev.target.tagName === "svg") clearSel(); });
  }
  function setView(v) {
    VIEW = v;
    try { localStorage.setItem("overview-view", v); } catch (e) {}
    renderGraph();
  }

  // ---------- views ----------
  function home() {
    var paras = (D.intro || []).map(function (p) { return "<p>" + esc(p) + "</p>"; });
    var lead = paras.slice(0, 1).join(""), more = paras.slice(1).join("");
    var nArt = D.sources.filter(function (s) { return s.kind !== "software" && s.kind !== "dataset"; }).length;
    var nOther = D.sources.length - nArt;
    var cases = D.case_studies.length ? D.case_studies.map(function (c) {
      return '<a class="case" href="#case-' + esc(c.id) + '">' + (c.teaches ? '<div class="teaches">' + esc(c.teaches) + "</div>" : "") +
        "<h3>" + esc(c.title) + "</h3><p class=\"muted\">" + esc(c.summary) + "</p></a>"; }).join("")
      : '<div class="pending">Case studies will appear here.</div>';
    var rows = D.sources.map(function (s) {
      return '<tr class="go" data-href="#source-' + esc(s.id) + '"><td><a href="#source-' + esc(s.id) + '">' + esc(short(s)) + '</a><div class="muted">' + esc(s.title) + "</div></td>" +
        "<td>" + esc(kindName[s.kind] || s.kind) + '</td><td class="num">' + s.models.length + '</td><td class="num">' + s.verdicts.length + "</td><td>" + bar(s.checked) + "</td></tr>"; }).join("");
    var outl = (D.links_out || []).map(function (l) { return '<a href="' + esc(l.href) + '" target="_blank" rel="noopener">' + esc(l.text) + "</a>"; }).join(" · ");
    app.innerHTML =
      '<header class="head"><div class="eyebrow">' + nArt + " papers · " + nOther + " sources of code and data · " + D.links.length + " tested links</div>" +
      "<h1>" + esc(D.title) + '</h1><div class="lede">' + lead + "</div></header>" +
      '<section aria-labelledby="g-h"><div class="graphhead"><h2 id="g-h" class="eyebrow" style="font-family:var(--body);font-size:12px">What was tested, and between what</h2>' +
      '<div class="seg" role="group" aria-label="View"><button type="button" id="view-full" aria-pressed="false">Everything</button><button type="button" id="view-sources" aria-pressed="false">Sources only</button></div></div>' +
      '<div class="figure"><div class="canvas"></div><aside class="panel" aria-live="polite"></aside></div>' +
      '<div class="legend"></div></section>' +
      (more ? '<section aria-labelledby="a-h"><h2 id="a-h">How the review works</h2><div class="lede plain">' + more + "</div></section>" : "") +
      '<section aria-labelledby="c-h"><h2 id="c-h">Case studies</h2><p class="muted" style="max-width:70ch">Each one follows a single thread from what a paper prints to what the record finds.</p><div class="cases">' + cases + "</div></section>" +
      '<section aria-labelledby="s-h"><h2 id="s-h">The sources</h2>' + KEY +
      '<div class="tbl"><table><thead><tr><th>Source</th><th>Kind</th><th class="num">Models</th><th class="num">Comparisons</th><th>Verdicts</th></tr></thead><tbody>' + rows + "</tbody></table></div></section>" +
      "<footer><div>A verdict is computed at the precision the value was printed with. It says whether a result follows from its stated inputs, not whether it is right about the world.</div>" +
      (outl ? "<div>" + outl + "</div>" : "") + "</footer>";
    app.querySelector("#view-full").addEventListener("click", function () { setView("full"); });
    app.querySelector("#view-sources").addEventListener("click", function () { setView("sources"); });
    renderGraph();
    app.querySelectorAll("tr.go").forEach(function (tr) { tr.addEventListener("click", function (ev) { if (ev.target.tagName !== "A") location.hash = tr.dataset.href; }); });
  }

  // values read from a figure each carry their interval and where they were read; show the values, name the figure once
  function plist(p) {
    if (!Array.isArray(p)) return esc(p);
    var m = /read from (.+)$/.exec(String(p[0] || ""));
    var v = p.slice(0, 6).map(function (x) { return String(x).split(" [")[0]; });
    return esc("[" + v.join(", ") + (p.length > 6 ? ", …" : "") + "]") + (m ? ' <span class="muted">read from ' + esc(m[1]) + "</span>" : "");
  }

  function sourceView(id) {
    var s = S[id];
    if (!s) return home();
    var order = Object.keys(D.purposes);
    var purposes = Object.keys(s.by_purpose).sort(function (a, b) { var i = order.indexOf(a), j = order.indexOf(b);
      return (i < 0 ? 99 : i) - (j < 0 ? 99 : j) || (a < b ? -1 : 1); }).map(function (p) {
      var t = s.by_purpose[p];
      return '<div class="purpose"><div><b>' + esc(p.replace("_", " ")) + '</b></div><div class="what">' + esc(D.purposes[p] || "") + "</div><div>" + bar(t) + '<div class="counts">' + counts(t) + "</div></div></div>"; }).join("");
    var models = s.models.map(function (m) {
      var rels = m.relations.map(function (r) { var o = r.other.split("/")[0];
        return '<div>' + esc(relName[r.kind] || r.kind) + ' <a href="#source-' + esc(o) + '">' + esc(short(S[o])) + "</a> <span class=\"mono\">" + esc(r.other.split("/")[1]) + "</span> · " + esc(statusName[r.status] || r.status) + (r.stated ? " (stated by the paper)" : "") + "</div>"; }).join("");
      return "<tr><td>" + esc(m.name || m.id) + '<div class="mono muted">' + esc(m.id) + "</div></td><td>" + (m.variant_of ? "corrected variant of <span class=\"mono\">" + esc(m.variant_of) + "</span>" : esc(m.role || "")) + "</td><td>" + (rels || '<span class="muted">none tested</span>') + "</td></tr>"; }).join("");
    var vrows = s.verdicts.map(function (v) {
      return '<tr><td class="mono">' + esc(v.comparison) + "</td><td>" + esc(v.purpose.replace("_", " ")) + '</td><td class="mono">' + esc(v.printed) + '</td><td class="mono">' + esc(v.computed) + "</td><td>" + pill(v.verdict) + '</td><td class="num">' + esc(v.page || "") + "</td></tr>"; }).join("");
    var fixes = (s.variants || []).map(function (v) {
      var cs = v.corrections.map(function (c) { return '<div class="q"><div class="eyebrow">' + esc(c.equation) + "</div><div><b>" + esc(c.change) + '</b></div><div class="muted">' + esc(c.evidence) + "</div></div>"; }).join("");
      return '<div class="fix"><div class="row"><span class="mono">' + esc(v.model) + '</span> <span class="muted">corrects</span> <span class="mono">' + esc(v.of) + "</span></div>" + cs +
        "<div>" + bar(v.tally) + '<div class="counts">' + counts(v.tally) + " (comparisons computed with the corrected variant)</div></div></div>"; }).join("");
    var qs = s.questions.map(function (q) { return '<div class="q"><div class="eyebrow">' + esc((q.kind || "").replace(/_/g, " ")) + '</div><div>' + esc(q.text) + "</div></div>"; }).join("");
    var from = (s.takes_from || []).map(function (t) { return '<a href="#source-' + esc(t) + '">' + esc(short(S[t])) + "</a>"; }).join(", ");
    app.innerHTML = '<a class="back" href="#overview">← Back to the overview</a>' +
      '<header class="head"><div class="eyebrow">' + esc(kindName[s.kind] || s.kind) + "</div><h1>" + esc(s.title) + "</h1>" +
      '<div class="meta"><span>' + esc((s.authors || []).join(", ")) + "</span>" + (s.year ? "<span>" + s.year + "</span>" : "") + (s.venue ? "<span>" + esc(s.venue) + "</span>" : "") + "</div></header>" +
      '<section><h2>What was checked</h2>' + KEY + '<div class="purposes">' + (purposes || '<p class="muted">Nothing in this source is compared with a computed value.</p>') + "</div>" +
      (from ? "<p>Takes values from " + from + ", each checked against the source it comes from.</p>" : "") + "</section>" +
      '<section><h2>Models</h2><div class="tbl"><table><thead><tr><th>Model</th><th>Role</th><th>Tested relations to other sources</th></tr></thead><tbody>' + (models || '<tr><td colspan="3" class="muted">No models.</td></tr>') + "</tbody></table></div></section>" +
      (fixes ? '<section><h2>Corrections</h2><p class="muted" style="max-width:70ch">Where an equation is evidently misprinted, the record keeps the model as printed and adds a corrected variant beside it, with the evidence for the correction. The paper\'s own tally above counts only the model as printed.</p>' + fixes + "</section>" : "") +
      '<section><h2>Every comparison</h2><details><summary>' + s.verdicts.length + ' comparisons, each with the printed and the computed value</summary><div><div class="tbl"><table><thead><tr><th>Comparison</th><th>Purpose</th><th>Printed</th><th>Computed</th><th>Verdict</th><th class="num">Page</th></tr></thead><tbody>' + vrows + "</tbody></table></div></div></details></section>" +
      '<section><h2>Open questions</h2><details><summary>' + s.questions.length + " questions the record leaves open</summary><div>" + qs + "</div></details></section>";
    window.scrollTo(0, 0);
  }

  function num(v) {
    if (Array.isArray(v)) return "[" + v.slice(0, 5).map(num).join(", ") + (v.length > 5 ? ", …" : "") + "]";
    return typeof v === "number" ? esc(Number(v.toPrecision(4))) : esc(v);
  }
  function evidence(e) {
    if (!e) return "";
    var src = function (k) { var sid = k.split("/")[0]; return S[sid] ? '<a href="#source-' + esc(sid) + '">' + esc(short(S[sid])) + "</a>" : esc(sid); };
    if (e.kind === "comparison") return '<div class="ev"><div class="row"><span class="eyebrow">' + esc(e.purpose.replace("_", " ")) + "</span>" + src(e.source) + (e.page ? '<span class="muted">p. ' + esc(e.page) + "</span>" : "") + "</div>" +
      '<div class="row"><span>Printed <span class="big">' + plist(e.printed) + '</span></span><span>Computed <span class="big">' + esc(e.computed) + (e.computed_2se ? " ± " + esc(e.computed_2se) : "") + "</span></span>" + pill(e.verdict) + "</div>" +
      (e.quote ? '<div class="detail">“' + esc(e.quote) + "”</div>" : "") + "</div>";
    if (e.kind === "relation") return '<div class="ev"><div class="row"><span class="eyebrow">' + esc(relName[e.relation] || e.relation) + (e.stated ? " · stated by the paper" : " · proposed by the reader") + "</span></div>" +
      '<div class="row"><span class="mono">' + esc(e.a) + "</span> → <span class=\"mono\">" + esc(e.b) + "</span><span>" + esc(statusName[e.status] || e.status) + "</span></div>" +
      (e.detail ? '<div class="detail">' + esc(e.detail) + "</div>" : "") + "</div>";
    if (e.kind === "cited") return '<div class="ev"><div class="row"><span class="eyebrow">A value taken from another source</span>' + src(e.datum) + " takes it from " + src(e.from || "") + "</div>" +
      '<div class="row"><span>Here <span class="big">' + esc(e.printed) + (e.unit ? " " + esc(e.unit) : "") + '</span></span><span>In the source <span class="big">' + esc(e.cited_printed) + (e.cited_unit ? " " + esc(e.cited_unit) : "") + "</span></span>" + pill(e.verdict) + "</div>" +
      (e.convention ? '<div class="detail">' + esc(e.convention) + "</div>" : "") + "</div>";
    if (e.kind === "cross_check") return '<div class="ev"><div class="row"><span class="eyebrow">A model run on another source\'s inputs</span></div>' +
      '<div class="row"><span class="mono">' + esc(e.model) + "</span> on the inputs of " + src(e.on_inputs_of + "/") + "</div>" +
      '<div class="row"><span>Printed <span class="big">' + plist(e.printed) + '</span></span><span>Computed <span class="big">' + esc(e.computed) + "</span></span>" + pill(e.verdict) + "</div>" +
      (e.added.length ? '<div class="detail">Inputs added: ' + esc(e.added.join("; ")) + "</div>" : "") + "</div>";
    if (e.kind === "validation") return '<div class="ev"><div class="row"><span class="eyebrow">A model against another paper\'s measurement</span></div>' +
      '<div class="row"><span class="mono">' + esc(e.model) + "</span> against " + src(e.against) + ' <span class="mono">' + esc(e.against.split("/").slice(1).join("/")) + "</span></div>" +
      (e.status === "checked" ? '<div class="row"><span>Measured <span class="big">' + plist(e.printed) + '</span></span><span>Predicted <span class="big">' + esc(e.computed) + "</span></span>" + pill(e.verdict) + "</div>"
        : '<div class="detail">' + esc(e.status) + "</div>") +
      '<div class="detail">Why this model should predict it: ' + esc(e.basis) + "</div>" +
      (e.correspondences.length ? '<div class="detail">Taken as the same quantity: ' + esc(e.correspondences.join("; ")) + "</div>" : "") + "</div>";
    if (e.kind === "refinement") return '<div class="ev"><div class="row"><span class="eyebrow">A numerical setting refined</span>' + src(e.source) + "</div>" +
      '<div class="tbl"><table><thead><tr><th>' + esc(e.setting) + '</th><th>' + esc(e.output) + "</th></tr></thead><tbody>" +
      e.series.map(function (x, i) { return '<tr><td class="mono">' + num(x.setting) + (i === 0 ? ' <span class="muted">(the paper\'s setting)</span>' : "") + '</td><td class="mono">' + num(x.value) + "</td></tr>"; }).join("") + "</tbody></table></div>" +
      '<div class="row"><span>' + (e.settles ? "Settles" : "Does not settle") + "; the value at the paper's setting is " + (e.belongs_to === "model" ? "within" : "outside") + " the tolerance (" + esc(e.tolerance) + ") of where it settles.</span>" +
      '<span class="pill ' + (e.belongs_to === "model" ? "v-reproduced" : "v-close") + '">belongs to the ' + esc(e.belongs_to) + "</span></div>" +
      (e.tolerance_basis ? '<div class="detail">Tolerance: ' + esc(e.tolerance_basis) + "</div>" : "") + "</div>";
    if (e.kind === "family") return '<div class="ev"><div class="row"><span class="eyebrow">A family in ModelAtlas</span><span>' + e.models.length + " models · " + e.tested + " pairs tested, " + e.verified + " verified, " + e.stated + " stated by a paper</span></div>" +
      '<div class="tbl"><table><thead><tr><th>Source</th><th>As the paper writes it</th></tr></thead><tbody>' +
      e.models.map(function (m) { return "<tr><td>" + src(m.key) + '<div class="muted">' + esc(m.name) + '</div></td><td class="mono">' + esc(m.equation) + (m.page ? ' <span class="muted">p. ' + esc(m.page) + "</span>" : "") + "</td></tr>"; }).join("") + "</tbody></table></div></div>";
    if (e.kind === "question") return '<div class="ev"><div class="row"><span class="eyebrow">Open question · ' + esc((e.question_kind || "").replace(/_/g, " ")) + "</span>" + src(e.source) + "</div>" +
      "<div>" + esc(e.text) + "</div></div>";
    if (e.kind === "figure") return '<div class="ev"><div class="row"><span class="eyebrow">' + esc(e.where) + "</span>" + src(e.source) + "</div>" +
      '<img src="' + esc(e.image) + '" alt="' + esc(e.what) + '" loading="lazy"><div class="detail">' + esc(e.what) + "</div></div>";
    return "";
  }
  function caseView(id) {
    var c = D.case_studies.filter(function (x) { return x.id === id; })[0];
    if (!c) return home();
    app.innerHTML = '<a class="back" href="#overview">← Back to the overview</a>' +
      '<header class="head">' + (c.teaches ? '<div class="eyebrow">' + esc(c.teaches) + "</div>" : "") + "<h1>" + esc(c.title) + '</h1><div class="lede"><p>' + esc(c.summary) + "</p></div></header>" +
      '<section><div class="steps">' + c.steps.map(function (st) { return '<div class="step"><div><p>' + esc(st.text) + "</p>" + evidence(st.evidence) + "</div></div>"; }).join("") + "</div></section>";
    window.scrollTo(0, 0);
  }

  function route() {
    var h = (location.hash || "").slice(1);
    if (h.indexOf("source-") === 0) return sourceView(h.slice(7));
    if (h.indexOf("case-") === 0) return caseView(h.slice(5));
    home();
  }
  window.addEventListener("hashchange", route);
  route();
})();
</script>
"""
