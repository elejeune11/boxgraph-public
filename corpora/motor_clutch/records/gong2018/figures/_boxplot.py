"""Shared code for the box plots of Figs. 4D and 5D of gong2018 (PDF pp. 6, 7):
measured cell spreading area on elastic (red box) and viscoelastic (blue box)
gels, with the model's predicted area drawn inside each box (a cross and a
triangle).

Axis: y by _bars.calibrate_y (outward ticks of the y axis, labels times 1e4 um^2).
x: the categories are names ("Elastic", "Viscoelastic"): the x of a reading is the
box's position from the left, 0 and 1.

A box is the largest blob of its fill colour.  Rows are read in two columns at an
eighth of the box's width from each side (away from the marker and the whisker),
and averaged:
  median    the dark line inside the fill: the middle of its run of dark rows;
  quartiles the outlines above and below the fill: the middle of each run of
            dark rows (the box's top and bottom);
  whiskers  in the box's centre column, the dark line followed from the box's
            outline up and down, bridging gaps of 4 rows upward
            (an outlier circle sits 6 rows above the cap) and 8 rows downward
            (the lower whisker starts a few rows below the outline); its ends are the caps,
            taken half a line width inside the last dark row.
`read_box(kind="box")` returns the median with the quartiles as its bar,
`kind="whiskers"` the median with the whisker ends as its bar.  The caption does
not say what the box and whiskers show.
The predicted marker: the dark pixels inside the box's middle half, opened by a
disk of radius `open_r` (wider than the median line, narrower than the marker's
strokes); the largest blob, at the centre of its bounding box (`center_px` allows
for a triangle whose plotted point is not that centre).
Intervals (95%): half the dark run, one source pixel (`src_px`), the calibration
misfit and half a pixel.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi


def _load(name):
    spec = importlib.util.spec_from_file_location(f"gong2018{name}", Path(__file__).with_name(f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _runs(v):
    idx = np.nonzero(v)[0]
    out, cur = [], []
    for i in list(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            out.append((cur[0], cur[-1]))
            cur = []
        if i is not None:
            cur.append(i)
    return out


def _box(img, color, tol):
    f = img.astype(float)
    m = np.sqrt(((f - np.asarray(color, float)) ** 2).sum(axis=2)) <= tol
    # the median line splits the fill: close across it
    m = ndi.binary_closing(m, structure=np.ones((31, 1), bool))
    m = ndi.binary_opening(m, structure=np.ones((5, 5), bool))
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    k = int(np.argmax(sizes)) + 1
    sl = ndi.find_objects(lab)[k - 1]
    return sl[1].start, sl[1].stop, sl[0].start, sl[0].stop


def read_box(img, s, kind):
    ya, _ = _load("_bars").calibrate_y(img, s)
    # black lines: every channel dark (a saturated red or blue fill has one channel at 255)
    dark = img.max(axis=2) < s.get("dark", 100)
    src = s.get("src_px", 8)
    res = max(ya.residual_px, 0.5)
    out = []
    for pos, (color, tol) in enumerate(s["boxes"]):
        ca, cb, ra, rb = _box(img, color, tol)
        w = cb - ca
        meds, tops, bots = [], [], []
        for c in (int(ca + w / 8), int(cb - w / 8)):
            col = dark[:, c]
            runs = _runs(col[ra - 40:rb + 40])
            runs = [(a + ra - 40, b + ra - 40) for a, b in runs]
            inside = [r for r in runs if r[0] > ra + 3 and r[1] < rb - 3]
            above = [r for r in runs if r[1] <= ra + 3]
            below = [r for r in runs if r[0] >= rb - 3]
            if not (inside and above and below):
                continue
            meds.append(max(inside, key=lambda r: r[1] - r[0]))
            tops.append(above[-1])
            bots.append(below[0])
        if not meds:
            out.append({"x": float(pos), "y": None, "note": "box lines not found"})
            continue
        mid = lambda rs: float(np.mean([(a + b + 1) / 2 for a, b in rs]))  # noqa: E731
        half = lambda rs: float(np.mean([(b + 1 - a) / 2 for a, b in rs]))  # noqa: E731
        row = mid(meds)
        e = half(meds) + src + 0.5 + res
        lo, hi = sorted((ya.to_value(row + e), ya.to_value(row - e)))
        rec = {"x": float(pos), "y": ya.to_value(row), "lo": lo, "hi": hi, "px": [(ca + cb) / 2, row],
               "px_lo": row - e, "px_hi": row + e, "note": f"median line at row {row:.0f}"}
        if kind == "box":
            t, b = mid(tops), mid(bots)
            et, eb = half(tops) + src + res, half(bots) + src + res
            rec["note"] += f"; box (quartiles, as drawn) rows {t:.0f}-{b:.0f}"
        else:
            cc = int((ca + cb) / 2)
            strip = dark[:, cc - 3:cc + 4].any(axis=1)
            top_out = min(r[0] for r in tops)
            i, last, miss = top_out, top_out, 0
            while i > 0:
                i -= 1
                if strip[i]:
                    last, miss = i, 0
                else:
                    miss += 1
                    if miss > 4:
                        break
            up = last
            bot_out = max(r[1] for r in bots)
            i, last, miss = bot_out, bot_out, 0
            while i < len(strip) - 1:
                i += 1
                if strip[i]:
                    last, miss = i, 0
                else:
                    miss += 1
                    if miss > 8:
                        break
            down = last
            lw = s.get("line_w", 8)
            t, b = up + lw / 2, down + 1 - lw / 2
            et = eb = lw / 2 + src + res
            rec["note"] += f"; whiskers rows {up}-{down} at column {cc}"
        rec["bar_hi"], rec["bar_lo"] = ya.to_value(t), ya.to_value(b)
        rec["bar_hi_outer"], rec["bar_lo_outer"] = ya.to_value(t - et), ya.to_value(b + eb)
        out.append(rec)
    return out


def read_markers(img, s):
    ya, _ = _load("_bars").calibrate_y(img, s)
    dark = img.max(axis=2) < s.get("dark", 100)
    src = s.get("src_px", 8)
    res = max(ya.residual_px, 0.5)
    out = []
    for pos, (color, tol) in enumerate(s["boxes"]):
        ca, cb, ra, rb = _box(img, color, tol)
        w = cb - ca
        m =np.zeros_like(dark)
        a, b = int(ca + w / 4), int(cb - w / 4)
        m[ra - 60:rb + 60, a:b] = dark[ra - 60:rb + 60, a:b]
        r = s["open_r"]
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        m = ndi.binary_opening(m, structure=np.hypot(yy, xx) <= r)
        lab, n = ndi.label(m)
        if n == 0:
            out.append({"x": float(pos), "y": None, "note": "no marker found"})
            continue
        sizes = ndi.sum(m, lab, range(1, n + 1))
        k = int(np.argmax(sizes)) + 1
        rows = np.nonzero((lab == k).any(axis=1))[0]
        cols = np.nonzero((lab == k).any(axis=0))[0]
        row = (rows.min() + rows.max() + 1) / 2
        e = src + 0.5 + res + s["center_px"][pos]
        lo, hi = sorted((ya.to_value(row + e), ya.to_value(row - e)))
        out.append({"x": float(pos), "y": ya.to_value(row), "lo": lo, "hi": hi,
                    "px": [(cols.min() + cols.max() + 1) / 2, row], "px_lo": row - e, "px_hi": row + e,
                    "note": f"marker bounding box rows {rows.min()}-{rows.max()}"})
    return out
