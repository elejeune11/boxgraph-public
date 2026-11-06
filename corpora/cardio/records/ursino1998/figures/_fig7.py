"""Shared reading code for Fig. 7 (p. 8): open-loop static responses to carotid sinus pressure.
Six panels, each a spreadsheet chart (calibration as in _excel.py, every printed label matched to
its tick; the first x label and the lowest y label stand where the axes cross).

Model results are thick lines (continuous: intact; long dashes: vagotomized); measured series are
markers joined by thin dashed lines. A model line is read as the thick ink (surviving an opening
with a disk of radius 8 px, which removes every thin line) in long pieces (continuous line) or
short ones (dashed line), with the markers' own ink taken out. Brunner's data (top panels) are
means with SD drawn as three diamonds at one pressure (mean - SD, mean, mean + SD), each group
joined to the point at high pressure by its own line: the middle diamond is the mean, the outer two
the ends of the SD bar.
"""
import importlib.util
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location(
    "_excel", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_excel.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)
u = X.u

N5 = [0, 0.5, 1, 1.5, 2]
PANELS = {
    "a": dict(xvals=N5, yvals=[-2, 2, 6, 10], legend=(1900, 100, 3425, 560)),
    "b": dict(xvals=N5, yvals=[-2, 2, 6, 10], legend=(2000, 250, 3465, 720)),
    "c": dict(xvals=[0, 50, 100, 150], yvals=[-0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], legend=(950, 300, 2250, 800)),
    "d": dict(xvals=N5, yvals=[0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8], legend=(2250, 0, 3550, 1000)),
    "e": dict(xvals=N5, yvals=[0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8], legend=(2300, 0, 3465, 950)),
    "f": dict(xvals=N5, yvals=[0.6, 0.8, 1, 1.2, 1.4], legend=(2180, 50, 3425, 830)),
}


def panel(image, name):
    return X.Panel(image, x_at_yaxis=True, y_at_xaxis=True, **PANELS[name])


def typical(pts, tol_a=0.35, tol_w=0.25):
    """Markers of the common size: drop blobs that are thick ink where lines and markers meet."""
    if len(pts) < 3:
        return pts
    ma = float(np.median([q["area"] for q in pts]))
    mw = float(np.median([q["w"] for q in pts]))
    return [q for q in pts if abs(q["area"] - ma) < tol_a * ma and abs(q["w"] - mw) < tol_w * mw]


def markers(p, kind):
    """Markers of one kind in panel p: (col, row, half-size) of each."""
    if kind in ("diamond", "square", "circle", "triangle"):
        # markers are about 100-120 px across, the thick model lines about 30 px: a disk of
        # radius 22 px keeps only the markers (each panel has one kind of filled marker)
        blobs = p.filled(22, kinds=None, amin=2000)
        if not blobs:
            return []
        mw = float(np.median([q["w"] for q in blobs]))
        mh = float(np.median([q["h"] for q in blobs]))
        out = []
        for q in blobs:
            if q["w"] < 0.8 * mw or q["h"] < 0.8 * mh:
                continue  # thick ink where lines cross, not a marker
            if q["w"] <= 1.3 * mw and q["h"] <= 1.3 * mh:
                out.append(dict(col=q["bcol"], row=q["brow"], half=max(q["w"], q["h"]) / 2.0, note=""))
                continue
            if q["w"] <= 1.65 * mw and q["h"] <= 1.3 * mh:
                # a marker with a thick line running into one side: its centre is ambiguous by
                # the excess width
                ex = (q["w"] - mw) / 2.0
                out.append(dict(col=q["bcol"], row=q["brow"], half=max(q["w"], q["h"]) / 2.0,
                                note=f"a line runs into the marker; its centre is uncertain by {ex:.0f} px across",
                                extra_px=0.0))
            if 1.65 * mw < q["w"] < 2.4 * mw and q["h"] <= 1.3 * mh:
                # two markers overlapping side by side: one at each end of the blob
                for c0 in (q["c0"], q["c1"] - int(round(mw))):
                    sub = q["mask"][:, c0 - q["c0"]: c0 - q["c0"] + int(round(mw))]
                    rows = np.flatnonzero(sub.any(axis=1))
                    out.append(dict(col=c0 + mw / 2.0, row=q["r0"] + (rows.min() + rows.max() + 1) / 2.0,
                                    half=mw / 2.0 + 10,
                                    note="two overlapping markers, split at the common marker width"))
        return out
    if kind in ("open_square", "open_circle"):
        pts = typical(p.open(300, 8000, kinds={kind.split("_")[1]}))
        return [dict(col=q["bcol"], row=q["brow"], half=max(q["w"], q["h"]) / 2.0 + 8) for q in pts]
    pts = p.crosses(arm=26, thin_max=7, kinds=[kind], frac=0.7)
    return [dict(col=q["col"], row=q["row"], half=30.0) for q in pts]


