"""Shared reading code for Figs. 5 (p. 7) and 8 (p. 9): spreadsheet charts of several marker
series. Calibration as in _excel.py (every printed label matched to its tick).

Markers are about 120 px across, the joining lines about 10 px thick. Filled markers are the ink
surviving an opening with a disk of radius 22 px, kept when of single-marker size (two touching
markers are left out). Open markers are the holes in the ink, the two halves of a hole cut by a
line joined back. Which series a marker belongs to:
  Fig. 5 top     the curves do not cross for Pra >= 2 mmHg and are ordered as the legend: at
                 each Pra, the filled markers from top to bottom are diamonds (62 mmHg),
                 triangles (87) and circles (122), the open ones squares (82) and circles (102);
                 a column without the full set is left out
  Fig. 5 bottom  filled diamonds (model, the only filled kind) and open circles (Kostiuk et al.)
  Fig. 8         filled squares have ink in the four corners of their box (over 60% of each
                 corner patch, on average), filled circles do not; open triangles are the only
                 open markers
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "_excel", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_excel.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)
u = X.u

PANELS = {
    "8a": dict(xvals=[20, 40, 60, 80, 100, 120, 140, 160], yvals=[0, 40, 80, 120, 160, 200], legend=(2450, 40, 3505, 880)),
    "8b": dict(xvals=[60, 100, 140, 180], yvals=[0, 40, 80, 120, 160, 200], legend=(2380, 40, 3380, 880)),
    "5top": dict(xvals=[0, 2, 4, 6, 8, 10], yvals=[0, 40, 80, 120, 160, 200], legend=(450, 60, 2350, 1450)),
    "5bot": dict(xvals=[60, 100, 140], yvals=[60, 80, 100, 120], legend=(2650, 350, 3880, 850)),
}


def panel(image, name):
    return X.Panel(image, x_at_yaxis=True, y_at_xaxis=True, **PANELS[name])


def filled(p):
    bl = p.filled(22, amin=3000)
    if not bl:
        return []
    mw = float(np.median([b["w"] for b in bl]))
    mh = float(np.median([b["h"] for b in bl]))
    return [b for b in bl if 0.8 * mw <= b["w"] <= 1.25 * mw and 0.8 * mh <= b["h"] <= 1.25 * mh]


def opened(p):
    pieces = [b for b in p.open(300, 8000) if b["w"] <= 110 and b["h"] <= 110]
    groups = []
    for b in sorted(pieces, key=lambda b: (b["bcol"], b["brow"])):
        for g in groups:
            if abs(g["bcol"] - b["bcol"]) < 30 and abs(g["brow"] - b["brow"]) < 60:
                g["parts"].append(b)
                g["r0"], g["r1"] = min(g["r0"], b["r0"]), max(g["r1"], b["r1"])
                g["c0"], g["c1"] = min(g["c0"], b["c0"]), max(g["c1"], b["c1"])
                break
        else:
            groups.append(dict(parts=[b], r0=b["r0"], r1=b["r1"], c0=b["c0"], c1=b["c1"], bcol=b["bcol"], brow=b["brow"]))
    out = []
    for g in groups:
        w, h = g["c1"] - g["c0"], g["r1"] - g["r0"]
        if w < 55:
            continue
        a = sum(q["area"] for q in g["parts"])
        out.append(dict(col=(g["c0"] + g["c1"]) / 2.0, row=(g["r0"] + g["r1"]) / 2.0, w=w, h=h,
                        fill=a / float(w * h), split=len(g["parts"]) > 1,
                        full=h >= 0.85 * w))
    return out


def _columns(items, key="col", tol=40):
    cols = []
    for it in sorted(items, key=lambda q: q[key]):
        if cols and abs(it[key] - cols[-1][-1][key]) < tol:
            cols[-1].append(it)
        else:
            cols.append([it])
    return cols


def _pt(p, col, row, err, note):
    return u.point(p.xcal, p.ycal, col, row, err + p.ycal.err, note + "; " + p.note())


def read_ranked(image, name, which, rank, n):
    """Marker number `rank` (from the top) of the n of its kind ('filled' or 'open') at each x."""
    p = panel(image, name)
    if which == "filled":
        items = [dict(col=b["bcol"], row=b["brow"]) for b in filled(p)]
    else:
        items = opened(p)
    out = []
    for c in _columns(items):
        if len(c) != n:
            continue
        q = sorted(c, key=lambda q: q["row"])[rank]
        err = 4.0
        note = f"{which} marker {rank + 1} of {n} from the top at this x"
        if which == "open" and not q.get("full", True):
            err += (q["w"] - q["h"]) / 2.0
            note += "; part of its hole is covered by a line: the interval covers it"
        out.append(_pt(p, q["col"], q["row"], err, note))
    return p.finish(out)


def read_kind(image, name, kind):
    """Fig. 5 bottom and Fig. 8: markers of one kind ('fsquare', 'fcircle', 'fdiamond', 'open')."""
    p = panel(image, name)
    out = []
    if kind == "open":
        # (spaces enclosed between crossing lines are holes too: a marker's hole has the
        # markers' common size and a closed outline's fill)
        ops = opened(p)
        if ops:
            mw = float(np.median([q["w"] for q in ops]))
            ops = [q for q in ops if abs(q["w"] - mw) <= 0.15 * mw and q["h"] <= 1.15 * mw
                   and (not q["full"] or 0.45 <= q["fill"] <= 0.8 or name == "5bot")]
        for q in sorted(ops, key=lambda q: q["col"]):
            err = 4.0 + (0.0 if q["full"] else (q["w"] - q["h"]) / 2.0)
            out.append(_pt(p, q["col"], q["row"], err, "open marker, at the centre of its hole"
                           + ("" if q["full"] else "; part of its hole is covered by a line")))
    else:
        for b in sorted(filled(p), key=lambda b: b["bcol"]):
            # a square has ink in the corners of its box, a circle has none
            r0, r1, c0, c1 = b["r0"], b["r1"], b["c0"], b["c1"]
            k8 = max(4, (c1 - c0) // 8)
            corners = [p.m[r0 + 2:r0 + 2 + k8, c0 + 2:c0 + 2 + k8], p.m[r0 + 2:r0 + 2 + k8, c1 - 2 - k8:c1 - 2],
                       p.m[r1 - 2 - k8:r1 - 2, c0 + 2:c0 + 2 + k8], p.m[r1 - 2 - k8:r1 - 2, c1 - 2 - k8:c1 - 2]]
            f = float(np.mean([c.mean() for c in corners]))
            # (between the two, a marker overlapped by another is left out)
            k = "fsquare" if f > 0.6 else ("fcircle" if f < 0.25 else "unclear")
            if k == kind or kind == "fany":
                out.append(_pt(p, b["bcol"], b["brow"], 4.0,
                               f"filled marker (corners {f:.2f} inked), at the centre of its box"))
    return p.finish(out)
