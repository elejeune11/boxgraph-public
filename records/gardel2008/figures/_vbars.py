"""Fig. 5 E-G (PDF p. 6): per condition, a blue and a red square with vertical error bars,
drawn at the same column (the red over the blue).

Calibration from the image: the frame; the long ticks on the left edge carry the y labels
(the caller matched the label of the topmost long tick and the step); short ticks lie
halfway. The x positions are the long ticks on the bottom edge, one per condition, left to
right; the caller says which condition each is.
Per condition and colour, in a window of columns around the tick: for each row, the number
of pixels of that colour (`width`). An error-bar cap is a horizontal stroke wider than the
marker: rows whose width is at least 85% of the widest; consecutive rows form one stroke,
whose centre row is a bar end (the topmost and bottommost strokes). A marker row is a row
whose width is that of a square marker (45-80% of the widest). The marker centre is the
middle of the span from the first to the last marker row; where caps or the other colour
cover part of the marker, the span is shorter than the marker is wide, and the centre is
uncertain by half the difference, which is added to its interval. A bar end not found
(hidden) is taken as the mirror of the other about the centre, and the note says so.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("gardel_lib", Path(__file__).with_name("_lib.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


def calibrate(img, y_first_major, ystep):
    fr = L.frame(img)
    ty = L.ticks(img, fr["left"], (fr["top"] + 15, fr["bottom"] - 15), "y", 1, 160, lw=fr["lw_col"])
    ay, by, my, dy = L.grid_axis(ty, fr["top"], fr["bottom"], 0.0, 0.0, ystep, first_major=y_first_major,
                                 edge_tol=-1)
    # the condition columns: the long ticks on the top and bottom edges (a bar end can cover
    # a tick on either edge); a column found on both edges is taken once, at their mean
    cols = []
    for edge, d in ((fr["top"], 1), (fr["bottom"], -1)):
        tx = L.ticks(img, edge, (fr["left"] + 15, fr["right"] - 15), "x", d, 160, lw=fr["lw_row"])
        longest = max(t[1] for t in tx)
        cols += [c for c, ln in tx if ln > 0.75 * longest]
    merged = []
    for c in sorted(cols):
        if merged and c - merged[-1][-1] < 20:
            merged[-1].append(c)
        else:
            merged.append([c])
    cols = [float(np.mean(m)) for m in merged]
    return fr, ay, by, my, dy, cols


def strokes(rows):
    out = []
    for s, e in L.runs(rows):
        out.append((s + e - 1) / 2.0)
    return out


def read_one(img, mask, col, pitch, fr, ay, by, my):
    half = int(0.35 * pitch)
    c0, c1 = int(col) - half, int(col) + half
    m = mask.copy()
    m[:int(fr["top"]) + 8] = False
    m[int(fr["bottom"]) - 8:] = False
    width = m[:, c0:c1].sum(axis=1).astype(float)
    wmax = width.max()
    if wmax < 20:
        return None
    capm = width >= 0.85 * wmax
    mk = (width >= 0.45 * wmax) & (width < 0.85 * wmax)
    caps = strokes(capm)
    caps_t = [e - s for s, e in L.runs(capm)]
    mrows = np.where(mk)[0]
    # the marker: the biggest cluster of marker rows (gaps up to a cap's thickness allowed)
    if len(mrows) == 0:
        return None
    groups = np.split(mrows, np.where(np.diff(mrows) > 25)[0] + 1)
    g = max(groups, key=len)
    span = g[-1] - g[0] + 1
    # nominal marker size: the marker's own width in its rows
    nominal = float(np.median(width[g]))
    centre = (g[0] + g[-1]) / 2.0
    hidden = max(0.0, nominal - span)
    pr = 1.5 + hidden / 2.0 + my
    val = lambda r: (r - ay) / by
    y = val(centre)
    e = pr / abs(by)
    res = {"y": float(y), "lo": float(y - e), "hi": float(y + e), "px": [float(col), float(centre)],
           "note": f"marker rows {g[0]}-{g[-1]} ({span} px of a {nominal:.0f} px marker)"}
    up = [c for c in caps if c < centre - 2]
    dn = [c for c in caps if c > centre + 2]
    capt = float(np.median(caps_t)) if caps_t else 4.0
    pad = (capt / 2.0 + 1.0 + my) / abs(by)
    top = min(up) if up else None
    bot = max(dn) if dn else None
    if top is None and bot is None:
        res["note"] += "; no error bar caps found"
        return res
    if top is None:
        top = 2 * centre - bot
        res["note"] += "; upper bar end hidden, taken as the mirror of the lower"
    if bot is None:
        bot = 2 * centre - top
        res["note"] += "; lower bar end hidden, taken as the mirror of the upper"
    hi, lo = val(top), val(bot)
    res.update({"bar_lo": float(lo), "bar_hi": float(hi), "bar_lo_outer": float(lo - pad),
                "bar_hi_outer": float(hi + pad), "px_lo": float(top), "px_hi": float(bot)})
    res["note"] += f"; caps at rows {top:.1f} and {bot:.1f}"
    return res


def read_panel(img, colour, conditions, y_first_major, ystep):
    """conditions: the condition index of each long x tick, left to right."""
    fr, ay, by, my, dy, cols = calibrate(img, y_first_major, ystep)
    if len(cols) != len(conditions):
        raise ValueError(f"{len(cols)} long x ticks, expected {len(conditions)}")
    pitch = float(np.median(np.diff(cols)))
    mask = L.hue_mask(img, colour, min_sat=60)
    out = []
    for col, (idx, name) in zip(cols, conditions):
        r = read_one(img, mask, col, pitch, fr, ay, by, my)
        if r is None:
            out.append({"x": float(idx), "y": None, "note": f"{name}: no {colour} marker"})
            continue
        r["x"] = float(idx)
        r["note"] = f"{name}: {r['note']}" + (f"; y axis {dy}" if not out else "")
        out.append(r)
    return sorted(out, key=lambda d: d["x"])
