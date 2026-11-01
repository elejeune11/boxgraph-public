"""The explorer: the Synthesis as one self-contained, interactive page.

A knowledge graph (papers, models, compared data, findings, questions; edges
for ModelAtlas relations, families, comparisons, cross-paper checks, cited
values and findings) beside a dashboard of results (verdicts by purpose,
findings, relations, checks, figure readings, what to read next).

The page is one HTML file: the data is embedded as JSON, the CSS and the
script are inline, figure overlays are embedded as data URIs, and nothing is
loaded from elsewhere. Everything is sorted, so the same Synthesis gives the
same page whatever order its parts come in.
"""

from __future__ import annotations

import base64
import html
import io
import json
from pathlib import Path

PURPOSES = ("reproduction", "validation", "consistency", "approximation")
VERDICTS = ("reproduced", "close", "not reproduced", "no verdict", "error")

KINDS = {
    "not_reproduced": ("Does not follow from its inputs",
                       "A printed result that the paper's own model, run on the paper's own inputs, does not give."),
    "belongs_to_numerics": ("Belongs to the numerics",
                            "A result that moves when the numerical settings are refined: it reflects the method, not the model."),
    "depends_on_added_input": ("Depends on an added input",
                               "A verdict that changes when an input the paper does not state is given another plausible value."),
    "refuted_relation": ("Refuted stated relation",
                         "A relation between models that a paper states and the test refutes."),
    "family_conflict": ("Conflict inside a family",
                        "Two models the atlas treats as one family disagree on another paper's inputs."),
    "cited_value": ("Cited value travelled wrongly",
                    "A value one paper takes from another differs from what that paper printed."),
}

NODE_TYPES = (
    ("paper", "Papers"), ("model", "Models"), ("datum", "Data"), ("finding", "Findings"),
    ("question", "Open questions"), ("family", "Families"),
)


def _plain(syn: dict) -> dict:
    """The JSON form of a Synthesis, whether given built (with helpers) or as written."""
    keep = {k: v for k, v in syn.items() if not callable(v) and k != "builds"}
    return json.loads(json.dumps(keep, default=str))


def _dump(x) -> str:
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def _local(gid: str) -> tuple[str, str]:
    sid, _, local = gid.partition("/")
    return sid, local


def _img(path: Path, width: int = 720, out: Path | None = None, ref: str | None = None) -> str | None:
    """An overlay, reduced to `width` px and a 256-colour palette: embedded as a data URI, or, with
    `out`, written there and referenced as `ref`."""
    if not path.exists():
        return None
    raw = path.read_bytes()
    try:
        from PIL import Image

        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(buf, format="PNG", optimize=True)
        raw = buf.getvalue()
    except Exception:  # an image PIL cannot read is embedded as it is
        pass
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
        return ref
    return "data:image/png;base64," + base64.b64encode(raw).decode()


class _Graph:
    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: dict[str, dict] = {}

    def node(self, nid: str, **kw) -> str:
        if nid not in self.nodes:
            self.nodes[nid] = {"id": nid, "core": False, **kw}
        else:
            for k, v in kw.items():
                self.nodes[nid].setdefault(k, v)
        return nid

    def edge(self, eid: str, source: str, target: str, etype: str, **kw) -> None:
        base, n = eid, 2
        while eid in self.edges:
            eid, n = f"{base}#{n}", n + 1
        self.edges[eid] = {"id": eid, "source": source, "target": target, "type": etype, **kw}


def _graph(syn: dict) -> dict:
    G = _Graph()
    papers = syn["papers"]

    def paper(sid: str) -> str:
        p = papers.get(sid)
        return G.node(sid, type="paper", key=sid, paper=sid, label=sid, core=True,
                      info={"title": p.get("title"), "authors": p.get("authors"), "year": p.get("year")} if p else
                      {"title": "not in the record"})

    def model(gid: str) -> str:
        sid, local = _local(gid)
        nid = "model:" + gid
        if nid not in G.nodes:
            m = (papers.get(sid) or {}).get("models", {}).get(local)
            G.node(nid, type="model", key=gid, paper=sid, label=local, info=m or {})
            G.edge(f"in:{nid}", paper(sid), nid, "in")
        return nid

    def datum(gid: str) -> str | None:
        sid, local = _local(gid)
        nid = "datum:" + gid
        if nid not in G.nodes:
            p = papers.get(sid) or {}
            if local in p.get("data", {}):
                info = {**p["data"][local], "kind": "datum"}
            elif local in p.get("added", {}):
                info = {**p["added"][local], "kind": "added"}
            else:
                return None
            G.node(nid, type="datum", key=gid, paper=sid, label=local, info=info, verdicts=[])
        return nid

    def resolve(gid: str) -> str | None:
        sid, local = _local(gid)
        p = papers.get(sid) or {}
        if local in p.get("models", {}):
            return model(gid)
        if local in p.get("data", {}) or local in p.get("added", {}):
            return datum(gid)
        return None

    for sid in sorted(papers):
        paper(sid)
    # comparisons: paper -> printed datum, by verdict
    for sid in sorted(papers):
        for v in sorted(papers[sid].get("verdicts", []), key=lambda v: v["comparison"]):
            d = datum(f"{sid}/{v['printed']}")
            if d is None:
                continue
            verdict = v.get("verdict") or "error"
            G.nodes[d]["verdicts"].append(v)
            G.edge(f"cmp:{sid}/{v['comparison']}", sid, d, "comparison", verdict=verdict, info=v)
    # ModelAtlas relations
    rel_by_key = {}
    for r in sorted(syn.get("relations", []), key=lambda r: r["key"]):
        rel_by_key[r["key"]] = r
        a, b = model(r["a"]), model(r["b"])
        G.nodes[a]["core"] = G.nodes[b]["core"] = True
        G.edge(r["key"], a, b, "relation", status=r.get("status"), kind=r.get("kind"), info=r)
    # families
    for i, fam in enumerate(sorted(sorted(f) for f in syn.get("families", [])), start=1):
        fid = f"family:{i}"
        G.node(fid, type="family", key=fid, paper=None, label=f"family {i}", core=True, info={"members": fam})
        for m in fam:
            mid = model(m)
            G.nodes[mid]["core"] = True
            G.edge(f"fam:{i}:{m}", fid, mid, "family")
    # cross-paper checks: model -> another paper's printed datum
    for x in sorted(syn.get("cross_checks", []), key=_dump):
        if x.get("status") != "checked":
            continue
        m, d = model(x["model"]), datum(x["printed"])
        if d is None:
            continue
        G.nodes[m]["core"] = G.nodes[d]["core"] = True
        G.edge(f"cross:{x['relation']}:{x['model']}:{x['printed']}", m, d, "cross_check",
               verdict=x.get("verdict") or "error", info=x)
    # cited values: citing datum -> cited datum
    for c in sorted(syn.get("cited_values", []), key=_dump):
        if c.get("status") != "checked" or not c.get("from_datum"):
            continue
        a, b = datum(c["datum"]), datum(f"{c.get('cited_record', c['from_source'])}/{c['from_datum']}")
        if a is None or b is None:
            continue
        G.nodes[a]["core"] = G.nodes[b]["core"] = True
        G.edge(f"cited:{c['datum']}", a, b, "cited", verdict=c.get("verdict") or "error", info=c)
    # findings, attached to their subject
    for f in _findings(syn):
        fid = f["node"]
        subj = f["subject"]
        target = resolve(subj)
        if target is None and subj in rel_by_key:
            target = model(rel_by_key[subj]["a"])
        if target is None:
            target = next((t for t in map(resolve, f.get("trace", [])) if t), None)
        if target is None:
            target = paper(f["source"]) if f.get("source") in papers else None
        G.node(fid, type="finding", key=subj, paper=f.get("source"), label=KINDS.get(f["kind"], (f["kind"],))[0],
               core=True, finding=f)
        if target is not None:
            G.nodes[target]["core"] = True
            G.edge(f"about:{fid}", fid, target, "finding")
    # open questions, attached to their paper and to what they are about
    for sid in sorted(papers):
        for q in sorted(papers[sid].get("questions", []), key=lambda q: q["id"]):
            qid = G.node(f"question:{sid}/{q['id']}", type="question", key=f"{sid}/{q['id']}", paper=sid,
                         label=q["id"], info=q)
            G.edge(f"in:{qid}", sid, qid, "in")
            for about in sorted(set(q.get("about") or [])):
                t = resolve(f"{sid}/{about}")
                if t is not None:
                    G.edge(f"q:{qid}:{about}", qid, t, "question")
    for nid in sorted(G.nodes):  # a datum not compared in its paper still belongs to it
        n = G.nodes[nid]
        if n["type"] == "datum" and not n["verdicts"]:
            G.edge(f"in:{nid}", n["paper"], nid, "in")
    for n in G.nodes.values():
        if n["type"] == "datum":
            vs = [v.get("verdict") or "error" for v in n["verdicts"]]
            n["verdict"] = next((x for x in ("not reproduced", "error", "close", "no verdict", "reproduced") if x in vs), None)
    return {"nodes": [G.nodes[k] for k in sorted(G.nodes)], "edges": [G.edges[k] for k in sorted(G.edges)]}


def _findings(syn: dict) -> list[dict]:
    out, seen = [], set()
    for f in sorted(syn.get("findings", []), key=lambda f: (f["kind"], f["subject"], _dump(f))):
        nid, n = f"finding:{f['kind']}:{f['subject']}", 2
        while nid in seen:
            nid, n = f"finding:{f['kind']}:{f['subject']}#{n}", n + 1
        seen.add(nid)
        out.append({**f, "node": nid})
    return out


