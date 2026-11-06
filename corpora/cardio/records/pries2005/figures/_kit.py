"""Shared reading code for the line plots of pries2005 (Figs. 2 and 4): black vector art on white.

Calibration, all from the image:
  the frame lines are the outermost groups of dark rows and columns longer than half the crop; the
  tick marks point outward from it and are found as dark runs (at least 8 px deep) just outside the
  bottom and left frame lines.  The x axis is logarithmic: the long ticks are matched in order to the
  printed decade labels the reading passes; the short ticks are then checked against the decade
  pattern (2, 3, ... 9 times a power of ten).  The y axis is matched tick by tick, from the bottom,
  to the printed labels the reading passes (`ylabels`; `ylong` = only the long ticks).  Each axis is
  a least-squares straight line in position (log10 where logarithmic); the largest misfit in pixels
  (label ticks and the short-tick check) is reported and added to every interval.

Separating the curves:
  thick ink = an opening of the ink (grey < 128) with a disk 7 px across: lines 8 px wide or more
  survive; thin lines (3-4 px), ticks, the hatching of Fig. 2 and tiny dots do not;
  thin ink = ink farther than 4 px from thick ink.
  Both are confined to the plot interior, 3 px inside the frame.

Tracing one curve: the reading lists segments, each with a seed column (`seed_x`), the rank of the
curve among the runs of that ink in the seed column (counted from the top) and the x range the
segment covers; a cusp (the peak or trough near 10.5 um) separates two segments.  From the seed the
curve is followed column by column in both directions.  In each column the runs of the ink (gaps up
to 2 px closed) are the candidates; runs shorter than 0.8 of the line's recent run length are the
oblique ends of dashes or dots and are passed over.  The prediction is a quadratic fit to the found
centres of the last 60 columns (a straight line over the last 8 at the start); the run nearest it is
kept when within 6 px + 2 |slope| + 0.4 px per column of gap.  A run that suddenly lengthens by more
than 10 px holds this curve fused with another (a crossing); while fused, the centre is the
prediction kept inside the run.  With no run near the prediction (a dash gap, or a thin line hidden
under a thick one) the prediction is kept; after 150 such columns the curve is lost.
The readings' `at` lists keep only positions where the overlays show the trace on the named curve.

Intervals (95%): a found line centre +-(2 px + misfit); a fused run: from the top to the bottom of
the run, less half the line thickness, +-(2 px + misfit); a gap: the prediction +-(8 px + 0.1 px per
column of gap + misfit).  A reading is `None` where the curve is lost.
"""

import numpy as np
from scipy import ndimage


def runs(v, close=0):
    v = np.asarray(v, bool)
    d = np.diff(np.concatenate([[0], v.astype(int), [0]]))
    s = np.flatnonzero(d == 1).tolist()
    e = np.flatnonzero(d == -1).tolist()
    out = list(zip(s, e))
    if close and out:
        m = [list(out[0])]
        for a, b in out[1:]:
            if a - m[-1][1] <= close:
                m[-1][1] = b
            else:
                m.append([a, b])
        out = [tuple(x) for x in m]
    return out


def dark_of(image):
    g = np.asarray(image, float)
    if g.ndim == 3:
        g = g[..., :3].mean(axis=2)
    return g < 128


def frame(dark):
    H, W = dark.shape
    rr = [i for i in range(H) if dark[i].sum() > 0.5 * W]
    cc = [j for j in range(W) if dark[:, j].sum() > 0.5 * H]
    def groups(v):
        g = [[v[0]]]
        for i in v[1:]:
            if i - g[-1][-1] <= 1:
                g[-1].append(i)
            else:
                g.append([i])
        return g

    gr, gc = groups(rr), groups(cc)  # the outermost groups are the frame lines
    return gc[0][0], gc[0][-1], gc[-1][0], gc[-1][-1], gr[0][0], gr[0][-1], gr[-1][0], gr[-1][-1]