def read_markers(image, name, kind, note):
    p = panel(image, name)
    out = []
    for q in sorted(markers(p, kind), key=lambda q: q["col"]):
        extra = q.get("note", "")
        err = 4.0 + (10.0 if extra else 0.0) + p.ycal.err
        out.append(u.point(p.xcal, p.ycal, q["col"], q["row"], err,
                           "; ".join(s for s in (note, extra, p.note()) if s)))
    return p.finish(out)


def read_brunner(image, name):
    p = panel(image, name)
    pts = sorted(markers(p, "diamond"), key=lambda q: q["col"])
    groups = []
    for q in pts:
        if groups and abs(q["col"] - groups[-1][0]["col"]) < 30:
            groups[-1].append(q)
        else:
            groups.append([q])
    out = []
    e = 4.0 + p.ycal.err
    for g in groups:
        g = sorted(g, key=lambda q: q["row"])
        col = float(np.mean([q["col"] for q in g]))
        if len(g) == 3:
            d = u.point(p.xcal, p.ycal, col, g[1]["row"], e,
                        "middle diamond of three: the mean; the outer two are mean - SD and mean + SD; " + p.note(),
                        bar=(g[0]["row"], g[2]["row"], e))
        elif len(g) == 1:
            half = g[0]["half"]
            d = u.point(p.xcal, p.ycal, col, g[0]["row"], e,
                        "one diamond: the three coincide, so the SD bar is within the marker; " + p.note(),
                        bar=(g[0]["row"] - half, g[0]["row"] + half, e))
        else:
            continue
        out.append(d)
    return p.finish(out)


def model_mask(p, dashed=False, erase=()):
    thick = ndimage.binary_opening(p.m, structure=X.disk(8))
    yy, xx = np.mgrid[0:thick.shape[0], 0:thick.shape[1]]
    for q in erase:
        thick[(xx - q["col"]) ** 2 + (yy - q["row"]) ** 2 <= (q["half"] + 6) ** 2] = False
    keep = np.zeros_like(thick)
    for b in u.blobs(thick):
        long_piece = b["w"] > 300
        if (long_piece and not dashed) or (dashed and not long_piece and b["w"] > 60 and b["area"] > 1500):
            keep[b["r0"]:b["r1"], b["c0"]:b["c1"]] |= b["mask"]
    return keep


def read_model(image, name, at, erase_kinds=(), dashed=False):
    p = panel(image, name)
    erase = [q for k in erase_kinds for q in markers(p, k)]
    m = model_mask(p, dashed, erase)
    if dashed:
        out = []
        for x in at:
            col = int(p.xcal.px(x))
            rs = u.column_runs(m, col)
            if len(rs) == 1:
                out += u.read_line(m, p.xcal, p.ycal, [x], pick=lambda c, r: r[0] if len(r) == 1 else None)
            else:
                out.append({"x": x, "y": None, "px": [p.xcal.px(x), 0.0],
                            "note": f"{len(rs)} dashes of the dashed line here"})
    else:
        out = u.read_line(m, p.xcal, p.ycal, at)
    for d in out:
        d["note"] = (d.get("note", "") + " " + p.note()).strip()
    return p.finish(out)