def _data(syn: dict, figdir: Path | None, image_dir: Path | None = None, image_prefix: str = "") -> dict:
    papers = syn["papers"]
    purposes = list(PURPOSES) + sorted({k for p in papers.values() for k in p.get("tally_by_purpose", {})} - set(PURPOSES))
    psum = []
    for sid in sorted(papers):
        p = papers[sid]
        psum.append({"id": sid, "title": p.get("title"), "authors": p.get("authors"), "year": p.get("year"),
                     "sound": p.get("sound"), "counts": p.get("counts", {}), "by_purpose": p.get("tally_by_purpose", {}),
                     "warnings": len(p.get("warnings") or []), "errors": len(p.get("errors") or []),
                     "cannot_check": len(p.get("cannot_check") or []), "reader": p.get("reader")})
    figures = []
    for sid in sorted(papers):
        for fg in sorted(papers[sid].get("figures", []), key=lambda f: f["id"]):
            rd = fg.get("readings") or []
            figures.append({
                "paper": sid, "id": fg["id"], "where": fg.get("where"), "what": fg.get("what"), "page": fg.get("page"),
                "readings": len(rd), "found": sum(1 for r in rd if r.get("found")), "errors": fg.get("errors") or [],
                "used_by": sorted(fg.get("used_by") or [], key=lambda u: u["comparison"]),
                "src": (_img(figdir / sid / f"{fg['id']}.png",
                             out=image_dir / sid / f"{fg['id']}.png" if image_dir is not None else None,
                             ref=f"{image_prefix}{sid}/{fg['id']}.png") if figdir is not None else None),
            })
    refs = sorted((r for r in syn.get("references", []) if r.get("would_settle")),
                  key=lambda r: (-len(r["would_settle"]), r.get("in_record", False), r["source"], str(r.get("label"))))
    return {
        "papers": psum,
        "purposes": purposes,
        "verdicts": list(VERDICTS),
        "kinds": {k: {"label": v[0], "about": v[1]} for k, v in KINDS.items()},
        "types": [{"id": t, "label": lbl} for t, lbl in NODE_TYPES],
        "graph": _graph(syn),
        "relations": sorted(syn.get("relations", []), key=lambda r: r["key"]),
        "families": sorted(sorted(f) for f in syn.get("families", [])),
        "findings": _findings(syn),
        "cross_checks": sorted(syn.get("cross_checks", []), key=_dump),
        "cited": sorted(syn.get("cited_values", []), key=_dump),
        "references": refs,
        "figures": figures,
    }


def render_explorer(syn: dict, title: str, figdir: Path | None = None, image_dir: Path | None = None,
                    image_prefix: str = "") -> str:
    """The Synthesis as a knowledge graph and a dashboard, in one HTML page. Figure overlays are embedded,
    or, with `image_dir`, written there and referenced as `image_prefix` + '<paper>/<figure>.png'."""
    syn = _plain(syn)
    data = _data(syn, Path(figdir) if figdir is not None else None,
                 Path(image_dir) if image_dir is not None else None, image_prefix)
    blob = _dump(data).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    t = html.escape(title)
    return (_PAGE.replace("@@TITLE@@", t).replace("@@CSS@@", _CSS).replace("@@JS@@", _JS)
            .replace("@@DATA@@", blob))


_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>@@TITLE@@</title>
<style>@@CSS@@</style>
</head>
<body>
<header class="top"><div class="wrap">
  <p class="eyebrow">BoxGraph · executable literature review</p>
  <h1>@@TITLE@@</h1>
  <p class="lede" id="lede"></p>
  <div class="stats" id="stats"></div>
</div></header>
<nav class="tabs" aria-label="Sections"><div class="wrap tabrow">
  <a href="#graph">Graph</a><a href="#verdicts">Verdicts</a><a href="#findings">Findings</a>
  <a href="#relations">Relations</a><a href="#checks">Checks</a><a href="#figures" id="nav-figures">Figures</a>
  <a href="#reading">Read next</a>
</div></nav>
<main class="wrap">
<section id="graph" class="sec">
  <div class="sechead"><h2>Knowledge graph</h2>
  <p class="note">Papers with the models that link them, the checks across papers and the findings. Open a paper to see all its models, compared data and open questions. Tap anything for its details.</p></div>
  <div class="toolbar">
    <div class="chips" id="type-chips" role="group" aria-label="Show node types"></div>
    <div class="chips" id="paper-chips" role="group" aria-label="Open a paper"></div>
  </div>
  <div class="graphgrid">
    <div class="graphbox">
      <svg id="g" role="img" aria-label="Knowledge graph of the Synthesis"></svg>
      <div class="zoom"><button type="button" id="z-in" aria-label="Zoom in">+</button><button type="button" id="z-out" aria-label="Zoom out">−</button><button type="button" id="z-fit">Fit</button></div>
    </div>
    <aside class="panel" id="panel" aria-live="polite"></aside>
  </div>
  <div class="legend" id="legend"></div>
</section>
<section id="verdicts" class="sec">
  <div class="sechead"><h2>Verdicts by paper</h2>
  <p class="note">Each comparison of a computed result with a printed one, judged at the precision the paper printed. Bars share one scale.</p></div>
  <div class="vlegend" id="vlegend"></div>
  <div class="vgrid" id="vbars"></div>
</section>
<section id="findings" class="sec">
  <div class="sechead"><h2>Findings</h2>
  <p class="note">What the Synthesis found wrong or fragile. Each traces to the page and the parts of the record behind it.</p></div>
  <div class="filters">
    <label class="search"><span class="sr">Search findings</span><input id="f-search" type="search" placeholder="Search subject or detail"></label>
    <div class="chips" id="f-kinds" role="group" aria-label="Kind"></div>
    <div class="chips" id="f-papers" role="group" aria-label="Paper"></div>
  </div>
  <div id="f-list"></div>
</section>
<section id="relations" class="sec">
  <div class="sechead"><h2>ModelAtlas relations</h2>
  <p class="note">How models in different papers relate, and whether the test bears the relation out.</p></div>
  <div id="r-list" class="rlist"></div>
</section>
<section id="checks" class="sec">
  <div class="sechead"><h2>Checks across papers</h2>
  <p class="note">One paper's model run on another's inputs, and values one paper cites from another.</p></div>
  <div id="c-list"></div>
</section>
<section id="figures" class="sec">
  <div class="sechead"><h2>Figure readings</h2>
  <p class="note">Curves read off the papers' figures, with the verdicts of the comparisons that use them.</p></div>
  <div class="strip" id="fig-strip"></div>
</section>
<section id="reading" class="sec">
  <div class="sechead"><h2>Read next</h2>
  <p class="note">Cited works that would settle open questions, most useful first.</p></div>
  <ol class="refs" id="refs"></ol>