def ticks(dark, fr):
    """Outward ticks: (centre, depth) on the bottom (x) and on the left (y) frame lines."""
    l0, l1, r0, r1, t0, t1, b0, b1 = fr
    band = dark[b1 + 1:b1 + 9, :].all(0)
    band[:l0 - 10] = False
    band[r1 + 10:] = False
    xt = []
    for s, e in runs(band):
        c = int(round((s + e - 1) / 2))
        k = 0
        while b1 + 1 + k < dark.shape[0] and dark[b1 + 1 + k, c]:
            k += 1
        xt.append(((s + e - 1) / 2, k))
    band = dark[:, l0 - 8:l0].all(1)
    band[:t0 - 10] = False
    band[b1 + 10:] = False
    yt = []
    for s, e in runs(band):
        r = int(round((s + e - 1) / 2))
        k = 0
        while l0 - 1 - k >= 0 and dark[r, l0 - 1 - k]:
            k += 1
        yt.append(((s + e - 1) / 2, k))
    return xt, yt


def fit(pos, val, log):
    v = np.log10(val) if log else np.asarray(val, float)
    a, b = np.polyfit(np.asarray(pos, float), v, 1)  # value = a pos + b
    mis = float(np.max(np.abs((v - b) / a - np.asarray(pos, float))))
    return a, b, mis


def calibrate(image, xlabels, ylabels, ylog, ylong):
    dark = dark_of(image)
    fr = frame(dark)
    xt, yt = ticks(dark, fr)
    depth = max(k for _, k in xt)
    xmaj = [c for c, k in xt if k > 0.8 * depth]
    if len(xmaj) != len(xlabels):
        raise ValueError(f"found {len(xmaj)} long x ticks for {len(xlabels)} labels")
    ydepth = max(k for _, k in yt)
    ysel = [r for r, k in yt if (k > 0.8 * ydepth) or not ylong]
    ysel = sorted(ysel, reverse=True)  # from the bottom
    if len(ysel) != len(ylabels):
        raise ValueError(f"found {len(ysel)} y ticks for {len(ylabels)} labels")
    ax, bx, mx = fit(xmaj, xlabels, True)
    ay, by, my = fit(ysel, ylabels, ylog)
    # check: the short x ticks of a log axis stand at whole multiples of the decade
    mm = 0.0
    for c, _ in xt:
        lv = ax * c + bx
        dec = np.floor(lv + 1e-9)
        k = np.clip(np.round(10 ** (lv - dec)), 1, 10)
        mm = max(mm, abs((np.log10(k) + dec - bx) / ax - c))
    mis = max(mx, my, mm)
    return dict(dark=dark, frame=fr, ax=ax, bx=bx, ay=ay, by=by, ylog=ylog, misfit=mis,
                note=f"x ticks {[round(c) for c in xmaj]} = {xlabels}, y ticks {[round(r) for r in ysel]} = "
                     f"{ylabels}; misfit {max(mx, my):.2f} px, minor x ticks off the decade pattern by at most "
                     f"{mm:.2f} px")


def col_of(cal, x):
    return (np.log10(x) - cal["bx"]) / cal["ax"]


def y_of(cal, row):
    v = cal["ay"] * row + cal["by"]
    return float(10 ** v) if cal["ylog"] else float(v)


def inks(cal):
    dark = cal["dark"]
    l0, l1, r0, r1, t0, t1, b0, b1 = cal["frame"]
    inner = np.zeros_like(dark)
    inner[t1 + 4:b0 - 3, l1 + 4:r0 - 3] = True
    d = dark & inner
    yy, xx = np.mgrid[-3:4, -3:4]
    disk = (xx ** 2 + yy ** 2) <= 9
    thick = ndimage.binary_opening(d, structure=disk)
    near = ndimage.binary_dilation(thick, structure=np.ones((9, 9), bool))
    thin = d & ~near
    return {"thick": thick, "thin": thin}


