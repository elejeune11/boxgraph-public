"""Shared code for reading coloured curves (lines) in the plots of sexton2025.

Calibration (`axes`): the y axis is the long vertical dark line at a given rank from the left among the
long vertical lines found (some panels have a colour bar beside it); the x axis is the lowest long
horizontal dark line. Ticks are short dark runs leaving the axis line on the given side; on a log axis
only the long (labelled, decade) ticks are kept by requiring a minimum run length. Tick centres are
matched in order to the printed labels the caller passes, a line is fitted (in log10 for a log axis),
and the largest misfit in pixels widens every interval.

Curves (`read_traced`): a colour mask (within `tol` of the curve's colour) is traced column by column
from a seed found in the image: the run in the seed column chosen by `pick` ('lowest', 'highest', or a
row fraction of the plot). The trace follows the run nearest the curve's recent slope and stops at gaps
over `max_gap` columns. A reading at x is the trace's centre in that column; its interval is half the
run height + 0.5 px + slope times the x misfit + the y misfit. A column the trace did not reach is
returned without a value. Columns where the run is much thicker than the line (a crossing, a merged
marker or an overlapping drawing) are flagged and their interval covers the whole run.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from boxgraph import digitize as D  # noqa: E402


def axes(image, ylabels, xlabels, yscale="linear", xscale="linear", dark=160, yrank=0, frac=0.45,
         ylen=12, ymin=None, xlen=12, xmin=None, yside="out", xside="out", ycols=None, xrow_rank=-1):
    rows, cols = C.frame(image, dark, frac)
    if ycols is not None:
        cols = [c for c in cols if ycols[0] <= c[0] <= ycols[1]]
    yc = cols[yrank]
    xr = rows[xrow_rank]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], yside, ylen, 0, xr[2] + 20, dark, ymin)]
    if len(yt) == len(ylabels) + 1 and ylabels[-1] == 0 and abs(yt[-1] - xr[0]) < 6:
        # one unlabelled tick above the highest label (S2E): the labels are matched from the x axis up
        yt = yt[1:]
    if len(yt) != len(ylabels):  # a drawing touching the axis adds marks: keep the evenly spaced set
        yt = D.regular_ticks(yt, tol=3.0)
    if len(yt) != len(ylabels):
        raise RuntimeError(f"expected {len(ylabels)} y ticks, found {yt}")
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], xside, xlen, yc[1] - 3, image.shape[1], dark, xmin)]
    if len(xt) == len(xlabels) + 1 and abs(xt[0] - yc[0]) < 6:  # the first label's tick is the y axis itself
        xt = xt[1:]
    if len(xt) != len(xlabels):
        xt = D.regular_ticks(xt, tol=3.0)
    if len(xt) != len(xlabels):
        raise RuntimeError(f"expected {len(xlabels)} x ticks, found {xt}")
    ax_y = C.Axis(yt, ylabels, yscale)
    ax_x = C.Axis(xt, xlabels, xscale)
    box = (yc[2] + 1, 0, image.shape[1], xr[1])
    return ax_x, ax_y, box


def mask_of(image, rgb, tol, box):
    m = C.hue_mask(image, rgb, tol)
    c0, r0, c1, r1 = box
    out = np.zeros_like(m)
    out[r0 + 2: r1 - 2, c0 + 2: c1 - 2] = m[r0 + 2: r1 - 2, c0 + 2: c1 - 2]
    return out


def _dark_run(gray, col, start, step, dark=90, limit=15):
    """Rows of near-black ink directly next to a curve's run (within 2 px of it), up to `limit`."""
    H = gray.shape[0]
    r, n, seen = start, 0, False
    for k in range(limit + 2):
        if not (0 <= r < H):
            break
        if gray[r, col] < dark:
            n += 1
            seen = True
        elif seen or k >= 2:
            break
        r += step
    return n


def read_traced(image, at, ax_x, ax_y, box, rgb, tol, seed_x, pick="lowest", max_gap=12, ylimit=None):
    m = mask_of(image, rgb, tol, box)
    sc = int(round(ax_x.pix(seed_x)))
    runs = []
    for dc in (0, 1, -1, 2, -2, 3, -3, 5, -5, 8, -8):
        runs = C.column_runs(m, sc + dc)
        if runs:
            sc += dc
            break
    if not runs:
        return [{"x": float(x), "y": None, "note": f"no curve pixels at the seed x = {seed_x}"} for x in at]
    if pick == "lowest":
        s, e = max(runs, key=lambda t: t[0])
    elif pick == "highest":
        s, e = min(runs, key=lambda t: t[0])
    else:
        target = box[1] + float(pick) * (box[3] - box[1])
        s, e = min(runs, key=lambda t: abs((t[0] + t[1]) / 2 - target))
    path = D.trace(m, (sc + 0.5, (s + e) / 2.0), max_gap=max_gap)
    gray = C.gray(image)
    halves = [h for (_, h, amb) in path.values() if not amb]
    typical = float(np.median(halves)) if halves else 3.0
    out = []
    for xv in at:
        x = float(xv)
        pc = ax_x.pix(x)
        col = int(np.floor(pc))
        got = None
        for dc in (0, 1, -1, 2, -2):
            if col + dc in path:
                got = col + dc
                break
        if got is None:
            out.append({"x": x, "y": None, "note": "the trace of this curve does not reach this x (gap, occlusion or the curve's end)"})
            continue
        centre, half, amb = path[got]
        prev, nxt = path.get(got - 2), path.get(got + 2)
        slope = abs(nxt[0] - prev[0]) / 4.0 if prev and nxt else 0.0
        note = ""
        if amb or half > 2.5 * typical + 2:
            note = "the run here is much thicker than the line (a crossing or an overlapping drawing): the interval covers it"
        h = half + 0.5 + slope * (abs(pc - (got + 0.5)) + ax_x.misfit) + ax_y.misfit
        # a dark line (the plot frame, an axis) drawn over the curve hides part of it: widen that side
        up_hide = _dark_run(gray, got, int(centre - half) - 1, -1)
        dn_hide = _dark_run(gray, got, int(centre + half) + 1, +1)
        if up_hide or dn_hide:
            note = (note + "; " if note else "") + "partly hidden under a dark line: the interval extends under it"
        lo, hi = sorted((ax_y.val(centre - h - up_hide), ax_y.val(centre + h + dn_hide)))
        out.append({"x": x, "y": ax_y.val(centre), "lo": lo, "hi": hi, "px": [pc, centre],
                    "px_lo": centre + h, "px_hi": centre - h, "note": note or f"misfits x {ax_x.misfit:.2f}, y {ax_y.misfit:.2f} px"})
    return out