</section>
</main>
<footer class="wrap foot"><p>Generated from the Synthesis. Every value here comes from the records; nothing is entered by hand.</p></footer>
<div class="tip" id="tip" role="tooltip" hidden></div>
<dialog id="figdlg"><form method="dialog"><button class="close" aria-label="Close">×</button></form><div id="figdlg-body"></div></dialog>
<script type="application/json" id="bg-data">@@DATA@@</script>
<script>@@JS@@</script>
</body>
</html>
"""

_CSS = r"""
/* Layout: a lab notebook. A header band, sticky section tabs, then sections on one column; the graph sits beside its detail panel on wide screens. */
:root {
  color-scheme: light;
  --bg: #f5f7f8; --surface: #ffffff; --surface-2: #eef2f4; --line: #d8dfe3; --line-2: #c3ccd2;
  --ink: #12191e; --ink-2: #44515a; --ink-3: #6e7b84;
  --accent: #155e75; --accent-2: #0e7490; --accent-ink: #ffffff;
  --ok: #0f8a0f; --close: #d99a00; --bad: #d03b3b; --none: #9aa3a9; --err: #6b5bd6;
  --ok-ink: #0b6b0b; --close-ink: #8a5f00; --bad-ink: #b02a2a; --none-ink: #59646b; --err-ink: #5345b8;
  --t-paper: #2a78d6; --t-model: #6250d6; --t-datum: #1baf7a; --t-finding: #eb6834; --t-question: #d55181; --t-family: #c98500;
  --edge: #b7c1c7; --shadow: 0 1px 2px rgba(18,25,30,.06), 0 4px 16px rgba(18,25,30,.06);
  --f-display: "Source Serif 4", "Iowan Old Style", Georgia, serif;
  --f-body: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  color-scheme: dark;
  --bg: #0f1417; --surface: #161d21; --surface-2: #1d262b; --line: #2a353b; --line-2: #3a474e;
  --ink: #e8eef1; --ink-2: #b3c0c7; --ink-3: #85939b;
  --accent: #5fb7cf; --accent-2: #7cc8dc; --accent-ink: #0b1215;
  --ok: #2bb52b; --close: #e0a40f; --bad: #e66767; --none: #6c777d; --err: #9085e9;
  --ok-ink: #57cf57; --close-ink: #f0bd45; --bad-ink: #f08a8a; --none-ink: #a3afb5; --err-ink: #aea6f0;
  --t-paper: #3987e5; --t-model: #9085e9; --t-datum: #199e70; --t-finding: #d95926; --t-question: #d55181; --t-family: #c98500;
  --edge: #43515a; --shadow: 0 1px 2px rgba(0,0,0,.3);
} }
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0f1417; --surface: #161d21; --surface-2: #1d262b; --line: #2a353b; --line-2: #3a474e;
  --ink: #e8eef1; --ink-2: #b3c0c7; --ink-3: #85939b;
  --accent: #5fb7cf; --accent-2: #7cc8dc; --accent-ink: #0b1215;
  --ok: #2bb52b; --close: #e0a40f; --bad: #e66767; --none: #6c777d; --err: #9085e9;
  --ok-ink: #57cf57; --close-ink: #f0bd45; --bad-ink: #f08a8a; --none-ink: #a3afb5; --err-ink: #aea6f0;
  --t-paper: #3987e5; --t-model: #9085e9; --t-datum: #199e70; --t-finding: #d95926; --t-question: #d55181; --t-family: #c98500;
  --edge: #43515a; --shadow: 0 1px 2px rgba(0,0,0,.3);
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.5 var(--f-body); overflow-x: hidden; }
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--surface); }
.wrap { max-width: 1240px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
code, .mono { font-family: var(--f-mono); font-size: .86em; overflow-wrap: anywhere; }
h1, h2, h3 { font-family: var(--f-display); font-weight: 600; text-wrap: balance; margin: 0; letter-spacing: -.01em; }
h1 { font-size: clamp(1.6rem, 4vw, 2.4rem); line-height: 1.15; }
h2 { font-size: 1.45rem; }
h3 { font-size: 1.08rem; }
a { color: var(--accent); }
button { font: inherit; color: inherit; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.top { background: var(--surface); border-bottom: 1px solid var(--line); }
.top .wrap { padding-block: 28px 20px; display: grid; gap: 10px; }
.eyebrow { margin: 0; font: 600 .72rem/1 var(--f-body); letter-spacing: .12em; text-transform: uppercase; color: var(--accent); }
.lede { margin: 0; color: var(--ink-2); max-width: 70ch; }
.stats { display: flex; flex-wrap: wrap; gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; margin-top: 6px; }
.stat { flex: 1 1 140px; background: var(--surface); padding: 10px 14px; display: grid; gap: 2px; }
.stat b { font: 600 1.5rem/1.1 var(--f-display); }
.stat span { font-size: .78rem; color: var(--ink-3); }
.stat i { font-style: normal; font-size: .78rem; color: var(--ink-2); }

.tabs { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: color-mix(in srgb, var(--surface) 92%, transparent); backdrop-filter: blur(6px); border-bottom: 1px solid var(--line); }
.tabrow { display: flex; gap: 4px; overflow-x: auto; scrollbar-width: none; padding-block: 6px; }
.tabrow a { flex: none; text-decoration: none; color: var(--ink-2); padding: 6px 10px; border-radius: 6px; font-size: .9rem; }
.tabrow a:hover { background: var(--surface-2); color: var(--ink); }

main { display: grid; gap: 40px; padding-block: 28px 20px; }
.sec { display: grid; gap: 14px; min-width: 0; scroll-margin-top: 56px; }
.sechead { display: grid; gap: 4px; }
.note { margin: 0; color: var(--ink-2); max-width: 72ch; font-size: .93rem; }

.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--line-2); background: var(--surface); border-radius: 999px; padding: 4px 10px; font-size: .84rem; cursor: pointer; color: var(--ink-2); min-height: 32px; }
.chip[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.chip[aria-pressed="true"] svg * { stroke: var(--bg); }
.chip .n { font-variant-numeric: tabular-nums; opacity: .75; }
.chip svg { flex: none; }
.toolbar { display: grid; gap: 8px; }

.graphgrid { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 12px; align-items: start; }
.graphbox { scroll-margin-top: 60px; position: relative; min-width: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; height: min(72vh, 640px); min-height: 380px; }
#g { width: 100%; height: 100%; display: block; touch-action: none; cursor: grab; user-select: none; -webkit-user-select: none; }
#g.dragging { cursor: grabbing; }
.zoom { position: absolute; right: 8px; bottom: 8px; display: flex; gap: 4px; }
.zoom button { min-width: 36px; height: 36px; border: 1px solid var(--line-2); background: var(--surface); border-radius: 8px; cursor: pointer; padding: 0 10px; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px; display: grid; gap: 10px; align-content: start; min-width: 0; max-height: min(72vh, 640px); overflow: auto; }
.panel .ptype { font: 600 .7rem/1 var(--f-body); letter-spacing: .1em; text-transform: uppercase; color: var(--ink-3); display: flex; align-items: center; gap: 6px; }
.panel h3 { overflow-wrap: anywhere; }
.panel dl { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 4px 10px; margin: 0; font-size: .88rem; }
.panel dt { color: var(--ink-3); }
.panel dd { margin: 0; overflow-wrap: anywhere; }
.panel .eq { font-family: var(--f-mono); font-size: .84rem; background: var(--surface-2); border-radius: 6px; padding: 8px 10px; overflow-x: auto; white-space: pre-wrap; overflow-wrap: anywhere; }
blockquote { margin: 0; padding: 6px 10px; border-left: 3px solid var(--line-2); color: var(--ink-2); font-style: italic; font-size: .9rem; }
.panel ul { margin: 0; padding-left: 18px; font-size: .88rem; display: grid; gap: 4px; }
.panel .btnrow { display: flex; flex-wrap: wrap; gap: 6px; }
.btn { text-decoration: none; display: inline-flex; align-items: center; border: 1px solid var(--accent); color: var(--accent); background: transparent; border-radius: 8px; padding: 6px 12px; cursor: pointer; font-size: .86rem; min-height: 34px; }
.btn.primary { background: var(--accent); color: var(--accent-ink); }
.linkish { background: none; border: 0; padding: 0; color: var(--accent); cursor: pointer; text-decoration: underline; text-underline-offset: 2px; font-family: var(--f-mono); font-size: .84rem; text-align: left; overflow-wrap: anywhere; }
.muted { color: var(--ink-3); }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: .8rem; color: var(--ink-2); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }

/* graph marks */
.e { fill: none; stroke: var(--edge); stroke-width: 1.2; }
.e.in { stroke-width: .8; stroke-dasharray: 2 3; }
.e.relation { stroke-width: 2.2; }
.e.cross_check { stroke-width: 2.6; stroke-dasharray: 8 4; }
.e.cited { stroke-width: 2; stroke-dasharray: 2 4; stroke-linecap: round; }
.e.family { stroke: var(--t-family); stroke-width: 1.4; stroke-dasharray: 1 3; stroke-linecap: round; }
.e.finding { stroke: var(--t-finding); stroke-width: 1.2; }
.e.question { stroke: var(--t-question); stroke-width: .9; stroke-dasharray: 3 3; }
.e.s-verified, .e.v-reproduced { stroke: var(--ok); }
.e.s-not_verified, .e.v-close { stroke: var(--close); }
.e.s-refuted, .e.v-not-reproduced { stroke: var(--bad); }
.e.s-unverifiable, .e.v-no-verdict { stroke: var(--none); }
.e.v-error { stroke: var(--err); }
.e.s-not_verified { stroke-dasharray: 6 4; }
.e.s-refuted { stroke-dasharray: 3 3; }
.e.s-unverifiable { stroke-dasharray: 1 4; stroke-linecap: round; }
.ehit { fill: none; stroke: transparent; stroke-width: 14; cursor: pointer; }
.elabel { display: none; }
.zoomed .elabel, .elabel.lit { display: inline; }
.elabel { font: 10px var(--f-body); fill: var(--ink-2); paint-order: stroke; stroke: var(--surface); stroke-width: 3px; stroke-linejoin: round; pointer-events: none; }
.n { cursor: pointer; }
.n .shape { stroke: var(--surface); stroke-width: 1.5; }
.n.paper .shape { fill: var(--t-paper); }
.n.model .shape { fill: var(--t-model); }
.n.datum .shape { fill: var(--t-datum); }
.n.finding .shape { fill: var(--t-finding); }
.n.question .shape { fill: var(--t-question); }
.n.family .shape { fill: var(--t-family); }
.n .ring { fill: none; stroke-width: 2.5; }
.n .ring.v-reproduced { stroke: var(--ok); } .n .ring.v-close { stroke: var(--close); } .n .ring.v-not-reproduced { stroke: var(--bad); }
.n .ring.v-no-verdict { stroke: var(--none); } .n .ring.v-error { stroke: var(--err); }
.n .hit { fill: transparent; }
.n text { font: 11px var(--f-body); fill: var(--ink); paint-order: stroke; stroke: var(--surface); stroke-width: 3px; stroke-linejoin: round; pointer-events: none; }
.n.paper text { font-weight: 700; font-size: 12px; fill: #fff; stroke: none; }
.n.minor text { display: none; }
.zoomed .n.minor text, .n.minor.lit text, .n.minor.sel text { display: inline; }
.n.sel .shape { stroke: var(--ink); stroke-width: 3; }
.faded { opacity: .16; }
#g .n.faded text, #g .elabel.faded { display: none; }
.n.paper.open .shape { stroke: var(--ink); stroke-width: 2; stroke-dasharray: 3 2; }

/* badges */
.badge { display: inline-flex; align-items: center; gap: 4px; border-radius: 999px; padding: 1px 8px 1px 6px; font-size: .76rem; font-weight: 600; border: 1px solid currentColor; white-space: nowrap; line-height: 1.5; }
.badge.v-reproduced, .badge.s-verified { color: var(--ok-ink); }
.badge.v-close, .badge.s-not_verified { color: var(--close-ink); }
.badge.v-not-reproduced, .badge.s-refuted { color: var(--bad-ink); }
.badge.v-no-verdict, .badge.s-unverifiable, .badge.s-other { color: var(--none-ink); }
.badge.v-error { color: var(--err-ink); }
.sw { width: 10px; height: 10px; border-radius: 2px; display: inline-block; flex: none; }
.sw.v-reproduced { background: var(--ok); } .sw.v-close { background: var(--close); } .sw.v-not-reproduced { background: var(--bad); }
.sw.v-no-verdict { background: var(--none); } .sw.v-error { background: var(--err); }

/* verdict bars */
.vlegend { display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: .84rem; color: var(--ink-2); }
.vlegend span { display: inline-flex; align-items: center; gap: 6px; }
.vgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 360px), 1fr)); gap: 12px; }
.vcard { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; display: grid; gap: 12px; align-content: start; min-width: 0; }
.vcard header { display: grid; gap: 2px; }
.vcard header .mono { color: var(--accent); }
.vcard header p { margin: 0; font-size: .86rem; color: var(--ink-2); }
.vrow { display: grid; gap: 4px; }
.vrow .lab { display: flex; justify-content: space-between; gap: 8px; font-size: .84rem; }
.vrow .lab b { font-weight: 600; text-transform: capitalize; }
.vrow .lab span { color: var(--ink-3); font-variant-numeric: tabular-nums; }
.bar { display: flex; gap: 2px; height: 14px; }
.bar .seg { height: 100%; min-width: 3px; cursor: default; }
.bar .seg:first-child { border-radius: 4px 0 0 4px; } .bar .seg:last-child { border-radius: 0 4px 4px 0; } .bar .seg:only-child { border-radius: 4px; }
.bar .seg.v-reproduced { background: var(--ok); } .bar .seg.v-close { background: var(--close); } .bar .seg.v-not-reproduced { background: var(--bad); }
.bar .seg.v-no-verdict { background: var(--none); } .bar .seg.v-error { background: var(--err); }
.bar .rest { flex: 1; }
.vrow .counts { display: flex; flex-wrap: wrap; gap: 4px 12px; font-size: .78rem; color: var(--ink-2); font-variant-numeric: tabular-nums; }
.vcard .meta { font-size: .78rem; color: var(--ink-3); border-top: 1px solid var(--line); padding-top: 8px; display: flex; flex-wrap: wrap; gap: 4px 12px; }