def trace(mask, seed_col, rank, lo_col, hi_col, w):
    """Trace one curve from the rank-th run (from the top) of `mask` in `seed_col`."""
    col_runs = lambda c: runs(mask[:, c], close=2)  # noqa: E731
    rr = col_runs(seed_col)
    if rank >= len(rr):
        raise ValueError(f"seed column {seed_col}: only {len(rr)} runs")
    s, e = rr[rank]
    out = {seed_col: ((s + e - 1) / 2, (s + e - 1) / 2 - 2, (s + e - 1) / 2 + 2, "found", 0)}
    for step in (1, -1):
        pts = [(seed_col, (s + e - 1) / 2)]
        lens = [e - s]
        gap = 0
        base = None  # while fused: the run length before the fusion
        c = seed_col + step
        while lo_col <= c <= hi_col:
            recent = [q for q in pts[-80:] if abs(q[0] - c) <= 60 + gap]
            if len(recent) >= 12 and abs(recent[0][0] - recent[-1][0]) >= 20:
                cs, rs = np.array(recent).T
                k2 = np.polyfit(cs - c, rs, 2)
                p = k2[2]
                sl = k2[1]
            elif len(pts) >= 2:
                cs, rs = np.array(pts[-8:]).T
                sl, ic = np.polyfit(cs, rs, 1)
                p = sl * c + ic
            else:
                sl, p = 0.0, pts[-1][1]
            ve = max(float(np.median(lens[-8:])), w)
            tol = 6 + 2 * abs(sl) + 0.4 * gap
            best = None
            for a, b in col_runs(c):
                if (b - a) < 0.8 * ve:  # the oblique end of a dash: its centre is off the line
                    continue
                dist = 0 if a <= p <= b - 1 else min(abs(a - p), abs(b - 1 - p))
                if dist <= tol and (best is None or dist < best[0]):
                    best = (dist, a, b)
            if best is None:
                gap += 1
                if gap > 150:
                    break
                out[c] = (p, p - 8 - 0.1 * gap, p + 8 + 0.1 * gap, "gap", gap)
            else:
                _, a, b = best
                L = b - a
                if base is None and gap == 0 and L > lens[-1] + 10:
                    base = lens[-1]  # a sudden lengthening: another line joins this one
                elif base is None and gap > 0 and L > ve + 10:
                    base = ve
                elif base is not None and L <= base + 8:
                    base = None
                if base is not None:
                    lo, hi = a + base / 2, b - 1 - base / 2
                    r = min(max(p, lo), hi)
                    out[c] = (r, lo - 2, hi + 2, "fused", 0)
                else:
                    r = (a + b - 1) / 2
                    out[c] = (r, r - 2, r + 2, "found", 0)
                    lens.append(L)
                    pts.append((c, r))
                gap = 0
            c += step
    return out


def read_curve(image, at, spec):
    cal = calibrate(image, spec["xlabels"], spec["ylabels"], spec["ylog"], spec.get("ylong", False))
    ink = inks(cal)
    w = spec.get("w", {"thick": 12.0, "thin": 4.0}[spec["ink"]])  # line width in pixels
    traces = []
    for seg in spec["segments"]:  # each: seed_x, rank, x_range
        seed = int(round(col_of(cal, seg["seed_x"])))
        lo_c = int(np.ceil(col_of(cal, seg["x_range"][0])))
        hi_c = int(np.floor(col_of(cal, seg["x_range"][1])))
        traces.append((seg["x_range"], trace(ink[spec["ink"]], seed, seg["rank"], lo_c, hi_c, w)))
    mis = cal["misfit"]
    res = []
    for x in at:
        cf = col_of(cal, x)
        c = int(round(cf))
        tr = next((t for (a, b), t in traces if a <= x <= b), {})
        if c not in tr:
            res.append({"x": x, "y": None, "note": "outside the traced range of this curve"})
            continue
        r, lo, hi, st, g = tr[c]
        lo -= mis
        hi += mis
        y = y_of(cal, r)
        ya, yb = y_of(cal, hi), y_of(cal, lo)
        res.append({"x": x, "y": y, "lo": min(ya, yb), "hi": max(ya, yb), "px": [cf, r], "px_lo": lo,
                    "px_hi": hi, "note": f"{st}{' ' + str(g) + ' columns' if st == 'gap' else ''}; {cal['note']}"})
    return res


def load(name):
    import importlib.util
    from pathlib import Path
    sp = importlib.util.spec_from_file_location(f"pries2005_{name}", Path(__file__).with_name(f"{name}.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m
