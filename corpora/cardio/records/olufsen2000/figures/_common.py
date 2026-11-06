"""Shared figure-reading code for olufsen2000 (Figs. 3, 6, 8, B5: MATLAB line plots with a box frame,
inward ticks and dotted grid lines). Everything is found in the image; each reader passes only the
printed tick labels it matched.

Calibration: the frame is the pair of longest dark rows and columns. Ticks are short dark runs that
start at the inner edge of the bottom (x) and left (y) frame lines; dotted grid lines continue from
them but break up. A linear fit of the matched labels to the tick pixels gives the axis; its worst
misfit is added to every interval.

Legend: a box drawn inside the frame, found as two long horizontal dark runs with the same ends;
everything inside it (and a margin) is ignored.

Solid line: in the column of each x, the dark runs that can be followed column by column for a few
columns to both sides (a solid line; dots of grid lines and letters break up). Exactly one such run
must remain; its centre is the value and its extent, widened by the misfit and 2 px, the interval.
"""
import numpy as np


def gray(image):
    return image[..., :3].astype(float).mean(axis=2)


def groups(idx, gap=2):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def frame(g):
    h, w = g.shape
    dark = g < 0.5 * (np.median(g) + np.percentile(g, 0.5))
    rows, cols = dark.sum(1), dark.sum(0)
    rr = np.where(rows > 0.6 * rows.max())[0]
    cc = np.where(cols > 0.6 * cols.max())[0]
    top = int(rr[rr < h / 2].max())
    bot = int(rr[rr >= h / 2].min())
    left = int(cc[cc < w / 2].max())
    right = int(cc[cc >= w / 2].min())
    return top, bot, left, right, dark


def _tick_runs(lengths, lo, hi):
    ticks = []
    for grp in groups(list(np.where(lengths > lo)[0])):
        if lengths[grp].max() > hi:
            continue
        ticks.append(float(np.mean(grp)))
    return ticks


def ticks_bottom(dark, top, bot, left, right):
    h = bot - top
    lengths = np.zeros(right - left - 5, int)
    for i, c in enumerate(range(left + 3, right - 2)):
        r = bot - 1
        while r > top and dark[r, c]:
            lengths[i] += 1
            r -= 1
    return [left + 3 + t for t in _tick_runs(lengths, 0.006 * h, 0.2 * h)]


def ticks_left(dark, top, bot, left, right):
    w = right - left
    lengths = np.zeros(bot - top - 5, int)
    for i, r in enumerate(range(top + 3, bot - 2)):
        c = left + 1
        while c < right and dark[r, c]:
            lengths[i] += 1
            c += 1
    return [top + 3 + t for t in _tick_runs(lengths, 0.004 * w, 0.1 * w)]


def _fit(pix, vals):
    pix, vals = np.asarray(pix, float), np.asarray(vals, float)
    a, b = np.polyfit(vals, pix, 1)  # pixel = a * value + b
    return a, b, float(np.abs(a * vals + b - pix).max())


def _match(found, vals, what):
    """The detected ticks that carry the labels `vals`, in order: when more short runs were found
    (the curve touching the frame also makes one), the ordered subset whose linear fit to the labels
    misfits least, which must be under 1.5% of the tick span."""
    import itertools

    found, n = sorted(found), len(vals)
    if len(found) < n:
        raise ValueError(f"expected {n} {what} ticks, found {len(found)} at {[round(f) for f in found]}")
    best = None
    for sub in itertools.combinations(found, n):
        mis = _fit(sub, vals)[2]
        if best is None or mis < best[0]:
            best = (mis, list(sub))
    if best[0] > 0.015 * (best[1][-1] - best[1][0]):
        raise ValueError(f"no regular {what} ticks among {[round(f) for f in found]} (misfit {best[0]:.1f} px)")
    return best[1]


def calibrate(image, x_frame, x_ticks, y_frame, y_ticks):
    """x_frame: (value at the left frame or None, value at the right frame or None); x_ticks: values of
    the interior bottom ticks, left to right. y_frame: (value at the top frame or None, at the bottom
    frame or None); y_ticks: values of the interior left ticks, top to bottom."""
    g = gray(image)
    top, bot, left, right, dark = frame(g)
    xp = _match(ticks_bottom(dark, top, bot, left, right), list(x_ticks), "x")
    yp = _match(ticks_left(dark, top, bot, left, right), list(y_ticks), "y")
    xv, yv = list(x_ticks), list(y_ticks)
    for edge, v in zip((left, right), x_frame):
        if v is not None:
            xp.append(edge)
            xv.append(v)
    for edge, v in zip((top, bot), y_frame):
        if v is not None:
            yp.append(edge)
            yv.append(v)
    ax, bx, xmis = _fit(xp, xv)
    ay, by, ymis = _fit(yp, yv)
    cal = dict(top=top, bot=bot, left=left, right=right, gray=g, xmis=xmis, ymis=ymis,
               col_of=lambda x: ax * x + bx, x_of=lambda c: (c - bx) / ax, val_of=lambda r: (r - by) / ay,
               slope_x=ax)
    cal["legend"] = legend_box(cal)
    return cal