/* findings */
.filters { display: grid; gap: 8px; }
.search input { width: 100%; max-width: 420px; border: 1px solid var(--line-2); background: var(--surface); color: var(--ink); border-radius: 8px; padding: 8px 12px; font: inherit; }
.fgroup { display: grid; gap: 8px; margin-top: 10px; }
.fgroup > header { display: grid; gap: 2px; }
.fgroup > header p { margin: 0; font-size: .86rem; color: var(--ink-3); }
.fcard { background: var(--surface); border: 1px solid var(--line); border-left: 3px solid var(--t-finding); border-radius: 8px; padding: 10px 14px; display: grid; gap: 6px; min-width: 0; }
.fcard .row { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 10px; }
.fcard p { margin: 0; font-size: .92rem; overflow-wrap: anywhere; }
.fcard details { font-size: .86rem; color: var(--ink-2); }
.fcard details ul { margin: 4px 0 0; padding-left: 18px; }
.fcard summary { cursor: pointer; color: var(--ink-3); }
.fcard .clamp { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.fcard .more { font-family: var(--f-body); justify-self: start; }
.empty { color: var(--ink-3); font-style: italic; }

/* relations and checks */
.rlist, .clist { display: grid; gap: 8px; }
.rrow { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; display: grid; gap: 6px; min-width: 0; }
.rrow .flow { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; font-size: .92rem; }
.rrow .kind { font-style: italic; color: var(--ink-2); }
.rrow p { margin: 0; font-size: .86rem; color: var(--ink-2); overflow-wrap: anywhere; }
.rrow .meta { font-size: .78rem; color: var(--ink-3); display: flex; flex-wrap: wrap; gap: 4px 12px; }
.clist h3 { margin-top: 8px; }

/* figures */
.strip { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; scroll-snap-type: x proximity; }
.fig { flex: none; width: 250px; scroll-snap-align: start; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; display: grid; grid-template-rows: auto 1fr; cursor: pointer; text-align: left; padding: 0; }
.fig .img { background: #fff; aspect-ratio: 4 / 3; max-width: 100%; display: grid; place-items: center; border-bottom: 1px solid var(--line); }
.fig .img { position: relative; overflow: hidden; }
.fig .img img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; display: block; }
.fig .img.none { background: var(--surface-2); color: var(--ink-3); font-size: .8rem; }
.fig .body { padding: 8px 10px 10px; display: grid; gap: 4px; align-content: start; }
.fig .body b { font-size: .88rem; }
.fig .body p { margin: 0; font-size: .8rem; color: var(--ink-2); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.fig .badges { display: flex; flex-wrap: wrap; gap: 4px; }
dialog { border: 1px solid var(--line); border-radius: 12px; background: var(--surface); color: var(--ink); max-width: min(900px, calc(100vw - 32px)); width: 100%; padding: 16px; }
dialog::backdrop { background: rgba(0,0,0,.5); }
dialog img { width: 100%; background: #fff; border-radius: 6px; }
dialog .close { float: right; border: 0; background: none; font-size: 1.6rem; line-height: 1; cursor: pointer; color: var(--ink-2); }
#figdlg-body { display: grid; gap: 8px; }
#figdlg-body table { border-collapse: collapse; font-size: .82rem; font-variant-numeric: tabular-nums; }
#figdlg-body td, #figdlg-body th { padding: 2px 8px; border-bottom: 1px solid var(--line); text-align: right; }
.tablewrap { overflow-x: auto; }

/* references */
.refs { margin: 0; padding-left: 22px; display: grid; gap: 8px; }
.refs li { font-size: .9rem; overflow-wrap: anywhere; }
.refs li .meta { font-size: .78rem; color: var(--ink-3); }

.tip { position: fixed; z-index: 20; pointer-events: none; background: var(--ink); color: var(--bg); font-size: .8rem; padding: 6px 9px; border-radius: 6px; max-width: 260px; box-shadow: var(--shadow); }
.foot { padding-block: 10px 32px; color: var(--ink-3); font-size: .8rem; }

@media (max-width: 860px) {
  .graphgrid { grid-template-columns: minmax(0, 1fr); }
  .graphbox { height: 440px; min-height: 0; }
  .panel { max-height: none; }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; transition: none !important; } }
"""

_JS = r"""
(function () {
"use strict";
const D = JSON.parse(document.getElementById("bg-data").textContent);
const SVGNS = "http://www.w3.org/2000/svg";
const SYM = {"reproduced": "✓", "close": "≈", "not reproduced": "✗", "no verdict": "–", "error": "!"};
const STATUS = {"verified": "verified", "not_verified": "not verified", "refuted": "refuted", "unverifiable": "unverifiable"};
const SSYM = {"verified": "✓", "not_verified": "≈", "refuted": "✗", "unverifiable": "?"};
const TYPE = Object.fromEntries(D.types.map(t => [t.id, t.label]));
const SINGULAR = {paper: "Paper", model: "Model", datum: "Datum", finding: "Finding", question: "Open question", family: "Family"};

function h(tag, props, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) e.append(c instanceof Node ? c : String(c));
  return e;
}
function s(tag, attrs) { const e = document.createElementNS(SVGNS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; }
const vcls = v => "v-" + String(v || "error").replace(/ /g, "-");
function fmt(x) {
  if (x == null) return "–";
  if (Array.isArray(x)) return x.map(fmt).join(", ");
  if (typeof x === "number") return Math.abs(x) >= 1e5 || (x !== 0 && Math.abs(x) < 1e-3) ? x.toExponential(3) : String(+x.toPrecision(4));
  if (typeof x === "object") return JSON.stringify(x);
  return String(x);
}
function badge(v) { return h("span", {class: "badge " + vcls(v)}, (SYM[v] || "!") + " " + (v || "error")); }
function sbadge(st) { return h("span", {class: "badge s-" + (STATUS[st] ? st : "other")}, (SSYM[st] || "?") + " " + (STATUS[st] || st || "untested")); }
function idref(gid, label) { return h("button", {type: "button", class: "linkish", onclick: () => focusKey(gid)}, label || gid); }

/* ---------- header ---------- */
const nCmp = D.papers.reduce((a, p) => a + Object.values(p.by_purpose).reduce((b, t) => b + Object.values(t).reduce((c, n) => c + n, 0), 0), 0);
const nRepro = D.papers.reduce((a, p) => a + Object.values(p.by_purpose).reduce((b, t) => b + (t["reproduced"] || 0) + (t["close"] || 0), 0), 0);
const nVer = D.relations.filter(r => r.status === "verified").length;
const nCross = D.cross_checks.filter(x => x.status === "checked").length;
document.getElementById("lede").textContent =
  `${D.papers.length} papers, read into executable records. Each paper's printed results are recomputed from its own models and judged at the precision the paper printed; models are related across papers and checked on each other's inputs.`;
const stats = [
  [D.papers.length, "papers", D.papers.map(p => p.id).join(" · ")],
  [nCmp, "comparisons", `${nRepro} reproduced or close`],
  [D.findings.length, "findings", `${new Set(D.findings.map(f => f.kind)).size} kinds`],
  [D.relations.length, "model relations", `${nVer} verified`],
  [nCross, "cross-paper checks", `${D.families.length} model families`],
];
document.getElementById("stats").append(...stats.map(([n, l, sub]) => h("div", {class: "stat"}, h("b", {}, n), h("span", {}, l), h("i", {}, sub))));

/* ---------- graph ---------- */
const svg = document.getElementById("g");
const NODES = D.graph.nodes.map(n => ({...n}));
const BYID = Object.fromEntries(NODES.map(n => [n.id, n]));
const BYKEY = {};
for (const n of NODES) if (!(n.key in BYKEY) || n.type !== "finding") BYKEY[n.key] = n;
const EDGES = D.graph.edges.map(e => ({...e, s: BYID[e.source], t: BYID[e.target]}));
const state = {types: new Set(["paper", "model", "datum", "finding", "family"]), open: new Set(), sel: null};
let view = {x: 0, y: 0, k: 1}, W = 800, H = 500;
const SIZE = {paper: 22, model: 9, datum: 6, finding: 8, question: 6, family: 9};
const vroot = s("g", {}), eLayer = s("g", {}), lLayer = s("g", {}), nLayer = s("g", {});
vroot.append(eLayer, lLayer, nLayer); svg.append(vroot);

function shapeFor(type, r, label) {
  if (type === "paper") { const w = Math.max(64, 8 * (label || "").length + 20); return s("rect", {x: -w / 2, y: -15, width: w, height: 30, rx: 8, class: "shape"}); }
  if (type === "datum") return s("rect", {x: -r, y: -r, width: 2 * r, height: 2 * r, transform: "rotate(45)", class: "shape"});
  if (type === "finding") return s("path", {d: `M0 ${-r * 1.25} L${r * 1.15} ${r * .8} L${-r * 1.15} ${r * .8} Z`, class: "shape"});
  if (type === "question") { const p = []; for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i; p.push((r * 1.1 * Math.cos(a)).toFixed(2) + " " + (r * 1.1 * Math.sin(a)).toFixed(2)); } return s("path", {d: "M" + p.join(" L") + " Z", class: "shape"}); }
  if (type === "family") return s("rect", {x: -r, y: -r * .8, width: 2 * r, height: 1.6 * r, rx: 3, class: "shape"});
  return s("circle", {r, class: "shape"});
}
function iconFor(type) {
  const g = s("svg", {width: 14, height: 14, viewBox: "-8 -8 16 16", "aria-hidden": "true"});
  const sh = type === "paper" ? s("rect", {x: -7, y: -5, width: 14, height: 10, rx: 3}) : shapeFor(type, 5.5);
  sh.setAttribute("style", `fill: var(--t-${type})`); sh.removeAttribute("class"); g.append(sh); return g;
}
for (const n of NODES) {
  const r = SIZE[n.type] || 7;
  const g = s("g", {class: `n ${n.type}` + (["datum", "question", "finding"].includes(n.type) ? " minor" : ""), tabindex: "-1"});
  g.append(s("circle", {r: Math.max(r + 8, 14), class: "hit"}));
  if (n.type === "datum" && n.verdict) g.append(s("circle", {r: r + 4, class: "ring " + vcls(n.verdict)}));
  g.append(shapeFor(n.type, r, n.label));
  const t = s("text", n.type === "paper" ? {"text-anchor": "middle", dy: "0.35em"} : {"text-anchor": "middle", y: r + 14});
  t.textContent = n.label.length > 26 ? n.label.slice(0, 25) + "…" : n.label;
  g.append(t);
  const title = s("title", {}); title.textContent = `${SINGULAR[n.type]}: ${n.key}`; g.append(title);
  n.el = g; n.r = r; nLayer.append(g);
  g.addEventListener("pointerdown", ev => startNodeDrag(ev, n));
}
const pairCount = {};
for (const e of EDGES) {
  const k = [e.source, e.target].sort().join("|");
  e.par = pairCount[k] = (pairCount[k] || 0) + 1;
  const cls = ["e", e.type];
  if (e.status) cls.push("s-" + e.status);
  if (e.verdict) cls.push(vcls(e.verdict));
  e.path = s("path", {class: cls.join(" ")});
  e.hit = s("path", {class: "ehit"});
  const ttl = s("title", {}); ttl.textContent = edgeTitle(e); e.hit.append(ttl);
  eLayer.append(e.path, e.hit);
  if (e.type === "relation") { e.label = s("text", {class: "elabel", "text-anchor": "middle"}); e.label.textContent = (e.kind || "").replace(/_/g, " "); lLayer.append(e.label); }
  e.hit.addEventListener("click", ev => { ev.stopPropagation(); selectEdge(e); });
}
function edgeTitle(e) {
  if (e.type === "relation") return `${e.info.a} ${e.kind.replace(/_/g, " ")} ${e.info.b}: ${STATUS[e.status] || e.status}`;
  if (e.verdict) return `${e.type.replace("_", " ")}: ${e.verdict}`;
  return e.type;
}

function visible(n) {
  if (!state.types.has(n.type)) return false;
  if (n.type === "paper" || n.type === "family") return true;
  return n.core || state.open.has(n.paper);
}
let VN = [], VE = [];
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function hash(str) { let x = 2166136261; for (let i = 0; i < str.length; i++) { x ^= str.charCodeAt(i); x = Math.imul(x, 16777619); } return x >>> 0; }

function layout() {
  const papers = NODES.filter(n => n.type === "paper");
  const R = 150 + 40 * papers.length;
  papers.forEach((p, i) => { if (p.x == null) { const a = -Math.PI / 2 + 2 * Math.PI * i / papers.length; p.x = R * Math.cos(a); p.y = R * Math.sin(a); } });
  const deg = new Map();
  for (const e of VE) { deg.set(e.s, (deg.get(e.s) || 0) + 1); deg.set(e.t, (deg.get(e.t) || 0) + 1); }
  const fresh = VN.filter(n => n.x == null);
  fresh.forEach((n, k) => {
    const r = rng(hash(n.id)); const anchor = BYID[n.paper] || {x: 0, y: 0};
    const nb = EDGES.find(e => (e.s === n && e.t.x != null && e.t !== n) || (e.t === n && e.s.x != null && e.s !== n));
    const base = nb ? (nb.s === n ? nb.t : nb.s) : anchor;
    const rad = 40 + 10 * Math.sqrt(deg.get(base) || 1), a = 2 * Math.PI * (k / Math.max(1, fresh.length)) + r() * 0.3;
    n.x = base.x + rad * Math.cos(a); n.y = base.y + rad * Math.sin(a);
  });
  const idx = new Map(VN.map((n, i) => [n, i]));
  const links = VE.map(e => [idx.get(e.s), idx.get(e.t), e]);
  const N = VN.length, X = new Float64Array(N), Y = new Float64Array(N);
  VN.forEach((n, i) => { X[i] = n.x; Y[i] = n.y; });
  const iters = 320;
  for (let it = 0; it < iters; it++) {
    const temp = 18 * (1 - it / iters) + 0.6;
    const FX = new Float64Array(N), FY = new Float64Array(N);
    for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
      let dx = X[i] - X[j], dy = Y[i] - Y[j]; let d2 = dx * dx + dy * dy;
      if (d2 < 0.01) { dx = (i - j) * 0.1; dy = 0.1; d2 = dx * dx + dy * dy; }
      const big = (VN[i].type === "paper" ? 3 : 1) * (VN[j].type === "paper" ? 3 : 1);
      const f = 1800 * big / d2; const d = Math.sqrt(d2);
      FX[i] += f * dx / d; FY[i] += f * dy / d; FX[j] -= f * dx / d; FY[j] -= f * dy / d;
    }
    for (const [a, b, e] of links) {
      const hub = e.s.type === "paper" ? e.s : e.t.type === "paper" ? e.t : null;
      const want = hub ? 36 + 9 * Math.sqrt(deg.get(hub) || 1) : e.type === "relation" ? 110 : e.type === "finding" ? 34 : 70;
      const dx = X[b] - X[a], dy = Y[b] - Y[a]; const d = Math.sqrt(dx * dx + dy * dy) || 0.01;
      const f = 0.06 * (d - want);
      FX[a] += f * dx / d; FY[a] += f * dy / d; FX[b] -= f * dx / d; FY[b] -= f * dy / d;
    }
    for (let i = 0; i < N; i++) {
      FX[i] -= X[i] * 0.012; FY[i] -= Y[i] * 0.012;
      if (VN[i].pinned) continue;
      const m = Math.sqrt(FX[i] * FX[i] + FY[i] * FY[i]) || 1; const step = Math.min(temp, m);
      X[i] += FX[i] / m * step; Y[i] += FY[i] / m * step;
    }
  }
  VN.forEach((n, i) => { n.x = X[i]; n.y = Y[i]; });
}
function edgePath(e) {
  const a = e.s, b = e.t; const dx = b.x - a.x, dy = b.y - a.y; const d = Math.sqrt(dx * dx + dy * dy) || 1;
  const bend = e.par > 1 ? (e.par % 2 ? -1 : 1) * Math.ceil((e.par - 1) / 2) * 22 : 0;
  const mx = (a.x + b.x) / 2 - dy / d * bend, my = (a.y + b.y) / 2 + dx / d * bend;
  e.mx = (a.x + b.x) / 2 - dy / d * bend / 2; e.my = (a.y + b.y) / 2 + dx / d * bend / 2;
  return `M${a.x.toFixed(1)} ${a.y.toFixed(1)} Q${mx.toFixed(1)} ${my.toFixed(1)} ${b.x.toFixed(1)} ${b.y.toFixed(1)}`;
}
function draw() {
  for (const n of VN) n.el.setAttribute("transform", `translate(${n.x.toFixed(1)} ${n.y.toFixed(1)})`);
  for (const e of VE) {
    const d = edgePath(e); e.path.setAttribute("d", d); e.hit.setAttribute("d", d);
    if (e.label) { e.label.setAttribute("x", e.mx.toFixed(1)); e.label.setAttribute("y", (e.my - 4).toFixed(1)); }
  }
  vroot.setAttribute("transform", `translate(${view.x.toFixed(2)} ${view.y.toFixed(2)}) scale(${view.k.toFixed(4)})`);
  svg.classList.toggle("zoomed", view.k > 1.35);
}
function refresh(relayout) {
  VN = NODES.filter(visible);
  const vis = new Set(VN);
  VE = EDGES.filter(e => vis.has(e.s) && vis.has(e.t));
  const ve = new Set(VE);
  for (const n of NODES) n.el.style.display = vis.has(n) ? "" : "none";
  for (const e of EDGES) { const on = ve.has(e); e.path.style.display = e.hit.style.display = on ? "" : "none"; if (e.label) e.label.style.display = on ? "" : "none"; }
  for (const n of NODES) if (n.type === "paper") n.el.classList.toggle("open", state.open.has(n.id));
  if (relayout) layout();
  draw(); highlight();
}
function measure() { const r = svg.getBoundingClientRect(); W = r.width || 800; H = r.height || 500; }
function fit() {
  measure(); if (!VN.length) return;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const n of VN) { x0 = Math.min(x0, n.x - 40); x1 = Math.max(x1, n.x + 40); y0 = Math.min(y0, n.y - 24); y1 = Math.max(y1, n.y + 28); }
  const k = Math.min(W / (x1 - x0), H / (y1 - y0), 2.2) * 0.94;
  view = {k, x: W / 2 - k * (x0 + x1) / 2, y: H / 2 - k * (y0 + y1) / 2}; draw();
}
function zoomAt(f, cx, cy) {
  const k = Math.max(0.2, Math.min(5, view.k * f)); const r = k / view.k;
  view.x = cx - (cx - view.x) * r; view.y = cy - (cy - view.y) * r; view.k = k; draw();
}
document.getElementById("z-in").onclick = () => { measure(); zoomAt(1.3, W / 2, H / 2); };
document.getElementById("z-out").onclick = () => { measure(); zoomAt(1 / 1.3, W / 2, H / 2); };
document.getElementById("z-fit").onclick = fit;
svg.addEventListener("wheel", ev => { ev.preventDefault(); const r = svg.getBoundingClientRect(); zoomAt(Math.exp(-ev.deltaY * 0.0015), ev.clientX - r.left, ev.clientY - r.top); }, {passive: false});
const pointers = new Map(); let pan = null, pinch = null, drag = null;
svg.addEventListener("pointerdown", ev => {
  pointers.set(ev.pointerId, {x: ev.clientX, y: ev.clientY});
  if (pointers.size === 2) { drag = null; const [p, q] = [...pointers.values()]; pinch = {d: Math.hypot(p.x - q.x, p.y - q.y), k: view.k}; pan = null; return; }
  if (!drag) { pan = {x: ev.clientX, y: ev.clientY, vx: view.x, vy: view.y, moved: false}; }
  svg.setPointerCapture(ev.pointerId);
});
svg.addEventListener("pointermove", ev => {
  if (!pointers.has(ev.pointerId)) return;
  pointers.set(ev.pointerId, {x: ev.clientX, y: ev.clientY});
  if (pinch && pointers.size === 2) {
    const [p, q] = [...pointers.values()]; const r = svg.getBoundingClientRect();
    zoomAt(pinch.k * Math.hypot(p.x - q.x, p.y - q.y) / pinch.d / view.k, (p.x + q.x) / 2 - r.left, (p.y + q.y) / 2 - r.top); return;
  }
  if (drag) {
    const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
    if (drag.moved) { drag.n.x = drag.nx + dx / view.k; drag.n.y = drag.ny + dy / view.k; drag.n.pinned = true; draw(); }
    return;
  }
  if (pan) {
    const dx = ev.clientX - pan.x, dy = ev.clientY - pan.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) { pan.moved = true; svg.classList.add("dragging"); }
    view.x = pan.vx + dx; view.y = pan.vy + dy; draw();
  }
});
function endPointer(ev) {
  pointers.delete(ev.pointerId);
  if (pointers.size < 2) pinch = null;
  if (drag) { if (!drag.moved) selectNode(drag.n, true); drag = null; }
  else if (pan && !pan.moved && ev.type === "pointerup" && ev.target === svg) clearSel();
  pan = null; svg.classList.remove("dragging");
}
svg.addEventListener("pointerup", endPointer); svg.addEventListener("pointercancel", endPointer);
function startNodeDrag(ev, n) { if (pointers.size > 0) return; drag = {n, x: ev.clientX, y: ev.clientY, nx: n.x, ny: n.y, moved: false}; }

