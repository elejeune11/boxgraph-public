"""Figure-specific calibration and reading for Figs. 2, 3, 4 and 6 of schwarz2020; the shared
machinery and the reading rules are in _sz.py.

Fig. 2A (p. 6, 800 dpi): histogram of segment length, 1 mm bins, log count axis.  x: the ticks
  down from the x axis, all of them, in order = 0, 1, ..., 22 mm (labels at the even ones).
  y: the long ticks left of the y axis = 1, 10, ..., 1,000,000 (log).  Fill: lavender (216, 216, 252).
Fig. 2B (p. 6, 800 dpi): horizontal box plots of segment length per diameter class.  x: the first
  seven ticks from the left = 0, 0.5, ..., 3 mm (the axis is broken after 3; the last tick is 6).  A
  whisker beyond the break (only >= 400 um) is not read.  Boxes from bottom to top = classes
  30-45 ... >= 400 um.  Fill: lavender.  Caption: whiskers are 1.5 IQR.
Fig. 3A (p. 7, 600 dpi): horizontal box plots of daughter symmetry per mother class.  x: all ticks in
  order = 0, 0.05, ..., 1 (labels every 0.1).  Fills: grey (228, 228, 228), yellow (252, 252, 216),
  blue (48, 132, 188).
Figs. 3B, 3C (p. 7, 800 dpi): histograms of daughter symmetry, bins 0.05 wide.  x: all ticks in order
  = 0, 0.1, ..., 1 (or 0, 0.05, ... when the half ticks are drawn: chosen by the count found).
  y: long ticks = 0, 0.02, ..., 0.14.  Fill: blue (48, 132, 188) in B, yellow (252, 252, 204) in C.
Fig. 4 (p. 8, 600 dpi): upright box plots of area growth, two panels: the left one (classes 30-45,
  45-60, 60-75 um) with its own axis 0 ... 60, the right one (75-90 ... >= 400 um) with 0 ... 3.  Each
  panel's y axis is the left end of its x axis line; long ticks = its printed labels.  The class of a
  box is the nearest class tick on the x axis (ticks down from the axis line, in order); light boxes
  (188, 216, 236) are daughter symmetry 0.5-1.0, dark ones (48, 132, 188) 0.0-0.5 (legend).
Fig. 6 (p. 10, 800 dpi): upright box plots of perfusion per region.  y long ticks = 0, 10, 20, 30.
  Fill: grey (240, 240, 240).  Boxes from left to right = LV epi, LV mid, LV endo, Sept LV, Sept mid,
  Sept RV, indexed 1 ... 6.
"""
import importlib.util
import os

import numpy as np

_s = importlib.util.spec_from_file_location("schwarz2020_sz", os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "_sz.py"))
S = importlib.util.module_from_spec(_s)
_s.loader.exec_module(S)

LAV = [(216, 216, 252), (220, 218, 252)]
CLASSES = ["30", "45", "60", "75", "90", "105", "120", "150", "200", "400"]


def _main_axes(k):
    xl = max(S.axis_rows(k, 400), key=lambda t: t[3] - t[2])
    yl = max(S.axis_cols(k, 400), key=lambda t: t[3] - t[2])
    return xl, yl  # (row0, row1, col0, col1), (col0, col1, row0, row1)


def _xticks(k, xl, yl):
    return S.ticks(S.depths_down(k, xl[1], yl[0] - 3, k.shape[1]))


def _yticks(k, xl, yl, long=True):
    return S.ticks(S.depths_left(k, yl[0], 0, xl[1] + 4), long=long)


# ---- Fig. 2A
def fig2a(image, at):
    k = S.ink_of(image)
    xl, yl = _main_axes(k)
    xt = _xticks(k, xl, yl)
    if len(xt) != 23:
        raise ValueError(f"Fig. 2A: {len(xt)} x ticks for 0..22")
    xa = S.Axis(xt, list(range(23)), what="x")
    yt = sorted(_yticks(k, xl, yl), reverse=True)
    if len(yt) != 7:
        raise ValueError(f"Fig. 2A: {len(yt)} long y ticks for 1..1e6")
    ya = S.Axis(yt, [10 ** i for i in range(7)], log=True, what="y (log)")
    return S.bars(image, LAV, xa, ya, xl[0], at)


# ---- box plots
def _emit_boxes(at, keys, bx, axis, stat, extra_note=""):
    chosen = {}
    for key, b in zip(keys, bx):
        chosen[key] = S.by_stat(b, axis)
    out = S.emit(at, chosen, stat, axis.note + extra_note)
    return out


def fig2b(image, at, stat):
    k = S.ink_of(image)
    xl, yl = _main_axes(k)
    xt = _xticks(k, xl, yl)[:7]
    ax = S.Axis(xt, [0, 0.5, 1, 1.5, 2, 2.5, 3], what="x")
    bx = S.boxes(image, LAV, ax, vertical=False, stop_rows=(yl[0], yl[1]))
    bx.sort(key=lambda b: -b["across"])  # bottom (30-45) first
    if len(bx) != 10:
        raise ValueError(f"Fig. 2B: {len(bx)} boxes")
    out = _emit_boxes(at, CLASSES, bx, ax, stat)
    lim = ax.pos(3.0)
    for r in out:
        if r.get("y") is not None and r["px"][0] > lim + 3:
            r.update({"y": None, "note": "beyond the axis break after 3 mm: no scale to read it on"})
            r.pop("lo", None), r.pop("hi", None), r.pop("px", None)
    return out


