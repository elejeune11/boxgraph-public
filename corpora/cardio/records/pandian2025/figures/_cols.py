"""Shared reading code for the column plots of pandian2025 (Figs. 3e, 3f, 3h, 3i, 4b, 4c, 4f, 4g): one column of
grey dots (a beeswarm) or a grey violin per category, with a black horizontal central line (solid or dashed),
sometimes grey whiskers with caps, and in Figs. 4b-c three large black dots per group (one per network).
The captions do not say what the central line, the whiskers or the black dots are (see figures.md): the
whiskers reach the outermost dots (a range), the central line is the paper's summary (median or mean,
unstated).

All are raster images, read at 1200-1500 dpi.

Calibration (_axes.py): within `box` (columns, rows of the crop holding the frame) the y axis line is the
darkest column and the x axis line the darkest row. Major y ticks are dark runs at least `ytick` px long to
the left of the y axis, matched in order (top to bottom) to the printed labels; on a log axis the labels are
the printed exponents and a value is 10**(reading). Categories are the x ticks (dark runs at least `xtick` px
below the x axis, more than 25 px right of the y axis), numbered 1, 2, ... from the left. The largest misfit
of the y fit widens every interval.

Central line: black pixels (grey < `black`) that belong to a vertical black run no longer than 30 px (this
drops the large black dots and the axis text). In the window of +/- `wfrac` x the category spacing around
the category centre, rows where such pixels cover at least `cover` of the window are line rows; rows above
`ymax` (a significance bar) are ignored; consecutive rows are grouped and the group with the largest mean
cover is the line. Value: the group's centre; interval +/- (half its height + 2 px + misfit).

Whisker caps (`caps=True`): rows where pixels of grey 90-215 cover at least 70 % of +/- `capfrac` x spacing
around the centre; the topmost and bottommost such row groups are the caps. Each end is the centre of its
group; the outer interval adds half the group height + 2 px + misfit.

Black dots (`dots`): pixels darker than 90 whose distance to the nearest lighter pixel exceeds `dot_core`
px, within +/- 0.45 x spacing of the centre; each local maximum is a dot centre; interval +/- (3 px +
misfit).
"""

import numpy as np
from scipy import ndimage as ndi
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_axes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def calibrate(image, box, labels, log, ytick=20, xtick=20):
    g = A.gray(image)
    ya, xa = A.frame(g, box)
    ty = A.ticks_left(g, ya, (box[2], xa[1] + 5), ytick)
    a, b, mis = A.fit(ty, labels)
    tx = [t for t in A.ticks_down(g, xa, (ya[0] - 5, box[1]), xtick) if t > ya[1] + 25]
    sp = float(np.median(np.diff(tx))) if len(tx) > 1 else 300.0
    return dict(g=g, a=a, b=b, mis=mis, log=log, ya=ya, xa=xa, cols=tx, sp=sp, ticks=ty)


def val(cal, row):
    v = cal["a"] + cal["b"] * row
    return 10 ** v if cal["log"] else v


def row_of(cal, value):
    v = np.log10(value) if cal["log"] else value
    return (v - cal["a"]) / cal["b"]


def vrun(mask):
    """Length of the vertical run each True pixel belongs to."""
    out = np.zeros(mask.shape, int)
    for c in range(mask.shape[1]):
        for s, e in A.runs(mask[:, c]):
            out[s:e, c] = e - s
    return out


def line_groups(cal, k, wfrac=0.3, cover=0.3, black=90, ymax=None):
    """Every horizontal line in the category's window: (row, tolerance, mean cover), top to bottom."""
    g = cal["g"]
    c = cal["cols"][k - 1]
    w = int(wfrac * cal["sp"])
    c0, c1 = int(c - w), int(c + w)
    r_top = int(row_of(cal, ymax)) if ymax is not None else int(min(cal["ticks"])) - 5
    r_bot = cal["xa"][0] - 3
    sub = g[r_top:r_bot, c0:c1] < black
    thin = sub & (vrun(sub) <= 30)
    frac = thin.mean(axis=1)
    return [(r_top + (s + e - 1) / 2.0, (e - s) / 2.0 + 2 + cal["mis"], float(frac[s:e].mean()))
            for s, e in A.runs(frac >= cover)]