/* selection and the detail panel */
const panel = document.getElementById("panel");
function highlight() {
  const sel = state.sel; const lit = new Set();
  if (sel && sel.node) { lit.add(sel.node); for (const e of VE) if (e.s === sel.node || e.t === sel.node) { lit.add(e.s); lit.add(e.t); lit.add(e); } }
  if (sel && sel.edge) { lit.add(sel.edge); lit.add(sel.edge.s); lit.add(sel.edge.t); }
  const few = lit.size <= 30;
  for (const n of VN) { n.el.classList.toggle("faded", !!sel && !lit.has(n)); n.el.classList.toggle("lit", few && lit.has(n)); n.el.classList.toggle("sel", !!sel && sel.node === n); }
  for (const e of VE) { const f = !!sel && !lit.has(e); e.path.classList.toggle("faded", f); if (e.label) { e.label.classList.toggle("faded", f); e.label.classList.toggle("lit", !!sel && lit.has(e)); } }
}
function selectNode(n, fromGraph) { state.sel = {node: n}; highlight(); showNode(n); if (!fromGraph) center(n); if (window.matchMedia("(max-width: 860px)").matches && fromGraph) panel.scrollIntoView({block: "nearest", behavior: "smooth"}); }
function selectEdge(e) { state.sel = {edge: e}; highlight(); showEdge(e); }
function clearSel() { state.sel = null; highlight(); showIntro(); }
function center(n) { measure(); view.x = W / 2 - n.x * view.k; view.y = H / 2 - n.y * view.k; draw(); }
function focusKey(key) {
  const n = BYKEY[key] || BYID[key]; if (!n) return;
  focusNode(n);
}
function focusNode(n) {
  let changed = false;
  if (!state.types.has(n.type)) { state.types.add(n.type); changed = true; syncTypeChips(); }
  if (!visible(n) && n.paper) { state.open.add(n.paper); changed = true; syncPaperChips(); }
  if (changed) refresh(true);
  if (view.k < 1.1) { measure(); view.k = 1.4; }
  selectNode(n, false);
  document.querySelector(".graphbox").scrollIntoView({behavior: "smooth", block: "start"});
}
function dl(pairs) {
  const d = h("dl");
  for (const [k, v] of pairs) if (v != null && v !== "" && !(Array.isArray(v) && !v.length)) d.append(h("dt", {}, k), h("dd", {}, v instanceof Node ? v : fmt(v)));
  return d;
}
function head(type, key, title) {
  return [h("div", {class: "ptype"}, iconFor(type), SINGULAR[type] || type), h("h3", {}, title || key), title && title !== key ? h("div", {class: "mono muted"}, key) : null];
}
function quote(q, page) { return q ? h("blockquote", {}, `“${q}”` + (page != null ? ` (p. ${page})` : "")) : null; }
function showIntro() {
  panel.replaceChildren(
    h("div", {class: "ptype"}, "Details"),
    h("h3", {}, "Tap a paper, model, datum or finding"),
    h("p", {class: "note"}, "Lines between models are ModelAtlas relations, coloured by whether the test verified them. Lines to data are comparisons, coloured by verdict. Open a paper to see everything it holds."),
    h("div", {class: "btnrow"}, ...NODES.filter(n => n.type === "paper").map(p => h("button", {type: "button", class: "btn", onclick: () => togglePaper(p.id, true)}, `Open ${p.id}`))));
}
function edgesOf(n) { return EDGES.filter(e => e.s === n || e.t === n); }
function showNode(n) {
  const i = n.info || {}; const out = n.type === "finding" ? [] : [...head(n.type, n.key, n.type === "paper" ? i.title : n.type === "model" ? i.name : null)];
  if (n.type === "paper") {
    const p = D.papers.find(p => p.id === n.id) || {};
    out.push(dl([["authors", (p.authors || []).join(", ")], ["year", p.year], ["record", p.sound ? "sound" : "not sound"],
      ["holds", p.counts ? `${p.counts.models} models, ${p.counts.data} data, ${p.counts.comparisons} comparisons, ${p.counts.questions} open questions` : null],
      ["can't check", p.cannot_check], ["read by", p.reader ? `${p.reader.name || ""} ${p.reader.model ? "(" + p.reader.model + ")" : ""}` : null]]));
    for (const pu of D.purposes) if (p.by_purpose && p.by_purpose[pu]) out.push(barRow(p, pu, null));
    const open = state.open.has(n.id);
    out.push(h("div", {class: "btnrow"}, h("button", {type: "button", class: "btn primary", onclick: () => togglePaper(n.id, !open)}, open ? "Close paper" : "Open paper in graph"),
      h("a", {class: "btn", href: "#verdicts"}, "Verdicts")));
  } else if (n.type === "model") {
    if (i.equation) out.push(h("div", {class: "eq"}, i.equation));
    out.push(dl([["paper", n.paper], ["page", i.page], ["role", i.role], ["runnable", i.runnable == null ? null : i.runnable ? "yes" : "no"]]));
    const rel = edgesOf(n).filter(e => ["relation", "cross_check", "family"].includes(e.type));
    if (rel.length) out.push(h("h3", {}, "Links"), h("ul", {}, ...rel.map(e => h("li", {}, linkLine(e, n)))));
  } else if (n.type === "datum") {
    out.push(dl([["printed", i.printed], ["unit", i.unit], ["quantity", i.quantity], ["origin", i.kind === "added" ? "added (not stated in the paper)" : i.origin], ["page", i.page], ["from", i.from_source]]));
    if (i.basis) out.push(h("p", {class: "note"}, i.basis));
    out.push(quote(i.quote));
    for (const v of n.verdicts || []) out.push(verdictBlock(v));
    const xs = edgesOf(n).filter(e => e.type === "cross_check" || e.type === "cited");
    if (xs.length) out.push(h("h3", {}, "Checked from other papers"), h("ul", {}, ...xs.map(e => h("li", {}, linkLine(e, n)))));
  } else if (n.type === "finding") {
    const f = n.finding; out.push(findingBody(f, false));
  } else if (n.type === "question") {
    out.push(dl([["kind", i.kind], ["paper", n.paper], ["about", (i.about || []).join(", ")]]), h("p", {}, i.text || ""));
    if (i.citation) out.push(quote(i.citation.quote, i.citation.page));
  } else if (n.type === "family") {
    out.push(h("p", {class: "note"}, "Models joined by verified relations: what holds for one holds for all."), h("ul", {}, ...(i.members || []).map(m => h("li", {}, idref(m)))));
  }
  panel.replaceChildren(...out.filter(Boolean));
}
function linkLine(e, from) {
  const other = e.s === from ? e.t : e.s;
  if (e.type === "relation") return h("span", {}, sbadge(e.status), " ", h("i", {}, e.kind.replace(/_/g, " ")), " ", idref(other.key), " ", h("button", {type: "button", class: "linkish", onclick: () => selectEdge(e)}, "details"));
  if (e.verdict) return h("span", {}, badge(e.verdict), " ", e.type === "cited" ? "cited " : "run on ", idref(other.key));
  return h("span", {}, idref(other.key));
}
function verdictBlock(v) {
  return h("div", {class: "rrow"}, h("div", {class: "flow"}, badge(v.verdict || "error"), h("span", {class: "mono"}, v.comparison), h("span", {class: "muted"}, v.purpose)),
    dl([["printed", v.printed_text], ["computed", v.computed_value], ["per value", v.per_value && v.per_value.length > 1 ? v.per_value.map(x => SYM[x] || "!").join(" ") : null], ["error", v.error]]));
}
function showEdge(e) {
  const i = e.info || {}; const out = [];
  if (e.type === "relation") {
    out.push(h("div", {class: "ptype"}, "ModelAtlas relation"), h("h3", {}, i.kind.replace(/_/g, " ")), h("div", {class: "flow"}, idref(i.a), " → ", idref(i.b)), sbadge(i.status),
      dl([["provenance", i.provenance], ["method", i.method], ["samples", i.samples || null], ["entered in", i.source], ["key", i.key]]), h("p", {}, i.detail || ""));
    if (i.holds_instead) out.push(h("p", {class: "note"}, "Holds instead: " + i.holds_instead));
  } else if (e.type === "comparison") {
    out.push(h("div", {class: "ptype"}, "Comparison"), h("h3", {}, i.comparison), verdictBlock(i), quote(i.quote, i.page));
  } else if (e.type === "cross_check") {
    out.push(h("div", {class: "ptype"}, "Cross-paper check"), h("h3", {}, `${i.model} on the inputs of ${i.on_inputs_of}`), badge(i.verdict),
      dl([["printed", i.printed_text], ["computed", i.computed_value], ["paper's own verdict", i.own_verdict], ["relation", i.relation], ["run", i.run]]));
    if ((i.correspondences || []).length) out.push(h("h3", {}, "Rests on"), h("ul", {}, ...i.correspondences.map(c => h("li", {class: "mono"}, c)), ...(i.added || []).map(c => h("li", {}, c))));
  } else if (e.type === "cited") {
    out.push(h("div", {class: "ptype"}, "Cited value"), h("h3", {}, i.datum), badge(i.verdict),
      dl([["printed", i.printed], ["source prints", i.cited_printed], ["from", `${i.cited_record || i.from_source}/${i.from_datum}`], ["page", i.page], ["matched by", i.correspondence]]));
  } else {
    out.push(h("div", {class: "ptype"}, e.type), h("p", {}, `${e.s.key} → ${e.t.key}`));
  }
  panel.replaceChildren(...out.filter(Boolean));
}

/* chips */
const typeChips = document.getElementById("type-chips");
const counts = {}; for (const n of NODES) counts[n.type] = (counts[n.type] || 0) + 1;
function syncTypeChips() { for (const b of typeChips.children) b.setAttribute("aria-pressed", state.types.has(b.dataset.t)); }
for (const t of D.types) if (counts[t.id]) {
  typeChips.append(h("button", {type: "button", class: "chip", "data-t": t.id, "aria-pressed": state.types.has(t.id), onclick: () => {
    if (t.id === "paper") return;
    state.types.has(t.id) ? state.types.delete(t.id) : state.types.add(t.id); syncTypeChips(); refresh(true); fit();
  }}, iconFor(t.id), t.label, h("span", {class: "n"}, counts[t.id])));
}
const paperChips = document.getElementById("paper-chips");
function syncPaperChips() { for (const b of paperChips.children) b.setAttribute("aria-pressed", state.open.has(b.dataset.p)); }
paperChips.append(h("span", {class: "muted", style: "font-size:.84rem; align-self:center"}, "Open:"));
for (const p of D.papers) paperChips.append(h("button", {type: "button", class: "chip", "data-p": p.id, "aria-pressed": "false", onclick: () => togglePaper(p.id, !state.open.has(p.id))}, p.id));
function togglePaper(id, on) {
  on ? state.open.add(id) : state.open.delete(id);
  if (on) state.types.add("question");
  syncPaperChips(); syncTypeChips(); refresh(true); fit();
  if (BYID[id]) { state.sel = {node: BYID[id]}; highlight(); showNode(BYID[id]); }
}
/* legend */
const leg = document.getElementById("legend");
function lineSample(cls) { const g = s("svg", {width: 30, height: 10, "aria-hidden": "true"}); g.append(s("path", {d: "M2 5 L28 5", class: "e " + cls})); return g; }
leg.append(
  h("span", {}, lineSample("relation s-verified"), "relation verified"), h("span", {}, lineSample("relation s-not_verified"), "not verified"),
  h("span", {}, lineSample("relation s-refuted"), "refuted"), h("span", {}, lineSample("relation s-unverifiable"), "unverifiable"),
  h("span", {}, lineSample("comparison v-reproduced"), "comparison: reproduced"), h("span", {}, lineSample("comparison v-close"), "close"),
  h("span", {}, lineSample("comparison v-not-reproduced"), "not reproduced"), h("span", {}, lineSample("comparison v-no-verdict"), "no verdict"),
  h("span", {}, lineSample("cross_check v-reproduced"), "cross-paper check"), h("span", {}, lineSample("cited v-reproduced"), "cited value"),
  h("span", {}, lineSample("family"), "family"));