def fig3a(image, at, stat):
    k = S.ink_of(image)
    xl, yl = _main_axes(k)
    xt = _xticks(k, xl, yl)
    if len(xt) != 21:
        raise ValueError(f"Fig. 3A: {len(xt)} x ticks for 0..1 by 0.05")
    ax = S.Axis(xt, [round(0.05 * i, 2) for i in range(21)], what="x")
    bx = S.boxes(image, [(228, 228, 228), (252, 252, 216), (48, 132, 188)], ax, vertical=False,
                 stop_rows=(yl[0], yl[1]))
    bx = [b for b in bx if b["across"] < xl[0]]  # grey anti-aliasing of the axis title is not a box
    bx.sort(key=lambda b: -b["across"])
    if len(bx) != 10:
        raise ValueError(f"Fig. 3A: {len(bx)} boxes")
    return _emit_boxes(at, CLASSES, bx, ax, stat)


def fig3(image, at, color):
    k = S.ink_of(image)
    xl, yl = _main_axes(k)
    xt = _xticks(k, xl, yl)
    if len(xt) == 11:
        vals = [round(0.1 * i, 2) for i in range(11)]
    elif len(xt) == 21:
        vals = [round(0.05 * i, 2) for i in range(21)]
    else:
        raise ValueError(f"Fig. 3B/C: {len(xt)} x ticks")
    xa = S.Axis(xt, vals, what="x")
    yt = sorted(_yticks(k, xl, yl), reverse=True)
    if len(yt) != 8:
        raise ValueError(f"Fig. 3B/C: {len(yt)} long y ticks")
    ya = S.Axis(yt, [round(0.02 * i, 2) for i in range(8)], what="y")
    return S.bars(image, [color], xa, ya, xl[0], at)


def fig4(image, at, stat, group):
    k = S.ink_of(image)
    lines = sorted([t for t in S.axis_rows(k, 400) if t[0] > k.shape[0] * 0.3], key=lambda t: t[2])
    if len(lines) != 2:
        raise ValueError(f"Fig. 4: {len(lines)} x axis lines")
    out_boxes = {}
    notes = []
    color = (188, 216, 236) if group == "light" else (48, 132, 188)
    vert = S.axis_cols(k, 400)
    for (r0, r1, c0, c1), labels, keys in ((lines[0], [0, 10, 20, 30, 40, 50, 60], CLASSES[:3]),
                                         (lines[1], [0, 1, 2, 3], CLASSES[3:])):
        # the panel's y axis: the long vertical line standing on the x axis line near its left end
        # (the axis line runs on to the left as the tick of 0)
        ya = [v for v in vert if c0 <= v[0] <= c0 + 150 and v[3] >= r0 - 5]
        if len(ya) != 1:
            raise ValueError(f"Fig. 4: {len(ya)} y axis lines near column {c0}")
        c0 = ya[0][0]
        dep = S.depths_left(k, c0, 0, r1 + 4)
        yt = sorted(S.ticks(dep, long=True), reverse=True)
        if len(yt) != len(labels):
            raise ValueError(f"Fig. 4: {len(yt)} long y ticks for {labels}")
        ax = S.Axis(yt, labels, what=f"y (panel {labels[-1]})")
        notes.append(ax.note)
        xt = [t for t in S.ticks(S.depths_down(k, r1, c0 + 10, c1)) if c0 + 10 < t < c1]
        if len(xt) != len(keys):
            raise ValueError(f"Fig. 4: {len(xt)} class ticks for {keys}")
        sub = np.array(image)[:, c0 + 6:c1]
        bx = S.boxes(sub, [color], ax, vertical=True, stop_rows=(r0, r1), min_along=2)
        for b in bx:
            b["across"] += c0 + 6
            for st in b["stats"].values():
                if "px" in st:
                    st["px"][0] += c0 + 6
            j = int(np.argmin([abs(b["across"] - t) for t in xt]))
            out_boxes[keys[j]] = S.by_stat(b, ax)
    return S.emit(at, out_boxes, stat, "; ".join(notes))


REGIONS = ["1", "2", "3", "4", "5", "6"]


def fig6(image, at, stat):
    k = S.ink_of(image)
    xl, yl = _main_axes(k)
    yt = sorted(_yticks(k, xl, yl), reverse=True)
    if len(yt) != 4:
        raise ValueError(f"Fig. 6: {len(yt)} long y ticks")
    ax = S.Axis(yt, [0, 10, 20, 30], what="y")
    bx = S.boxes(image, [(240, 240, 240)], ax, vertical=True, stop_rows=(xl[0], xl[1]))
    # boxes stand right of the y axis and are wider than the solid parts of the label glyphs
    bx = [b for b in bx if b["c0"] > yl[1] and b["c1"] - b["c0"] > 100]
    bx.sort(key=lambda b: b["across"])
    if len(bx) != 6:
        raise ValueError(f"Fig. 6: {len(bx)} boxes")
    return _emit_boxes(at, REGIONS, bx, ax, stat)
