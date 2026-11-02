"""The written review and the HTML/Markdown report.

The review is generated from the Synthesis, sentence by sentence. Each
sentence carries the ids it rests on. The tracer refuses a sentence with no
trace, a trace to an unknown id, or a number that does not appear in what it
traces to (04-synthesis.md: every sentence traces back to the records).
"""

from __future__ import annotations

import base64
import html as H
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .synthesis import cross_id

KIND_ORDER = ["not_reproduced", "refuted_relation", "family_conflict", "cited_value", "belongs_to_numerics",
              "depends_on_added_input"]

KIND_TEXT = {
    "not_reproduced": "A printed result does not follow from the paper's own model and inputs",
    "belongs_to_numerics": "A result belongs to the numerics, not the model",
    "depends_on_added_input": "A verdict depends on an input the paper does not state",
    "refuted_relation": "A relation a paper states is refuted",
    "family_conflict": "A conflict inside a family",
    "cited_value": "A cited value does not match its source",
}


@dataclass
class Sentence:
    text: str
    trace: list[str] = field(default_factory=list)
    section: str = "review"


# --------------------------------------------------------------------------
# Index: id -> what it says, for the tracer
# --------------------------------------------------------------------------


def _floats(o, out: set):
    if isinstance(o, dict):
        for v in o.values():
            _floats(v, out)
    elif isinstance(o, list):
        for v in o:
            _floats(v, out)
    elif isinstance(o, float):
        for fmt in ("{:.4g}", "{:.3g}", "{:.2g}", "{:.1e}", "{:.2e}"):
            out.add(fmt.format(o))


def _material(*objs) -> str:
    extra: set = set()
    for o in objs:
        _floats(o, extra)
    return json.dumps(objs, default=str, ensure_ascii=False) + " " + " ".join(sorted(extra))


def build_index(syn: dict) -> dict[str, str]:
    idx: dict[str, list] = {}

    def add(key, obj):
        idx.setdefault(key, []).append(obj)

    for sid, p in syn["papers"].items():
        add(f"paper:{sid}", {k: p.get(k) for k in ("title", "authors", "year", "counts", "tally", "tally_by_purpose", "reader", "sound")})
        for did, d in (p.get("data") or {}).items():
            add(f"{sid}/{did}", d)
        for aid, a in (p.get("added") or {}).items():
            add(f"{sid}/{aid}", a)
        for mid, m in (p.get("models") or {}).items():
            add(f"{sid}/{mid}", m)
        for v in p.get("verdicts", []):
            add(f"{sid}/{v['comparison']}", v)
            add(f"{sid}/{v['printed']}", v)
        for r in p.get("refinements", []):
            add(f"{sid}/{r['id']}", r)
        for q in p.get("questions", []):
            add(f"{sid}/{q['id']}", q)
    for sid, b in (syn.get("builds") or {}).items():
        for vid, v in b["values"].items():
            if v["kind"] == "output":
                add(f"{sid}/{vid}", v)
        for rid, r in b["runs"].items():
            add(f"{sid}/{rid}", r)
    for f in syn["findings"]:
        add(f["subject"], f)
    for r in syn["relations"]:
        add(r["key"], r)
    for i, fam in enumerate(syn["families"]):
        add(f"family:{i + 1}", fam)
    for x in syn["cross_checks"]:
        add(cross_id(x), x)
    for c in syn["cited_values"]:
        add(c["datum"], c)
    for v in syn.get("validations", []):
        add(v["id"], v)
    for r in syn["references"]:
        add(f"ref:{r['source']}/{r['id']}", r)
    return {k: _material(*v) for k, v in idx.items()}