/* ---------- verdict bars ---------- */
const tip = document.getElementById("tip");
function showTip(ev, text) { tip.textContent = text; tip.hidden = false; const x = Math.min(ev.clientX + 12, window.innerWidth - 270); tip.style.left = Math.max(8, x) + "px"; tip.style.top = (ev.clientY + 14) + "px"; }
function hideTip() { tip.hidden = true; }
let maxTotal = 1;
for (const p of D.papers) for (const t of Object.values(p.by_purpose)) maxTotal = Math.max(maxTotal, Object.values(t).reduce((a, b) => a + b, 0));
function barRow(p, pu) {
  const t = p.by_purpose[pu]; const total = Object.values(t).reduce((a, b) => a + b, 0);
  const bar = h("div", {class: "bar", role: "img", "aria-label": `${p.id} ${pu}: ` + D.verdicts.filter(v => t[v]).map(v => `${t[v]} ${v}`).join(", ")});
  for (const v of D.verdicts) if (t[v]) {
    const seg = h("div", {class: "seg " + vcls(v), style: `flex: 0 0 calc(${(100 * t[v] / maxTotal).toFixed(3)}% - 2px)`});
    const text = `${p.id} · ${pu}: ${t[v]} of ${total} ${v}`;
    seg.addEventListener("pointermove", ev => showTip(ev, text)); seg.addEventListener("pointerleave", hideTip);
    bar.append(seg);
  }
  bar.append(h("div", {class: "rest"}));
  return h("div", {class: "vrow"}, h("div", {class: "lab"}, h("b", {}, pu), h("span", {}, `${total} ${total === 1 ? "comparison" : "comparisons"}`)), bar,
    h("div", {class: "counts"}, ...D.verdicts.filter(v => t[v]).map(v => h("span", {}, `${SYM[v]} ${t[v]} ${v}`))));
}
document.getElementById("vlegend").append(...D.verdicts.map(v => h("span", {}, h("i", {class: "sw " + vcls(v)}), `${SYM[v]} ${v}`)));
const vbars = document.getElementById("vbars");
for (const p of D.papers) {
  const rows = D.purposes.filter(pu => p.by_purpose[pu]).map(pu => barRow(p, pu));
  vbars.append(h("article", {class: "vcard"},
    h("header", {}, h("button", {type: "button", class: "linkish", onclick: () => focusKey(p.id)}, p.id), h("h3", {}, p.title || p.id),
      h("p", {}, [(p.authors || []).join(", "), p.year].filter(Boolean).join(" · "))),
    ...(rows.length ? rows : [h("p", {class: "empty"}, "No comparisons.")]),
    h("div", {class: "meta"}, h("span", {}, `${p.counts.models ?? 0} models`), h("span", {}, `${p.counts.data ?? 0} data`),
      h("span", {}, `${p.cannot_check} cannot be checked`), h("span", {}, `${p.counts.questions ?? 0} open questions`), p.sound ? null : h("span", {}, "record not sound"))));
}

