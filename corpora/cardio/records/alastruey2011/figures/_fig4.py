"""Shared reading code for Fig. 4 (PDF p. 8): the first 20 flow harmonics at the left renal midpoint,
log10 of the amplitude against frequency: measured (crosses), elastic (circles), visco-elastic (triangles).

Calibration, all from the image, with the frame, tick and legend finders of _fig3.py (same MATLAB
style): the inward tick marks on the bottom frame line with a dotted grid line from them, matched
to 5, 10, 15 Hz, and on the left frame line matched to 0, -1, -2 (log10 of ml/s); a straight-line
fit, whose largest misfit is reported and added to every interval.

Markers: the three legend markers are the templates (top to bottom in the legend: exp cross, elas
circle, visc triangle). Each dark component in the plot (grid dots, under 300 px, left out) is
compared with each template of about its size by the overlap of their masks, centres aligned
(intersection over union at least 0.6); one that matches is a single marker of that kind, any
other is several markers drawn over one another. Markers are grouped in columns (centres within
25 px). In a column:
  one single marker of the kind: its centre, +- 3 px; a triangle's data point is not at the centre
    of its bounding box (MATLAB centres '^' on its centroid, a quarter of its radius below the box
    centre, about 12 px here), so a triangle is taken 6 px below the box centre, +- 9 px;
  no single marker of the kind but overlapping markers: the kind is taken to be among them (every
    harmonic is plotted for all three), anywhere from half a template height inside the top to half
    inside the bottom of the overlapping blob;
  two single markers of the kind: unreadable.
Markers at 0 Hz are drawn on the left frame line and cut by it: their rows are kept (the shapes are
symmetric left to right) and their column is the frame line's centre.
Every interval also has the calibration misfit and 1 px. x is the centre column of the marker (or
blob) on the frequency axis.
"""

import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage

KINDS = ("exp", "elas", "visc")
IOU_MIN = 0.85  # single markers match their template at 0.95 or more, overlapping ones at 0.7 or less


def _f3():
    spec = importlib.util.spec_from_file_location("alastruey2011_fig3_for4", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _iou(a, b):
    h, w = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])

    def pad(m):
        out = np.zeros((h, w), bool)
        r0, c0 = (h - m.shape[0]) // 2, (w - m.shape[1]) // 2
        out[r0:r0 + m.shape[0], c0:c0 + m.shape[1]] = m
        return out

    pa, pb = pad(a), pad(b)
    best = 0.0
    for dr in (-2, -1, 0, 1, 2):
        for dc in (-2, -1, 0, 1, 2):
            sb = np.roll(np.roll(pb, dr, axis=0), dc, axis=1)
            u = (pa | sb).sum()
            best = max(best, (pa & sb).sum() / u if u else 0.0)
    return best


def analyse(image, xlabels, ylabels):
    f3 = _f3()
    g = image[..., :3].astype(float).mean(axis=2)
    dark = g < 128
    fr = f3.frame(dark)
    xt, yt = f3.ticks(dark, fr)
    xa, xb, xm = f3._fit(xt, xlabels, "x axis")
    ya, yb, ym = f3._fit(yt, ylabels, "y axis")
    leg = f3._legend(dark, fr)
    if leg is None:
        raise ValueError("no legend box found")
    # templates: the marker-sized components in the left third of the legend, top to bottom
    lr0, lr1, lc0, lc1 = leg
    sub = dark[lr0 + 12:lr1 - 12, lc0 + 12:lc0 + 12 + (lc1 - lc0) // 3]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    temps = []
    for k, sl in enumerate(ndimage.find_objects(lab), start=1):
        m = lab[sl] == k
        if m.sum() > 1000:
            temps.append((sl[0].start, m))
    temps.sort(key=lambda t: t[0])
    if len(temps) != 3:
        raise ValueError(f"found {len(temps)} legend markers, expected 3")
    temp = {k: t[1] for k, t in zip(KINDS, temps)}
    inside = np.zeros_like(dark)
    inside[fr["top"] + 3:fr["bottom"] - 3, fr["left"] + 3:fr["right"] - 3] = True
    inside[max(lr0, 0):lr1, max(lc0, 0):lc1] = False
    lab, n = ndimage.label(dark & inside, structure=np.ones((3, 3)))
    comps = []
    for k, sl in enumerate(ndimage.find_objects(lab), start=1):
        m = lab[sl] == k
        if m.sum() < 300:
            continue
        kind, scores = None, {}
        for kk, t in temp.items():
            if abs(m.shape[0] - t.shape[0]) <= 6 and abs(m.shape[1] - t.shape[1]) <= 6:
                scores[kk] = _iou(m, t)
                if scores[kk] >= IOU_MIN:
                    kind = kk
        cx = (sl[1].start + sl[1].stop - 1) / 2.0
        if sl[1].start <= fr["left"] + 4:
            # markers drawn on the left frame line (0 Hz) are cut by it: their rows are whole (the
            # shapes are symmetric left to right) and their centre is the frame line itself
            kind, cx = None, fr["left"] - 5.0
        comps.append({"r0": sl[0].start, "r1": sl[0].stop - 1, "c0": sl[1].start, "c1": sl[1].stop - 1,
                      "kind": kind, "cx": cx, "scores": scores})
    comps.sort(key=lambda c: c["cx"])
    cols = []
    for c in comps:
        if cols and c["cx"] - cols[-1][-1]["cx"] <= 25:
            cols[-1].append(c)
        else:
            cols.append([c])
    return {"x": (xa, xb, xm), "y": (ya, yb, ym), "cols": cols, "temp": temp}


def read_kind(image, kind, xlabels, ylabels):
    a = analyse(image, xlabels, ylabels)
    xa, xb, xm = a["x"]
    ya, yb, ym = a["y"]
    th = a["temp"][kind].shape[0]
    out = []
    for col in a["cols"]:
        pure = [c for c in col if c["kind"] == kind]
        merged = [c for c in col if c["kind"] is None]
        if len(pure) == 1:
            c = pure[0]
            yc = (c["r0"] + c["r1"]) / 2.0
            half = 3.0
            if kind == "visc":
                yc, half = yc + 6.0, 9.0
            lo, hi = yc - half, yc + half
            cx, note = c["cx"], "single marker"
        elif not pure and merged:
            r0 = min(c["r0"] for c in merged)
            r1 = max(c["r1"] for c in merged)
            lo, hi = r0 + th / 2.0, r1 - th / 2.0
            if hi < lo:
                lo = hi = (r0 + r1) / 2.0
            if kind == "visc":
                lo, hi = lo - 3.0, hi + 9.0
            yc = (lo + hi) / 2.0
            cx = float(np.mean([c["cx"] for c in merged])) if any(c["c0"] <= 0 or c["cx"] < c["c0"] for c in merged) \
                else (min(c["c0"] for c in merged) + max(c["c1"] for c in merged)) / 2.0
            note = "within overlapping markers"
        else:
            continue
        pad = ym + 1.0
        lo, hi = lo - pad, hi + pad
        x = xa + xb * cx
        # the axis is printed as log10 of the amplitude in ml/s: values are returned in ml/s
        v, v1, v2 = (10.0 ** (ya + yb * r) for r in (yc, lo, hi))
        out.append({"x": float(x), "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(cx), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{note}; x misfit {xm:.1f} px, y misfit {ym:.1f} px"})
    return out