_NUM = re.compile(r"(?<![\w/.:])[-−]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def trace_check(sentences: list[Sentence], index: dict[str, str]) -> list[str]:
    problems = []
    for s in sentences:
        if not s.trace:
            problems.append(f"no trace: {s.text!r}")
            continue
        unknown = [t for t in s.trace if t not in index]
        if unknown:
            problems.append(f"unknown ids {unknown}: {s.text!r}")
            continue
        material = " ".join(index[t] for t in s.trace).replace("−", "-")
        text = s.text
        for t in sorted(s.trace, key=len, reverse=True):  # ids are not numbers
            text = text.replace(t, " ")
        for tok in _NUM.findall(text):
            tok = tok.replace("−", "-")
            if tok not in material and tok.lstrip("-") not in material:
                problems.append(f"number {tok} is not in what the sentence traces to: {s.text!r}")
    return problems


# --------------------------------------------------------------------------
# The review
# --------------------------------------------------------------------------


def _fmt(x) -> str:
    if isinstance(x, list):
        return "[" + ", ".join(_fmt(v) for v in x) + "]"
    if isinstance(x, float):
        return f"{x:.4g}"
    return "—" if x is None else str(x)


def _fmt_computed(x, se) -> str:
    """A computed value, with ± two standard errors when it has sampling error."""
    if isinstance(x, list):
        ses = se if isinstance(se, list) else [se] * len(x)
        return "[" + ", ".join(_fmt_computed(v, s) for v, s in zip(x, ses, strict=True)) + "]"
    if isinstance(x, float) and se:
        return f"{x:.4g} ± {2 * se:.2g}"
    return _fmt(x)


def review(syn: dict) -> list[Sentence]:
    S: list[Sentence] = []
    papers = syn["papers"]
    S.append(Sentence(
        "The record holds " + ", ".join(f"{p.get('title', sid)} ({sid})" for sid, p in papers.items()) + ".",
        [f"paper:{sid}" for sid in papers], "overview"))
    for sid, p in papers.items():
        if not p.get("sound"):
            S.append(Sentence(f"The record of {sid} is not sound yet, so it is not in the Synthesis.", [f"paper:{sid}"], "papers"))
            continue
        c, t = p["counts"], p["tally"]
        S.append(Sentence(
            f"{sid} was read by {p['reader']['name']} into {c['data']} printed values, {c['added']} added inputs, "
            f"{c['models']} models and {c['runs']} runs.", [f"paper:{sid}"], "papers"))
        S.append(Sentence(
            f"Against itself, {sid} has {t['reproduced']} results reproduced, {t['close']} close, "
            f"{t['not reproduced']} not reproduced and {t['no verdict']} without a verdict.", [f"paper:{sid}"], "papers"))
        for purpose, tp in (p.get("tally_by_purpose") or {}).items():
            if purpose == "reproduction":
                continue
            S.append(Sentence(
                f"Its {purpose.replace('_', ' ')} comparisons: {tp['reproduced']} reproduced, {tp['close']} close, "
                f"{tp['not reproduced']} not reproduced, {tp['no verdict']} without a verdict.", [f"paper:{sid}"], "papers"))
    for f in syn["findings"]:
        trace = [f["subject"]] + [x for x in f.get("trace", []) if x != f["subject"]]
        where = f" (p. {f['page']})" if f.get("page") else ""
        S.append(Sentence(f"{KIND_TEXT.get(f['kind'], f['kind'])}: {f['subject']}{where}. {f['detail']}.", trace, "findings"))
        if f.get("implicates"):
            named = f["implicates"][:6]
            more = " and more" if len(f["implicates"]) > len(named) else ""
            S.append(Sentence("It puts in doubt " + ", ".join(named) + more + ".", [f["subject"], *named], "findings"))
    for r in syn["relations"]:
        S.append(Sentence(f"{r['a']} {r['kind'].replace('_', ' ')} {r['b']}, {r['provenance']}, is {r['status'].replace('_', ' ')}: {r['detail']}.",
                          [r["key"]], "atlas"))
    for i, fam in enumerate(syn["families"]):
        S.append(Sentence(f"{', '.join(fam)} form a family.", [f"family:{i + 1}"], "atlas"))
    for x in syn["cross_checks"]:
        if x.get("status") != "checked":
            continue
        S.append(Sentence(
            f"Running {x['model']} on the inputs of {x['run']} gives {_fmt(x['computed_value'])} against "
            f"{x['printed']} printed as {x['printed_text']}: {x['verdict']}, given "
            + "; ".join(x["correspondences"]) + ".", [cross_id(x)], "cross"))
    for v in syn.get("validations", []):
        if v.get("status") != "checked":
            continue
        how = "fitted to" if v.get("purpose") == "fit_quality" else "judged against"
        S.append(Sentence(f"{v['model']} is {how} {v['against']}, measured in {v['against_record']} "
                          f"({v['id']}): {v['verdict']}" + (", given " + "; ".join(v["correspondences"]) if v["correspondences"] else "")
                          + ".", [v["id"]], "cross"))
    for c in syn["cited_values"]:
        if c.get("status") == "checked":
            S.append(Sentence(f"{c['datum']} prints {c['printed']} and says it comes from {c.get('cited_record', c['from_source'])}, "
                              f"which prints {c['cited_printed']}: {c['verdict']}.", [c["datum"]], "cross"))
    for r in [r for r in syn["references"] if r["would_settle"]][:5]:
        S.append(Sentence(f"Reading {r['text']}, cited by {r['source']}, would bear on {len(r['would_settle'])} open questions.",
                          [f"ref:{r['source']}/{r['id']}"], "next"))
    return S


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

SECTIONS = [("overview", "Overview"), ("papers", "Papers against themselves"), ("findings", "Findings"),
            ("atlas", "ModelAtlas"), ("cross", "Across papers"), ("next", "What to read next")]


def render_markdown(syn: dict, sentences: list[Sentence]) -> str:
    out = ["# Synthesis", ""]
    for key, title in SECTIONS:
        ss = [s for s in sentences if s.section == key]
        if not ss:
            continue
        out += [f"## {title}", ""]
        for s in ss:
            out.append(f"- {s.text} `[{', '.join(s.trace)}]`")
        out.append("")
    out += ["## Verdicts by paper", ""]
    for sid, p in syn["papers"].items():
        out += [f"### {sid}: {p.get('title', '')}", ""]
        if not p.get("sound"):
            out += ["Not sound:", ""] + [f"- {e}" for e in p.get("errors", [])] + [""]
            continue
        out += ["| comparison | purpose | printed | computed | verdict | page |", "|---|---|---|---|---|---|"]
        for v in p["verdicts"]:
            out.append(f"| {v['comparison']} | {v['purpose']} | {_fmt(v['printed_text'])} | {_fmt_computed(v['computed_value'], v.get('computed_se'))} | "
                       f"{v['verdict'] or 'error: ' + str(v['error'])} | {v['page'] or ''} |")
        out.append("")
        if p["cannot_check"]:
            out += ["Cannot be checked:", ""] + [f"- {next(iter(c.values()))}: {c['why']}" for c in p["cannot_check"]] + [""]
        if p["questions"]:
            out += ["Open questions:", ""] + [f"- **{q['kind']}** {q['text']} `[{', '.join(q['about'])}]`" for q in p["questions"]] + [""]
    return "\n".join(out)


CSS = """
:root{--bg:#fbfaf7;--fg:#22211f;--muted:#6b6963;--line:#dedbd2;--card:#fff;--accent:#534ab7;
--ok:#2f6b12;--close:#8a5a07;--bad:#a12d2d;--none:#6b6963;--code:#f1efe8}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#1c1b19;--fg:#ecebe6;--muted:#a9a69d;
--line:#3a3935;--card:#262522;--accent:#afa9ec;--ok:#97c459;--close:#efa94a;--bad:#f09595;--code:#2e2d2a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:1040px;margin:0 auto;padding:24px 16px 64px}h1{font-size:26px;margin:0 0 4px}
h2{font-size:19px;margin:36px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{font-size:16px;margin:22px 0 8px}.muted{color:var(--muted)}code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:12.5px;word-break:break-all}
ul{padding-left:20px}li{margin:6px 0}li,.card,.trace,td{overflow-wrap:anywhere}.trace{display:block;color:var(--muted);font-size:12px;margin-top:2px}
.tbl{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13.5px;background:var(--card)}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{font-weight:600}
.v{font-weight:600;white-space:nowrap}.v-reproduced{color:var(--ok)}.v-close{color:var(--close)}
.v-not{color:var(--bad)}.v-none{color:var(--none)}.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:10px 0}
.figs{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.figs figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px}
.figs img{width:100%;height:auto;display:block;background:#fff}.figs figcaption{font-size:12.5px;color:var(--muted);margin-top:6px}
details summary{cursor:pointer}.card ul{margin:6px 0}.kind{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--accent)}
"""


def _vcls(v) -> str:
    if v == "reproduced":
        return "v v-reproduced"
    if v == "close":
        return "v v-close"
    if v == "not reproduced":
        return "v v-not"
    return "v v-none"


def _img_src(figdir: Path | None, sid: str, fid: str) -> str:
    """The overlay as a data URI when its file is at hand, so the page stands alone; else a relative link."""
    rel = f"figures/{sid}/{fid}.png"
    if figdir is not None and (figdir / sid / f"{fid}.png").exists():
        return "data:image/png;base64," + base64.b64encode((figdir / sid / f"{fid}.png").read_bytes()).decode()
    return rel


def render_html(syn: dict, sentences: list[Sentence], title: str = "BoxGraph Synthesis",
                figdir: Path | None = None) -> str:
    e = H.escape
    o = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
         f"<title>{e(title)}</title><style>{CSS}</style></head><body><main>",
         f"<h1>{e(title)}</h1><p class=muted>An executable literature review: what each paper states, what checks out "
         f"within each paper, and what checks out across papers. Every sentence lists the record ids it rests on.</p>"]
    o.append("<h2>Findings</h2>")
    if not syn["findings"]:
        o.append("<p class=muted>No findings.</p>")
    rank = {k: i for i, k in enumerate(KIND_ORDER)}
    for f in sorted(syn["findings"], key=lambda f: (rank.get(f["kind"], 99), f["subject"])):
        page = f" · p. {f['page']}" if f.get("page") else ""
        quote = f"<div class=muted>“{e(f['quote'])}”</div>" if f.get("quote") else ""
        ev = f.get("evidence") or [f["detail"]]
        body = (f"<div>{e(ev[0])}</div>" if len(ev) == 1 else
                "<ul>" + "".join(f"<li>{e(x)}</li>" for x in ev) + "</ul>")
        imp = ""
        if f.get("implicates"):
            n = len(f["implicates"])
            imp = (f"<details class=trace><summary>puts in doubt {n} further node{'s' if n != 1 else ''}</summary>"
                   f"{e(', '.join(f['implicates']))}</details>")
        o.append(f"<div class=card><div class=kind>{e(KIND_TEXT.get(f['kind'], f['kind']))}</div>"
                 f"<div><code>{e(f['subject'])}</code>{e(page)}</div>{body}{quote}"
                 f"<div class=trace>trace: {e(', '.join(f.get('trace', [])))}</div>{imp}</div>")
    for key, title_ in SECTIONS:
        ss = [s for s in sentences if s.section == key]
        if not ss or key == "findings":
            continue
        o.append(f"<h2>{e(title_)}</h2><ul>")
        for s in ss:
            o.append(f"<li>{e(s.text)}<span class=trace>{e(', '.join(s.trace))}</span></li>")
        o.append("</ul>")
    o.append("<h2>Verdicts by paper</h2>")
    for sid, p in syn["papers"].items():
        o.append(f"<h3>{e(sid)}: {e(p.get('title', ''))}</h3>")
        if not p.get("sound"):
            o.append("<p>Not sound:</p><ul>" + "".join(f"<li>{e(x)}</li>" for x in p.get("errors", [])) + "</ul>")
            continue
        o.append("<div class=tbl><table><tr><th>comparison</th><th>purpose</th><th>printed</th><th>computed</th><th>verdict</th><th>page</th></tr>")
        for v in p["verdicts"]:
            verdict = v["verdict"] or f"error: {v['error']}"
            o.append(f"<tr><td><code>{e(v['comparison'])}</code></td><td>{e(v['purpose'])}</td><td>{e(_fmt(v['printed_text']))}</td>"
                     f"<td>{e(_fmt_computed(v['computed_value'], v.get('computed_se')))}</td><td class='{_vcls(v['verdict'])}'>{e(verdict)}</td><td>{e(str(v['page'] or ''))}</td></tr>")
        o.append("</table></div>")
        if p.get("figures"):
            o.append("<p class=muted>Figure readings, drawn over the figure (magenta: value and its interval):</p><div class=figs>")
            for fg in p["figures"]:
                src = _img_src(figdir, sid, fg["id"])
                mis = fg.get("residual_px") or [0, 0]
                o.append(f"<figure><img src='{e(src)}' alt='{e(fg['where'])}' loading=lazy>"
                         f"<figcaption><b>{e(fg['where'])}</b>, p. {fg['page']}: {e(fg['what'])}. "
                         f"Calibration misfit {mis[0]:.2f} px (x), {mis[1]:.2f} px (y).</figcaption></figure>")
            o.append("</div>")
        if p["cannot_check"]:
            o.append("<p class=muted>Cannot be checked:</p><ul>" + "".join(
                f"<li><code>{e(str(next(iter(c.values()))))}</code> {e(c['why'])}</li>" for c in p["cannot_check"]) + "</ul>")
        if p["questions"]:
            o.append("<p class=muted>Open questions:</p><ul>" + "".join(
                f"<li><b>{e(q['kind'].replace('_', ' '))}</b> {e(q['text'])}<span class=trace>{e(', '.join(q['about']))}</span></li>"
                for q in p["questions"]) + "</ul>")
    o.append("</main></body></html>")
    return "\n".join(o)


