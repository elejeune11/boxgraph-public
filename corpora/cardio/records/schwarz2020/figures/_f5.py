"""Shared reading code for Fig. 5 (PDF p. 9): five panels of medians and interquartile areas against
segment diameter on a logarithmic x axis.  Vector art rendered at 1000 dpi.

Inks, all told apart by colour (measured on the crops; each pixel is assigned to the nearest
reference colour within a tolerance):
  black  : the axes, ticks and the 'cast, fit' line            max(R, G, B) < 90
  brown  : 'cast, median' line                                 about (130, 105, 25)
  teal   : 'in silico, median' line                            about (32, 144, 128)
  tan    : 'cast, IQR' area                                    about (227, 213, 164)
  cyan   : 'in silico, IQR' area                               about (218, 244, 241)
  both   : the two areas overlapping                           about (207, 231, 209)

Calibration, from the image only:
  the y axis is the column with the longest vertical black run, the x axis the row with the longest
  horizontal black run.  Ticks point outward: x ticks are black runs going down from the bottom of
  the x axis line, y ticks black runs going left from the left edge of the y axis line (the axis lines
  themselves run on past the corner and serve as the first tick of each axis).  The deepest ticks are
  the labelled ones: matched in order (left to right; bottom to top) to the printed labels.  Each axis
  is a least-squares line in position (log10 for logarithmic axes); the misfit is the largest
  distance in pixels of a labelled tick from the fit.  On a logarithmic axis the short ticks are also
  checked against the decade pattern (2 ... 9 times a power of ten) and that misfit is included.

Reading a line at an x position: the column of that x; the runs of the line's ink in the plot interior
(beyond the axes).  One run: its centre is the value.  Where the run touches a run of another line
ink (the line is partly hidden under the other one, e.g. the brown median under the black fit),
the interval spans both runs.  No run of the ink: not read (hidden or outside the line's range).
More than one run (the line folds back, which these lines do not): the run nearest the run read in the
previous `at` position is kept, and the note says so.
Interval (95%): the run, or the union of touching runs, +-(1 px + misfit).

Reading an area edge ('upper' or 'lower' quartile): in the column, the topmost (upper) or bottommost
(lower) pixel whose colour is that area's fill (alone or overlapping the other area).  A line drawn
over the edge hides it: when a line ink pixel lies within 3 px beyond the found edge, the edge may be
under that line and the interval reaches across the line.  Interval: +-(2 px + misfit), widened so.
"""
import numpy as np

REF = {
    "brown": (130, 105, 25),
    "teal": (32, 144, 128),
    "tan": (227, 213, 164),
    "cyan": (218, 244, 241),
    "both": (207, 231, 209),
}
TOL = {"brown": 45, "teal": 45, "tan": 14, "cyan": 10, "both": 12}


