"""Fig. 1 D, F (PDF p. 2): notched box plots, one per cell region. The caption: box = 25% (lower
bound), median (middle line) and 75% (upper bound); whiskers = nearest observations within 1.5
times the interquartile range; notches = 95% confidence interval of the median; + = outliers.

Calibration from the image: the frame; the categories are the ticks on the bottom edge (left
to right, the caller names them); y from the ticks on the left edge, all of one length, the
topmost labelled by the caller, one label step apart.
Per category, in the columns around its tick: the median is the red horizontal stroke that
spans most of the box (the outliers' + marks are much narrower); the box bounds are the blue
horizontal strokes spanning most of the box (the topmost and bottommost); the whisker ends are
the black horizontal caps (topmost and bottommost). Each value is the stroke's centre row; its
interval is half the stroke's thickness, the calibration misfit and 1 px.
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
    tx = L.ticks(img, fr["bottom"], (fr["left"] + 15, fr["right"] - 15), "x", -1, 80, lw=fr["lw_row"])
    ty = L.ticks(img, fr["left"], (fr["top"] + 15, fr["bottom"] - 15), "y", 1, 80, lw=fr["lw_col"])
    ay, by, my, dy = L.grid_axis(ty, fr["top"], fr["bottom"], 0.0, 0.0, ystep, first_major=y_first_major,
                                 edge_tol=-1, all_major=True)
    cols = sorted(c for c, _ in tx)
    return fr, cols, ay, by, my, dy


def strokes(mask, c, half, frac, fr):
    """Horizontal strokes across columns c-half..c+half: (centre row, thickness)."""
    sub = mask[:, int(c - half):int(c + half) + 1]
    rows = sub.mean(axis=1) > frac
    rows[:int(fr["top"]) + 12] = False
    rows[int(fr["bottom"]) - 12:] = False
    return [((s + e - 1) / 2.0, e - s) for s, e in L.runs(rows)]


def read_stat(img, stat, categories, y_first_major, ystep):
    fr, cols, ay, by, my, dy = calibrate(img, y_first_major, ystep)
    if len(cols) != len(categories):
        raise ValueError(f"{len(cols)} category ticks, expected {len(categories)}")
    pitch = float(np.median(np.diff(cols)))
    red = L.hue_mask(img, "red", min_sat=60)
    blue = L.hue_mask(img, "blue", min_sat=40)
    black = L.neutral_dark(img, 110)
    out = []
    for c, (idx, name) in zip(cols, categories):
        if stat == "median":
            # the notch narrows the box at the median: the red line spans the notch's waist
            st = strokes(red, c, 0.12 * pitch, 0.8, fr)
            st = st[-1:] if st else []
        elif stat in ("q1", "q3"):
            st = strokes(blue, c, 0.12 * pitch, 0.8, fr)
            st = [st[-1]] if (st and stat == "q1") else ([st[0]] if st else [])
        else:
            st = strokes(black, c, 0.08 * pitch, 0.8, fr)
            st = [st[-1]] if (st and stat == "whisker_lo") else ([st[0]] if st else [])
        if not st:
            out.append({"x": float(idx), "y": None, "note": f"{name}: no {stat} stroke found"})
            continue
        r, th = st[0]
        y = (r - ay) / by
        e_px = th / 2.0 + my + 1.0
        e = e_px / abs(by)
        note = f"{name}: {stat} stroke at row {r:.1f}, {th} px thick" + ("" if out else f"; y axis {dy}")
        out.append({"x": float(idx), "y": float(y), "lo": float(y - e), "hi": float(y + e), "px": [float(c), r],
                    "px_lo": r - e_px, "px_hi": r + e_px, "note": note})
    return sorted(out, key=lambda d: d["x"])
