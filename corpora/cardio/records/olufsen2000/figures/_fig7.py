"""Fig. 7 (PDF p. 13): measured (dashed, 'meas') and simulated (solid, 'sim') flow at nine sites.
Calibration is the shared one of _common.py (frame, inward ticks, linear fit of the matched labels).
Labels matched in every panel: x ticks 3.4, 3.6, 3.8, 4, 4.2 s; the y labels are passed by each panel.

Separating the two black curves, from the image alone:

- Length scale t: 0.5% of the plot width (about 9 px at 1000 dpi, of the order of the line width;
  the nine panels are drawn alike). The legend box is masked (found as in _common.py, or with looser
  tolerances by _legend_loose when that misses it).
- Solid line: in each column, the dark runs that can be followed column by column for H = 6 t columns
  to at least one side (so the line is found up to its ends). A dash is about 2-3 t long and the gaps between dashes about t, so a dash never
  follows that far on its own; a dash that touches the solid line is taken in with it.
- Dashes: what is dark once the solid line (dilated by 2 px) is removed, as connected components
  whose area is at least 2.5 t^2 (grid dots and the '+' marks of the grid are smaller) and whose
  extent is at most 8 t both ways (the curves and the legend are larger; the legend is masked anyway).

Reading the solid line ('sim'): exactly one solid run in the column; its centre is the value and its
extent (widened by the x misfit, 2 px and the y misfit) the interval. Where a dash touches the solid
line the run includes it, so the interval is wider there.

Reading the dashed line ('meas'): if one dash covers the column, its centre there is the value and
its extent the interval. In a gap between two dashes (both ends within 2.5 t columns), the value is
interpolated linearly between the facing ends and the interval spans both end runs. Otherwise (the
dashed curve hidden under the solid line, or two dashes in the column) the position is not read.
"""
import importlib.util
import os

import numpy as np
from scipy import ndimage as nd

_spec = importlib.util.spec_from_file_location(
    "_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)

X_TICKS = [3.4, 3.6, 3.8, 4.0, 4.2]


def _legend_loose(cal):
    """The legend box when _common.legend_box misses it: in the upper right quarter of the plot, the
    two longest horizontal dark runs (> 15% of the plot width) whose ends agree within 10 px."""
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    dark = g < _c.ink_threshold(cal)
    w, h = right - left, bot - top
    cands = []
    for r in range(top + 6, top + h // 2):
        for a, b in _c._hruns(dark[r, left + w // 2:right - 6]):
            if b - a > 0.15 * w:
                cands.append((r, a + left + w // 2, b + left + w // 2))
    best = None
    for i, (r0, a0, b0) in enumerate(cands):
        for r1, a1, b1 in cands[i + 1:]:
            if r1 - r0 >= 0.08 * h and abs(a1 - a0) <= 10 and abs(b1 - b0) <= 10:
                if best is None or r1 - r0 > best[3] - best[1]:
                    best = (min(a0, a1), r0, max(b0, b1), r1)
    return best


def _prepare(image, y_frame, y_ticks, x_ticks=None):
    cal = _c.calibrate(image, (None, None), x_ticks or X_TICKS, y_frame, y_ticks)
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    dark = g < _c.ink_threshold(cal)
    inner = np.zeros_like(dark)
    m = max(6, int(0.006 * (bot - top)))
    inner[top + m:bot - m, left + m:right - m] = True
    dark &= inner
    leg = cal["legend"] or _legend_loose(cal)
    cal["legend"] = leg
    if leg is not None:
        c0, r0, c1, r1 = leg
        dark[max(r0 - 8, 0):r1 + 9, max(c0 - 8, 0):c1 + 9] = False
    runs = {}
    for c in range(left, right + 1):
        idx = list(np.where(dark[:, c])[0])
        runs[c] = [(grp[0], grp[-1]) for grp in _c.groups(idx, gap=1)]
    # length scale: all nine panels are drawn alike, and 0.5% of the plot width (about 9 px at
    # 1000 dpi) is of the order of the line width
    t = 0.005 * (right - left)
    H = int(round(6 * t))

    def follows(run, c0, step):
        r0, r1 = run
        for cc in range(c0 + step, c0 + step * (H + 1), step):
            nxt = [(a, b) for a, b in runs.get(cc, []) if a <= r1 + 1 and b >= r0 - 1]
            if not nxt:
                return False
            r0, r1 = min(a for a, _ in nxt), max(b for _, b in nxt)
        return True

    solid = {}
    smask = np.zeros_like(dark)
    for c in range(left, right + 1):
        # to one side suffices, so the last H columns before a curve end are still solid
        solid[c] = [rn for rn in runs[c] if follows(rn, c, +1) or follows(rn, c, -1)]
        for a, b in solid[c]:
            smask[a:b + 1, c] = True
    smask = nd.binary_dilation(smask, iterations=2)
    rest = dark & ~smask
    lab, n = nd.label(rest, structure=np.ones((3, 3)))
    keep = np.zeros(n + 1, bool)
    for i, sl in enumerate(nd.find_objects(lab), start=1):
        area = int((lab[sl] == i).sum())
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        keep[i] = area >= 2.5 * t * t and h <= 8 * t and w <= 8 * t
    dlab = np.where(keep[lab], lab, 0)
    cal.update(runs=runs, solid=solid, dlab=dlab, t=t, H=H)
    return cal


def _interval(cal, x, c, r0, r1, rc, what):
    pad = 2 + cal["ymis"]
    ya, yb = cal["val_of"](r0 - pad), cal["val_of"](r1 + pad)
    return {"x": x, "y": cal["val_of"](rc), "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, rc],
            "px_lo": r0 - pad, "px_hi": r1 + pad,
            "note": f"{what}; t {cal['t']:.0f} px; misfit x {cal['xmis']:.1f} px, y {cal['ymis']:.1f} px"}


def read_sim(image, at, y_frame, y_ticks, x_ticks=None):
    """The solid line; x_ticks defaults to the Fig. 7 labels (Fig. 5 passes its own)."""
    cal = _prepare(image, y_frame, y_ticks, x_ticks)
    out = []
    for x in at:
        c = int(round(cal["col_of"](x)))
        rr = cal["solid"].get(c, [])
        if len(rr) != 1:
            out.append({"x": x, "y": None, "note": f"{len(rr)} solid runs in column {c}"})
            continue
        r0, r1 = rr[0]
        rc = 0.5 * (r0 + r1)
        cm = int(np.ceil(cal["xmis"]))
        for cc in (c - cm, c + cm):
            for a, b in cal["solid"].get(cc, []):
                if a <= r1 + 1 and b >= r0 - 1:
                    r0, r1 = min(r0, a), max(r1, b)
        out.append(_interval(cal, x, c, r0, r1, rc, f"solid rows {r0}-{r1}"))
    return out


def _dash_runs(dlab, c):
    col = dlab[:, c]
    labs = sorted(set(col[col > 0].tolist()))
    res = []
    for k in labs:
        rows = np.where(col == k)[0]
        res.append((k, int(rows.min()), int(rows.max())))
    return res


def read_meas(image, at, y_frame, y_ticks):
    cal = _prepare(image, y_frame, y_ticks)
    dlab, t = cal["dlab"], cal["t"]
    G = int(round(2.5 * t))
    cm = int(np.ceil(cal["xmis"]))
    out = []
    for x in at:
        c = int(round(cal["col_of"](x)))
        here = _dash_runs(dlab, c)
        if len(here) > 1 and all(here[i + 1][1] - here[i][2] <= G for i in range(len(here) - 1)):
            # consecutive dashes of a steep stretch stacked in one column: one run spanning them
            a, b = here[0][1], here[-1][2]
            out.append(_interval(cal, x, c, a, b, 0.5 * (a + b),
                                 f"{len(here)} stacked dashes rows {a}-{b} (steep stretch)"))
            continue
        if len(here) == 1:
            k, r0, r1 = here[0]
            rc = 0.5 * (r0 + r1)
            for cc in (c - cm, c + cm):
                for kk, a, b in _dash_runs(dlab, cc):
                    if kk == k:
                        r0, r1 = min(r0, a), max(r1, b)
            out.append(_interval(cal, x, c, r0, r1, rc, f"dash {k} rows {r0}-{r1}"))
            continue
        if len(here) > 1:
            out.append({"x": x, "y": None, "note": f"{len(here)} dashes in column {c}"})
            continue
        left = right = None
        for d in range(1, G + 1):
            if left is None and _dash_runs(dlab, c - d):
                left = (c - d, _dash_runs(dlab, c - d))
            if right is None and _dash_runs(dlab, c + d):
                right = (c + d, _dash_runs(dlab, c + d))
        if left is None or right is None or len(left[1]) != 1 or len(right[1]) != 1:
            out.append({"x": x, "y": None,
                        "note": f"no dash within {G} columns on both sides of column {c} (dashed curve hidden)"})
            continue
        (cl, [(kl, al, bl)]), (cr, [(kr, ar, br)]) = left, right
        ml, mr = 0.5 * (al + bl), 0.5 * (ar + br)
        rc = ml + (mr - ml) * (c - cl) / (cr - cl)
        out.append(_interval(cal, x, c, min(al, ar), max(bl, br), rc,
                             f"gap between dashes {kl} (col {cl}) and {kr} (col {cr})"))
    return out