def runs(v):
    v = np.asarray(v, bool)
    d = np.diff(np.concatenate([[0], v.astype(int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def masks(image):
    a = np.asarray(image, float)[..., :3]
    out = {"black": a.max(axis=2) < 90}
    for k, c in REF.items():
        out[k] = np.sqrt(((a - np.array(c, float)) ** 2).sum(axis=2)) < TOL[k]
    out["black"] &= ~out["brown"]
    return out


def _fit(pos, labels, log):
    v = np.log10(labels) if log else np.asarray(labels, float)
    a, b = np.polyfit(np.asarray(pos, float), v, 1)
    mis = float(np.max(np.abs((v - b) / a - np.asarray(pos, float))))
    return a, b, mis


def _log_minor_misfit(pos, a, b):
    mm = 0.0
    for c in pos:
        lv = a * c + b
        dec = np.floor(lv + 1e-9)
        k = np.clip(np.round(10 ** (lv - dec)), 1, 10)
        mm = max(mm, abs((np.log10(k) + dec - b) / a - c))
    return mm


def _ticks(dep):
    """Long ticks: runs of positions deeper than 0.8 of the deepest; all ticks: runs deeper than 10 px
    of ordinary width (ticks fused with a neighbour into one wider run are left out of the check)."""
    dmax = dep.max()
    maj = [(a + b - 1) / 2 for a, b in runs(dep > 0.8 * dmax)]
    rr = runs(dep > 10)
    wmed = np.median([b - a for a, b in rr])
    allt = [(a + b - 1) / 2 for a, b in rr if b - a <= 1.5 * wmed]
    return maj, allt


def calibrate(image, xlabels, ylabels, ylog):
    m = masks(image)
    k = m["black"]
    H, W = k.shape
    vlen = [max([b - a for a, b in runs(k[:, j])] or [0]) for j in range(W)]
    ycol = int(np.argmax(vlen))
    ycols = [j for j in range(max(ycol - 20, 0), min(ycol + 20, W)) if vlen[j] > 0.8 * vlen[ycol]]
    yl, yr = min(ycols), max(ycols)
    hlen = [max([b - a for a, b in runs(k[i, :])] or [0]) for i in range(H)]
    xrow = int(np.argmax(hlen))
    xrows = [i for i in range(max(xrow - 20, 0), min(xrow + 20, H)) if hlen[i] > 0.8 * hlen[xrow]]
    xt, xb = min(xrows), max(xrows)
    # x ticks: black going down from the bottom of the x axis line, depth per column (label glyphs
    # left of the y axis are not ticks); y ticks: black going left from the y axis line, per row.
    xdep = np.zeros(W, int)
    for j in range(max(yl - 3, 0), W):
        d = 0
        while xb + 1 + d < H and k[xb + 1 + d, j]:
            d += 1
        xdep[j] = d
    ydep = np.zeros(H, int)
    for i in range(0, min(xb + 4, H)):
        d = 0
        while yl - 1 - d >= 0 and k[i, yl - 1 - d]:
            d += 1
        ydep[i] = d
    xmaj, xall = _ticks(xdep)
    ymaj, yall = _ticks(ydep)
    ymaj = sorted(ymaj, reverse=True)
    if len(xmaj) != len(xlabels):
        raise ValueError(f"found {len(xmaj)} long x ticks for {len(xlabels)} labels")
    if len(ymaj) != len(ylabels):
        raise ValueError(f"found {len(ymaj)} long y ticks for {len(ylabels)} labels")
    ax, bx, mx = _fit(xmaj, xlabels, True)
    mmx = _log_minor_misfit(xall, ax, bx)
    ay, by, my = _fit(ymaj, ylabels, ylog)
    mmy = _log_minor_misfit(yall, ay, by) if ylog else 0.0
    mis = max(mx, my, mmx, mmy)
    note = (f"x long ticks at columns {[round(c) for c in xmaj]} = {xlabels}; y long ticks at rows "
            f"{[round(r) for r in ymaj]} = {ylabels}; misfit {max(mx, my):.2f} px, minor ticks off the "
            f"decade pattern by at most {max(mmx, mmy):.2f} px")
    return dict(m=m, ax=ax, bx=bx, ay=ay, by=by, ylog=ylog, mis=mis, note=note,
                interior=(yr + 6, xt - 6), H=H, W=W)


def col_of(cal, x):
    return (np.log10(x) - cal["bx"]) / cal["ax"]


def y_of(cal, r):
    v = cal["ay"] * r + cal["by"]
    return float(10 ** v) if cal["ylog"] else float(v)


def _interval(cal, top, bot):
    ya, yb = y_of(cal, bot), y_of(cal, top)
    return min(ya, yb), max(ya, yb)


LINES = ("black", "brown", "teal")


def read_line(image, at, xlabels, ylabels, ylog, ink, xrange=None):
    cal = calibrate(image, xlabels, ylabels, ylog)
    c0, r1 = cal["interior"]
    m = cal["m"]
    out, prev = [], None
    for xs in at:
        x = float(xs)
        if xrange and not (xrange[0] <= x <= xrange[1]):
            out.append({"x": x, "y": None, "note": "outside the range read for this line"})
            continue
        cf = col_of(cal, x)
        c = int(round(cf))
        if c <= c0 or c >= cal["W"]:
            out.append({"x": x, "y": None, "note": "outside the plot"})
            continue
        col = {k: m[k][:r1, c] for k in LINES}
        rr = [(a, b) for a, b in runs(col[ink]) if b - a >= 3]
        if not rr:
            out.append({"x": x, "y": None, "note": f"no {ink} ink in this column (hidden or beyond the line)"})
            continue
        note = ""
        if len(rr) > 1:
            ref = prev if prev is not None else np.mean([(a + b) / 2 for a, b in rr])
            rr = [min(rr, key=lambda t: abs((t[0] + t[1]) / 2 - ref))]
            note = "several runs, the one nearest the previous reading kept; "
        a, b = rr[0]
        top, bot = a, b - 1
        hidden = False
        for other in LINES:
            if other == ink:
                continue
            for s, e in runs(col[other]):
                if s <= bot + 3 and e - 1 >= top - 3:
                    top, bot = min(top, s), max(bot, e - 1)
                    hidden = True
        r = (a + b - 1) / 2
        prev = r
        pad = 1 + cal["mis"]
        lo, hi = _interval(cal, top - pad, bot + pad)
        note += ("touches another line: the interval spans both; " if hidden else "") + cal["note"]
        out.append({"x": x, "y": y_of(cal, r), "lo": lo, "hi": hi, "px": [float(cf), float(r)],
                    "px_lo": float(bot + pad), "px_hi": float(top - pad), "note": note})
    return out


def read_edge(image, at, xlabels, ylabels, ylog, area, side, xrange=None):
    cal = calibrate(image, xlabels, ylabels, ylog)
    c0, r1 = cal["interior"]
    m = cal["m"]
    fill = m[area] | m["both"]
    line = m["black"] | m["brown"] | m["teal"]
    out = []
    for xs in at:
        x = float(xs)
        if xrange and not (xrange[0] <= x <= xrange[1]):
            out.append({"x": x, "y": None, "note": "outside the range read for this area"})
            continue
        cf = col_of(cal, x)
        c = int(round(cf))
        rows = np.flatnonzero(fill[:r1, c])
        if c <= c0 or len(rows) < 3:
            out.append({"x": x, "y": None, "note": f"no {area} fill in this column"})
            continue
        r = int(rows[0] if side == "upper" else rows[-1])
        step = -1 if side == "upper" else 1
        top = bot = r
        note = ""
        # a line just beyond the edge may hide the true edge: reach across it
        j = r + step
        k = 0
        while 0 <= j < r1 and k <= 3 and not line[j, c]:
            j += step
            k += 1
        if 0 <= j < r1 and line[j, c]:
            while 0 <= j < r1 and line[j, c]:
                j += step
            top, bot = min(r, j), max(r, j)
            note = "a line lies on the edge: the interval reaches across it; "
        pad = 2 + cal["mis"]
        lo, hi = _interval(cal, top - pad, bot + pad)
        out.append({"x": x, "y": y_of(cal, r), "lo": lo, "hi": hi, "px": [float(cf), float(r)],
                    "px_lo": float(bot + pad), "px_hi": float(top - pad), "note": note + cal["note"]})
    return out


def load():
    import importlib.util
    import os
    sp = importlib.util.spec_from_file_location("schwarz2020_f5", os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "_f5.py"))
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod
