"""Fig. 2 B (PDF p. 3), + BLEB: mean traction stress (green dots, left axis) and F-actin speed
(blue line, right axis) against distance from the leading cell edge.

Calibration from the image: the frame; x from the black ticks on the bottom edge, one every
label step (the labels 12, 8, 4, 0 sit under every other tick: 12 under the leftmost tick, 0 at
the right frame edge, which lies on the tick grid); y from the green ticks on the left edge
(left axis labels 10, 20, 30; 30 at the top frame edge, 0 at the bottom edge, both on the grid).
The blue ticks of the right axis (labels 10, 20) lie on the same rows as the green 10 and 20:
both axes have the same scale; the code checks this.
Green dots: green blobs separated by erosion (_dots.find_markers). Blue line: it has a vertex
(a small star marker) at every green dot's distance; the speed is read at those columns as the
centre of the blue line's run, with the line's half-thickness in the interval.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("gardel_dots", Path(__file__).with_name("_dots.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
L = D.L


def calibrate(img):
    fr = L.frame(img)
    nonwhite = L.gray(img) < 200
    tx = L.ticks(img, fr["bottom"], (fr["left"] + 15, fr["right"] - 15), "x", -1, 80, lw=fr["lw_row"])
    ty = L.ticks(img, fr["left"], (fr["top"] + 15, fr["bottom"] - 15), "y", 1, 80, lw=fr["lw_col"],
                 mask=nonwhite & L.hue_mask(img, "green", min_sat=40, max_gray=245))
    tyr = L.ticks(img, fr["right"], (fr["top"] + 15, fr["bottom"] - 15), "y", -1, 80, lw=fr["lw_col"],
                  mask=nonwhite & L.hue_mask(img, "blue", min_sat=40, max_gray=245))
    # x: values grow leftward from the right edge (0); the leftmost tick is labelled 12
    ax, bx, mx, dx = L.grid_axis(tx, fr["right"], fr["left"], 0.0, (None, 1), 2.0, all_major=True)
    ay, by, my, dy = L.grid_axis(ty, fr["bottom"], fr["top"], 0.0, 30.0, 10.0, all_major=True)
    ar, br, mr, dr = L.grid_axis(tyr, fr["bottom"], fr["top"], 0.0, (None, 1), 10.0, all_major=True)
    same = abs(ar - ay) < 4 and abs(br - by) / abs(by) < 0.01
    if not same:
        raise ValueError("the right axis does not share the left axis's scale")
    return fr, (ax, bx, mx, dx), (ay, by, my, dy)


def green_dots(img, fr):
    mask = L.hue_mask(img, "green", min_sat=60)
    mk, R, single = D.find_markers(mask, fr, 12, margin=4)
    return mk, R


def read_stress(img):
    fr, (ax, bx, mx, dx), (ay, by, my, dy) = calibrate(img)
    mk, R = green_dots(img, fr)
    out = []
    for p in sorted(mk, key=lambda d: d["c"]):
        pr = 1.5 + (4 if p["blob_markers"] > 1 else 0) + (R / 2 if p["split"] else 0)
        y = (p["r"] - ay) / by
        e = (pr + my) / abs(by)
        note = f"green dot centre (R = {R:.1f} px)" + ("" if out else f"; x axis {dx}; y axis {dy}")
        if p["blob_markers"] > 1:
            note += f"; one of {p['blob_markers']} overlapping dots"
        out.append({"x": float((p["c"] - ax) / bx), "y": float(y), "lo": float(y - e), "hi": float(y + e),
                    "px": [p["c"], p["r"]], "note": note})
    return sorted(out, key=lambda d: d["x"])


def read_speed(img):
    fr, (ax, bx, mx, dx), (ay, by, my, dy) = calibrate(img)
    mk, R = green_dots(img, fr)
    blue = L.hue_mask(img, "blue", min_sat=60)
    blue[:int(fr["top"]) + 10] = False
    blue[int(fr["bottom"]) - 10:] = False
    out = []
    for p in sorted(mk, key=lambda d: d["c"]):
        c = int(round(p["c"]))
        col = blue[:, max(0, c - 1):c + 2].any(axis=1)
        rr = L.runs(col)
        if not rr:
            out.append({"x": float((p["c"] - ax) / bx), "y": None, "note": "no blue line in this column"})
            continue
        s, e = max(rr, key=lambda t: t[1] - t[0])
        r = (s + e - 1) / 2.0
        half = (e - s) / 2.0
        y = (r - ay) / by
        err = (half + 1.0 + my) / abs(by)
        note = f"blue line at the green dot's column, run {e - s} px" + ("" if out else f"; x axis {dx}; y axis {dy}")
        out.append({"x": float((p["c"] - ax) / bx), "y": float(y), "lo": float(y - err), "hi": float(y + err),
                    "px": [float(c), r], "px_lo": r - half - 1, "px_hi": r + half + 1, "note": note})
    return sorted(out, key=lambda d: d["x"])