def central_line(cal, k, wfrac=0.3, cover=0.3, black=90, ymax=None):
    groups = line_groups(cal, k, wfrac, cover, black, ymax)
    return max(groups, key=lambda g: g[2]) if groups else None


def caps(cal, k, capfrac=0.13):
    g = cal["g"]
    c = cal["cols"][k - 1]
    w = int(capfrac * cal["sp"])
    r_top = int(min(cal["ticks"])) - 5
    r_bot = cal["xa"][0] - 8  # clear of the anti-aliased edge of the x axis line
    sub = g[r_top:r_bot, int(c - w): int(c + w)]
    hit = ((sub >= 90) & (sub <= 215)).mean(axis=1) >= 0.7
    groups = A.runs(hit)
    if len(groups) < 2:
        return None
    (s1, e1), (s2, e2) = groups[0], groups[-1]
    top = (r_top + (s1 + e1 - 1) / 2.0, (e1 - s1) / 2.0 + 2 + cal["mis"])
    bot = (r_top + (s2 + e2 - 1) / 2.0, (e2 - s2) / 2.0 + 2 + cal["mis"])
    return top, bot


def read_column(image, at, cal, wfrac=0.3, cover=0.3, with_caps=False, capfrac=0.13, ymax=None, what="central line"):
    out = []
    for x in at:
        k = int(round(x))
        c = cal["cols"][k - 1]
        cl = central_line(cal, k, wfrac=wfrac, cover=cover, ymax=ymax)
        if cl is None:
            out.append({"x": x, "y": None, "note": f"category {k}: no {what} found"})
            continue
        r, tol, fr = cl
        rec = {"x": x, "y": val(cal, r), "px": [float(c), r],
               "note": f"category {k}: {what} at row {r:.1f} (cover {fr:.2f}); "
                       f"{len(cal['ticks'])} y ticks, misfit {cal['mis']:.2f} px"}
        lo, hi = sorted((val(cal, r + tol), val(cal, r - tol)))
        rec["lo"], rec["hi"] = lo, hi
        if with_caps:
            cp = caps(cal, k, capfrac)
            if cp is None:
                rec["note"] += "; no whisker caps found"
            else:
                (rt, tt), (rb, tb) = cp
                rec["bar_hi"], rec["bar_lo"] = val(cal, rt), val(cal, rb)
                rec["bar_hi_outer"], rec["bar_lo_outer"] = val(cal, rt - tt), val(cal, rb + tb)
                rec["px_lo"], rec["px_hi"] = rb, rt
                rec["note"] += f"; whisker caps at rows {rt:.1f} and {rb:.1f}"
        out.append(rec)
    return out


def read_dots(image, cal, groups, dot_core=12, ymax=None):
    """Black filled dots around each listed category; x = category + small offset by column order."""
    g = cal["g"]
    m = g < 90
    r_top = int(row_of(cal, ymax)) if ymax is not None else 0
    m[:r_top, :] = False
    m[cal["xa"][0] - 3:, :] = False
    m[:, : cal["ya"][1] + 3] = False
    dt = ndi.distance_transform_edt(m)
    out = []
    for k in groups:
        c = cal["cols"][k - 1]
        w = 0.45 * cal["sp"]
        pk = [(r, cc) for r, cc in A.peaks(dt, dot_core, 2 * dot_core) if abs(cc - c) <= w]
        pk.sort(key=lambda rc: rc[1])
        for i, (r, cc) in enumerate(pk):
            tol = 3 + cal["mis"]
            lo, hi = sorted((val(cal, r + tol), val(cal, r - tol)))
            out.append({"x": round(k + (i + 1) / 10.0, 2), "y": val(cal, r), "lo": lo, "hi": hi,
                        "px": [float(cc), float(r)], "px_lo": r + tol, "px_hi": r - tol,
                        "note": f"category {k}, dot {i + 1} of {len(pk)} from the left (radius {dt[r, cc]:.0f} px); "
                                f"x is the category plus 0.1 x the dot's order"})
    return out