MISFIT_FLAG_PX = 1.0  # calibration misfit above this is shown as worth a look

FIGCHECK_CSS = """
.fc{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:14px;align-items:start}
@media (max-width:760px){.fc{grid-template-columns:1fr}}
.fc img{width:100%;height:auto;display:block;background:#fff;border:1px solid var(--line);border-radius:6px;cursor:zoom-in}
.fc img.zoom{width:auto;max-width:none;cursor:zoom-out}.imgbox{overflow:auto}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 10px}.chip{font-size:12px;border:1px solid var(--line);border-radius:999px;padding:2px 9px}
.chip.warn{border-color:var(--close);color:var(--close)}.chip.bad{border-color:var(--bad);color:var(--bad)}.chip.ok{border-color:var(--ok);color:var(--ok)}
.bar{position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:2;border-bottom:1px solid var(--line)}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}.toc a{margin-right:10px}
"""


def _figure_flags(fg: dict) -> list[tuple[str, str]]:
    """Chips for a figure reading: (css class, text). A class of warn or bad marks it for a look."""
    flags = []
    mis = fg.get("residual_px") or [0.0, 0.0]
    worst = max(abs(m) for m in mis)
    flags.append(("warn" if worst > MISFIT_FLAG_PX else "ok", f"calibration misfit {mis[0]:.2f} / {mis[1]:.2f} px"))
    if fg.get("skew_deg"):
        flags.append(("", f"deskewed {fg['skew_deg']:.2f}°"))
    pts = fg.get("readings") or []
    missing = sum(1 for p in pts if not p.get("found", True))
    flags.append(("bad" if missing else "ok", f"{len(pts) - missing}/{len(pts)} points found"))
    for err in fg.get("errors") or []:
        flags.append(("bad", str(err)))
    for u in fg.get("used_by") or []:
        cls = {"reproduced": "ok", "close": "warn", "not reproduced": "bad"}.get(u["verdict"], "")
        flags.append((cls, f"{u['comparison']}: {u['verdict'] or 'error'}"))
    if not fg.get("used_by"):
        flags.append(("", "used by no comparison"))
    return flags


