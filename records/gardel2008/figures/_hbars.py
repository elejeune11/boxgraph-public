"""Fig. 4 D (PDF p. 5): coloured squares with horizontal error bars, one row per condition.

Calibration from the image: the plot frame (the four longest dark lines), and the
tick marks pointing up from the bottom edge. The long (major) ticks lie between the
frame edges at equal steps; the frame edges themselves carry the end labels. The
caller says which values the end labels and majors have (the printed labels it matched).
Markers: blobs of one colour about the size of a square marker; their centroid is
the mean. Error bars: from the marker the bar is followed left and right along its
row in the same colour; it ends in a vertical cap, whose centre column is the bar end.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("gardel_lib", Path(__file__).with_name("_lib.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)

# the four conditions, one colour each (the legend of Fig. 4 C; rows of Fig. 4 D top to bottom)
CONDITIONS = [("red", 1, "CONTROL"), ("green", 2, "BLEB"), ("blue", 3, "CA-RAC"), ("black", 4, "CA-RHO")]


def calibrate(img, left_value, right_value, step):
    """The long ticks between the frame edges carry the labels left_value + k*step (k >= 1); the
    short ticks lie halfway between. The edge whose label sits on it (checked: it lies one tick
    step beyond the last tick) is added; an edge that does not lie on the tick grid is not used."""
    fr = L.frame(img)
    lw = fr["lw_row"]
    tk = L.ticks(img, fr["bottom"], (fr["left"] + 15, fr["right"] - 15), "x", -1, 120, lw=lw)
    a, b, mis, desc = L.grid_axis(tk, fr["left"], fr["right"], left_value, right_value, step)
    return fr, a, b, mis, desc


def _cap(mask, r, c_end, direction):
    """Centre column of the vertical cap at the end of a bar that ends near column c_end."""
    h = mask.shape[0]
    r0, r1 = max(0, int(r) - 60), min(h, int(r) + 61)
    lo, hi = int(c_end) - 25, int(c_end) + 26
    ext = np.array([mask[r0:r1, c].sum() for c in range(lo, hi)], dtype=float)
    # the cap: columns whose vertical extent is well above the bar line's own thickness
    thr = 0.5 * ext.max()
    on = np.where(ext >= thr)[0]
    if len(on) == 0 or ext.max() < 15:
        return None, None
    # the cap run nearest the end
    groups = np.split(on, np.where(np.diff(on) > 1)[0] + 1)
    g = groups[-1] if direction > 0 else groups[0]
    w = ext[g]
    return float((g + lo) @ w / w.sum()), float(len(g))


def read_rows(img, left_value, right_value, step):
    fr, a, b, mis, n = calibrate(img, left_value, right_value, step)
    val = lambda c: (c - a) / b
    pxv = abs(b)
    out = []
    inside = np.zeros(img.shape[:2], bool)
    inside[int(fr["top"]) + 10:int(fr["bottom"]) - 10, int(fr["left"]) + 10:int(fr["right"]) - 10] = True
    for color, idx, name in CONDITIONS:
        m_marker = L.hue_mask(img, color, min_sat=60) & inside
        m_bar = (L.hue_mask(img, color, min_sat=25, max_gray=245) if color != "black"
                 else (L.gray(img) < 140) & (L.sat(img) < 60)) & inside
        bl = [x for x in L.blobs(m_marker, 2000, open_iter=12)
              if 0.6 < (x["r1"] - x["r0"]) / max(1, x["c1"] - x["c0"]) < 1.6]
        if len(bl) != 1:
            out.append({"x": float(idx), "y": None, "note": f"{name}: {len(bl)} square markers of colour {color}"})
            continue
        mk = bl[0]
        half = 0.5 * (mk["c1"] - mk["c0"])
        r, c = mk["r"], mk["c"]
        y = val(c)
        e = (1.5 + mis) / pxv
        row = {"x": float(idx), "y": float(y), "lo": float(y - e), "hi": float(y + e), "px": [c, r],
               "note": f"{name}: marker centroid; x axis {n}, misfit {mis:.2f} px, {pxv:.1f} px per unit"}
        ends = {}
        for d in (-1, 1):
            start = mk["c1"] + 2 if d > 0 else mk["c0"] - 3
            last = L.follow(m_bar, r, start, 0, d, gap=10, band=6)
            if last is None or abs(last[1] - start) < 20:
                continue
            cap, cw = _cap(m_bar, r, last[1], d)
            if cap is not None:
                ends[d] = (cap, cw)
        if -1 in ends and 1 in ends:
            (cl, wl), (cr, wr) = ends[-1], ends[1]
            v1, v2 = sorted((val(cl), val(cr)))
            p = (0.5 * max(wl, wr) + 1.0 + mis) / pxv
            row.update({"bar_lo": float(v1), "bar_hi": float(v2), "bar_lo_outer": float(v1 - p),
                        "bar_hi_outer": float(v2 + p)})
            row["note"] += f"; error bar caps at columns {cl:.1f} and {cr:.1f}"
        else:
            row["note"] += "; error bar caps not both found"
        out.append(row)
    return out