def ink_threshold(cal, frac=0.35):
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    paper = float(np.median(g))
    ink = float(np.percentile(g[top:bot, left:right], 0.2))
    return ink + frac * (paper - ink)


def _hruns(row, gap=1):
    idx = np.where(row)[0]
    return [(grp[0], grp[-1]) for grp in groups(list(idx), gap=gap)]


def legend_box(cal):
    """The legend: two long horizontal dark runs inside the frame with the same ends (within 3 px),
    4-30% of the plot height apart. Returns (c0, r0, c1, r1) or None."""
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    dark = g < ink_threshold(cal)
    w, h = right - left, bot - top
    m = 6
    cands = []
    for r in range(top + m, bot - m):
        for a, b in _hruns(dark[r, left + m:right - m]):
            if b - a > 0.12 * w:
                cands.append((r, a + left + m, b + left + m))
    best = None
    for i, (r0, a0, b0) in enumerate(cands):
        for r1, a1, b1 in cands[i + 1:]:
            if 0.04 * h <= r1 - r0 <= 0.3 * h and abs(a1 - a0) <= 3 and abs(b1 - b0) <= 3:
                # both vertical sides must be dark
                sides = [dark[r0:r1 + 1, c].mean() for c in (min(a0, a1), max(b0, b1))]
                if min(sides) > 0.9 and (best is None or r1 - r0 > best[3] - best[1]):
                    best = (min(a0, a1), r0, max(b0, b1), r1)
    return best


def read_solid(cal, at, half_frac=0.004):
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    dark = g < ink_threshold(cal)
    leg = cal["legend"]
    if leg is not None:
        c0, r0, c1, r1 = leg
        dark[max(r0 - 6, 0):r1 + 7, max(c0 - 6, 0):c1 + 7] = False
    half = max(3, int(half_frac * (right - left)))
    margin = max(4, int(0.006 * (bot - top)))

    def col_runs(cc):
        return [(grp[0] + top + margin, grp[-1] + top + margin)
                for grp in groups(list(np.where(dark[top + margin:bot - margin, cc])[0]), gap=1)]

    def traces(run, c0, step):
        r0, r1 = run
        for cc in range(c0 + step, c0 + step * (half + 1), step):
            nxt = [(a, b) for a, b in col_runs(cc) if a <= r1 + 1 and b >= r0 - 1]
            if not nxt:
                return False
            r0, r1 = min(a for a, _ in nxt), max(b for _, b in nxt)
        return True

    out = []
    for x in at:
        c = int(round(cal["col_of"](x)))
        if c - half <= left + margin or c + half >= right - margin:
            out.append({"x": x, "y": None, "note": "too close to the frame"})
            continue
        runs = col_runs(c)
        solid = [run for run in runs if traces(run, c, +1) and traces(run, c, -1)]
        if len(solid) != 1:
            out.append({"x": x, "y": None, "note": f"{len(solid)} solid dark runs in column {c} (dark runs {runs})"})
            continue
        r0, r1 = solid[0]
        rc = 0.5 * (r0 + r1)
        # x misfit: the column may be off by xmis px; widen by the rows the line covers over that span
        cm = int(np.ceil(cal["xmis"]))
        for cc in (c - cm, c + cm):
            for a, b in col_runs(cc):
                if a <= r1 + 1 and b >= r0 - 1:
                    r0, r1 = min(r0, a), max(r1, b)
        pad = 2 + cal["ymis"]
        ya, yb = cal["val_of"](r0 - pad), cal["val_of"](r1 + pad)
        out.append({"x": x, "y": cal["val_of"](rc), "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, rc],
                    "px_lo": r0 - pad, "px_hi": r1 + pad,
                    "note": f"line rows {r0}-{r1}; misfit x {cal['xmis']:.1f} px, y {cal['ymis']:.1f} px"})
    return out


def load(name):
    """Import a sibling module of this folder by file name."""
    import importlib.util
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