/* ---------- findings ---------- */
const fstate = {kind: null, paper: null, q: ""};
const kindsPresent = [...new Set(D.findings.map(f => f.kind))];
const fk = document.getElementById("f-kinds"), fp = document.getElementById("f-papers");
function chip(label, n, pressed, on) { return h("button", {type: "button", class: "chip", "aria-pressed": pressed, onclick: on}, label, n != null ? h("span", {class: "n"}, n) : null); }
function renderFChips() {
  fk.replaceChildren(chip("All kinds", D.findings.length, fstate.kind === null, () => { fstate.kind = null; renderFindings(); }),
    ...kindsPresent.map(k => chip((D.kinds[k] || {label: k}).label, D.findings.filter(f => f.kind === k).length, fstate.kind === k, () => { fstate.kind = fstate.kind === k ? null : k; renderFindings(); })));
  const ps = [...new Set(D.findings.map(f => f.source))].sort();
  fp.replaceChildren(chip("All papers", null, fstate.paper === null, () => { fstate.paper = null; renderFindings(); }),
    ...ps.map(p => chip(p, D.findings.filter(f => f.source === p).length, fstate.paper === p, () => { fstate.paper = fstate.paper === p ? null : p; renderFindings(); })));
}
function findingBody(f, card) {
  const kids = [];
  if (card) kids.push(h("div", {class: "row"}, h("span", {class: "mono"}, f.subject), f.page != null ? h("span", {class: "muted"}, `p. ${f.page}`) : null,
    h("button", {type: "button", class: "linkish", onclick: () => focusNode(BYID[f.node])}, "show in graph")));
  else kids.push(h("div", {class: "ptype"}, iconFor("finding"), (D.kinds[f.kind] || {label: f.kind}).label), h("h3", {}, f.subject), dl([["paper", f.source], ["page", f.page]]));
  const det = f.detail || "";
  if (card && det.length > 260) {
    const p = h("p", {class: "clamp"}, det);
    kids.push(p, h("button", {type: "button", class: "linkish more", onclick: ev => { const c = p.classList.toggle("clamp"); ev.target.textContent = c ? "show all" : "show less"; }}, "show all"));
  } else kids.push(h("p", {}, det));
  if (f.quote) kids.push(quote(f.quote, f.page));
  if ((f.evidence || []).length > 1) kids.push(h("details", {}, h("summary", {}, `${f.evidence.length} lines of evidence`), h("ul", {}, ...f.evidence.map(x => h("li", {}, x)))));
  if ((f.trace || []).length) kids.push(h("details", {open: !card}, h("summary", {}, "Traces to"), h("ul", {}, ...f.trace.map(x => h("li", {}, BYKEY[x] ? idref(x) : h("span", {class: "mono"}, x))))));
  if ((f.implicates || []).length) kids.push(h("details", {}, h("summary", {}, `Puts ${f.implicates.length} more ${f.implicates.length === 1 ? "result" : "results"} in doubt`), h("ul", {}, ...f.implicates.map(x => h("li", {}, BYKEY[x] ? idref(x) : h("span", {class: "mono"}, x))))));
  return card ? h("article", {class: "fcard"}, ...kids) : h("div", {style: "display:grid; gap:8px"}, ...kids);
}
function renderFindings() {
  renderFChips();
  const q = fstate.q.toLowerCase();
  const sel = D.findings.filter(f => (!fstate.kind || f.kind === fstate.kind) && (!fstate.paper || f.source === fstate.paper) &&
    (!q || (f.subject + " " + f.detail + " " + (f.evidence || []).join(" ")).toLowerCase().includes(q)));
  const list = document.getElementById("f-list"); list.replaceChildren();
  if (!sel.length) { list.append(h("p", {class: "empty"}, D.findings.length ? "No finding matches these filters." : "The Synthesis has no findings.")); return; }
  for (const k of kindsPresent) {
    const fs = sel.filter(f => f.kind === k); if (!fs.length) continue;
    list.append(h("div", {class: "fgroup"}, h("header", {}, h("h3", {}, `${(D.kinds[k] || {label: k}).label} (${fs.length})`), h("p", {}, (D.kinds[k] || {about: ""}).about)),
      ...fs.map(f => findingBody(f, true))));
  }
}
document.getElementById("f-search").addEventListener("input", ev => { fstate.q = ev.target.value; renderFindings(); });
renderFindings();

/* ---------- relations ---------- */
const rl = document.getElementById("r-list");
if (!D.relations.length) rl.append(h("p", {class: "empty"}, "No relations between models yet."));
for (const r of D.relations) {
  const e = EDGES.find(e => e.id === r.key);
  rl.append(h("article", {class: "rrow"},
    h("div", {class: "flow"}, sbadge(r.status), idref(r.a), h("span", {class: "kind"}, (r.kind || "").replace(/_/g, " ")), idref(r.b)),
    h("p", {}, r.detail || ""), r.holds_instead ? h("p", {}, "Holds instead: " + r.holds_instead) : null,
    h("div", {class: "meta"}, h("span", {}, r.provenance === "stated" ? "stated by the paper" : "proposed"), r.method ? h("span", {}, "tested " + r.method) : null,
      h("span", {}, "entered in " + r.source), e ? h("button", {type: "button", class: "linkish", onclick: () => { focusNode(e.s); selectEdge(e); }}, "show in graph") : null)));
}
if (D.families.length) rl.append(h("p", {class: "note"}, `Families: ${D.families.map(f => f.join(" = ")).join("; ")}.`));

/* ---------- checks ---------- */
const cl = h("div", {class: "clist"}); document.getElementById("c-list").append(cl);
cl.append(h("h3", {}, "Models run on another paper's inputs"));
const checked = D.cross_checks.filter(x => x.status === "checked");
if (!checked.length) cl.append(h("p", {class: "empty"}, "No relation lets one paper's model run on another's inputs yet."));
for (const x of checked) cl.append(h("article", {class: "rrow"},
  h("div", {class: "flow"}, badge(x.verdict), idref(x.model), h("span", {class: "kind"}, "on the inputs of"), idref(x.run)),
  h("p", {}, `computes ${fmt(x.computed_value)}; the paper printed ${fmt(x.printed_text)} (${x.printed}). The paper's own model: ${x.own_verdict || "–"}.`),
  h("div", {class: "meta"}, h("span", {}, "via " + x.relation), ...(x.added || []).map(a => h("span", {}, a)))));
const other = D.cross_checks.filter(x => x.status !== "checked");
if (other.length) cl.append(h("details", {}, h("summary", {}, `${other.length} more links could not be run`), h("ul", {}, ...other.map(x => h("li", {}, `${x.model || x.relation}: ${x.status}`)))));
cl.append(h("h3", {}, "Cited values"));
const cchk = D.cited.filter(c => c.status === "checked"), cout = D.cited.filter(c => c.status !== "checked");
if (!cchk.length) cl.append(h("p", {class: "empty"}, "No cited value points to a paper in the record."));
for (const c of cchk) cl.append(h("article", {class: "rrow"},
  h("div", {class: "flow"}, badge(c.verdict), idref(c.datum), h("span", {class: "kind"}, "cites"), idref(`${c.cited_record || c.from_source}/${c.from_datum}`)),
  h("p", {}, `printed ${c.printed}; the cited paper prints ${c.cited_printed}.`)));
if (cout.length) cl.append(h("details", {}, h("summary", {}, `${cout.length} cited values come from works not in the record`),
  h("ul", {}, ...cout.map(c => h("li", {}, h("span", {class: "mono"}, c.datum), ` = ${c.printed}, from ${c.from_source}` + (c.page != null ? ` (p. ${c.page})` : ""))))));

/* ---------- figures ---------- */
const strip = document.getElementById("fig-strip");
if (!D.figures.length) { document.getElementById("figures").hidden = true; document.getElementById("nav-figures").hidden = true; }
const dlg = document.getElementById("figdlg"), dlgBody = document.getElementById("figdlg-body");
for (const f of D.figures) {
  const tally = {}; for (const u of f.used_by) { const v = u.verdict || "error"; tally[v] = (tally[v] || 0) + 1; }
  const badges = D.verdicts.filter(v => tally[v]).map(v => h("span", {class: "badge " + vcls(v)}, `${SYM[v]} ${tally[v] > 1 ? tally[v] + " " : ""}${v}`));
  strip.append(h("button", {type: "button", class: "fig", onclick: () => openFig(f), "aria-label": `${f.paper} ${f.where}`},
    f.src ? h("div", {class: "img"}, h("img", {src: f.src, alt: `${f.where} of ${f.paper}, with the reading drawn on it`})) : h("div", {class: "img none"}, "no image"),
    h("div", {class: "body"}, h("b", {}, `${f.paper} · ${f.where}`), h("p", {}, f.what || ""),
      h("span", {class: "muted", style: "font-size:.76rem"}, `${f.found} of ${f.readings} points read` + (f.errors.length ? ` · ${f.errors.length} errors` : "")),
      h("div", {class: "badges"}, ...(badges.length ? badges : [h("span", {class: "muted", style: "font-size:.76rem"}, "not used by a comparison")])))));
}
function openFig(f) {
  dlgBody.replaceChildren(h("h3", {}, `${f.paper} · ${f.where}`), h("p", {class: "note"}, (f.what || "") + (f.page != null ? ` (p. ${f.page})` : "")),
    f.src ? h("img", {src: f.src, alt: `${f.where} with the reading drawn on it`}) : null,
    ...f.used_by.map(u => h("div", {class: "flow", style: "display:flex; gap:8px; flex-wrap:wrap; align-items:center"}, badge(u.verdict || "error"), h("span", {class: "mono"}, u.comparison), h("span", {class: "muted"}, u.purpose),
      u.per_value && u.per_value.length > 1 ? h("span", {}, u.per_value.map(x => SYM[x] || "!").join(" ")) : null)),
    ...f.errors.map(x => h("p", {class: "note"}, "Error: " + x)));
  if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
}
dlg.addEventListener("click", ev => { if (ev.target === dlg) dlg.close(); });

/* ---------- references ---------- */
const refs = document.getElementById("refs");
if (!D.references.length) refs.replaceWith(h("p", {class: "empty"}, "No cited work is tied to an open question."));
for (const r of D.references.slice(0, 15)) refs.append(h("li", {}, r.text || r.label, h("div", {class: "meta"},
  `cited by ${r.source} [${r.label}] · would settle ${r.would_settle.length} open ${r.would_settle.length === 1 ? "question" : "questions"} · ` + (r.in_record ? "in the record" : "not in the record yet"))));
if (D.references.length > 15) refs.after(h("p", {class: "note"}, `${D.references.length - 15} more cited works would settle open questions.`));

/* ---------- start ---------- */
showIntro();
refresh(true);
requestAnimationFrame(fit);
let rz; window.addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(fit, 150); });
})();
"""