def render_figure_check(syn: dict, figdir: Path | None = None, title: str = "Figure readings") -> str:
    """A page for checking digitized figures: each overlay beside its read points, intervals and verdicts."""
    e = H.escape
    o = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
         f"<title>{e(title)}</title><style>{CSS}{FIGCHECK_CSS}</style></head><body><main>",
         f"<h1>{e(title)}</h1><p class=muted>Every value read from a figure, drawn over the figure it came from. "
         f"Magenta marks are the read points with their intervals; check that each sits on the intended curve or "
         f"marker, at the intended x. Tap an image to see it at full size.</p>"]
    cards, toc = [], []
    n_all = n_flag = 0
    for sid, p in syn["papers"].items():
        figs = p.get("figures") or []
        if not figs:
            continue
        toc.append(f"<a href='#p-{e(sid)}'>{e(sid)} ({len(figs)})</a>")
        cards.append(f"<h2 id='p-{e(sid)}'>{e(sid)}: {e(p.get('title', ''))}</h2>")
        for fg in figs:
            flags = _figure_flags(fg)
            flagged = any(c in ("warn", "bad") for c, _ in flags)
            n_all += 1
            n_flag += flagged
            used = fg.get("used_by") or []
            per = used[0]["per_value"] if len(used) == 1 and isinstance(used[0].get("per_value"), list) else None
            pts = fg.get("readings") or []
            if per is not None and len(per) != len(pts):
                per = None
            rows = []
            for i, pt in enumerate(pts):
                half = (pt["hi"] - pt["lo"]) / 2 if pt.get("found", True) else None
                rel = f"{100 * half / abs(pt['y']):.2g}%" if half is not None and pt["y"] else "—"
                v = per[i] if per else None
                rows.append(f"<tr><td class=num>{e(_fmt(pt['x']))}</td><td class=num>{e(_fmt(pt.get('y')))}</td>"
                            f"<td class=num>[{e(_fmt(pt.get('lo')))}, {e(_fmt(pt.get('hi')))}]</td><td class=num>±{rel}</td>"
                            + (f"<td class='{_vcls(v)}'>{e(v)}</td>" if per else "")
                            + ("" if pt.get("found", True) else "<td class='v v-not'>not found</td>") + "</tr>")
            head = "<tr><th>x</th><th>y read</th><th>interval</th><th>±</th>" + ("<th>verdict</th>" if per else "") + "</tr>"
            chips = "".join(f"<span class='chip {c}'>{e(t)}</span>" for c, t in flags)
            notes = "".join(f"<li>{e(str(n))}</li>" for n in fg.get("notes") or [])
            cards.append(
                f"<div class='card fig' data-flagged='{int(flagged)}' id='f-{e(sid)}-{e(fg['id'])}'>"
                f"<div class=kind>{e(fg['where'])} · p. {e(str(fg['page']))} · <code>{e(fg['id'])}</code></div>"
                f"<div><b>{e(fg['what'])}</b></div><div class=chips>{chips}</div>"
                f"<div class=fc><div class=imgbox><img src='{e(_img_src(figdir, sid, fg['id']))}' alt='{e(fg['where'])}' "
                f"loading=lazy onclick=\"this.classList.toggle('zoom')\"></div>"
                f"<div class=tbl><table>{head}{''.join(rows)}</table>{f'<ul class=muted>{notes}</ul>' if notes else ''}</div></div></div>")
    o.append(f"<div class=bar><label><input type=checkbox id=only> show only the {n_flag} of {n_all} readings "
             f"worth a look</label><div class='toc muted'>{''.join(toc)}</div></div>")
    o += cards
    o.append("<script>document.getElementById('only').addEventListener('change',function(){var on=this.checked;"
             "document.querySelectorAll('.fig').forEach(function(c){c.style.display=on&&c.dataset.flagged==='0'?'none':''})})"
             "</script></main></body></html>")
    return "\n".join(o)
