"""Shared reading code for Fig. 7 (PDF p. 10): peak forward (black circles, solid line) and backward
(red circles, dashed line) wave intensity, log10 scale, against distance along six arteriovenous paths.

The figure is a bitmap embedded at about 300 dpi; rendered at 1200 dpi each source pixel is a block of
about 4 x 4 px. Everything below is found in the rendered crop.

Calibration: the axes are the gray (about 100/255) lines, the longest dark row in the lower part of the
crop (x axis) and the longest dark column in its left part (y axis); the gray microvascular band
(about 150/255) is lighter than the 125 threshold used. Tick marks are short dark runs (6-40 px)
standing inward from each axis line. The labelled ticks are evenly spaced, so the candidate ticks are
matched to the printed labels passed in the panel's spec (all interior ticks: the tick at the axis
corner merges with the other axis line) by choosing the evenly spaced set that the most candidates fit,
then fitted by a straight line; the largest tick misfit (px) is reported and added to every interval.

Markers: open circles. Ink masks: black = every channel below 90 (the gray axes and band excluded),
red = R above 150 with G and B below 130. Circle centres are found by correlating each mask with a ring
(the annulus of the circle's line) less its inside disk; the ring radius is chosen from the image as the
one giving the strongest mean of the best ten peaks over radii of 10-30 px. Peaks are local maxima above
half the best score, at least 0.6 radius apart, inside the plot box (rows above the x axis line and
columns right of the y axis line, below the top of the y axis line).
Intervals (95%): the centre lies within a quarter of the circle's line width plus 2 px (the source
bitmap's pixel is 4 px), plus the calibration misfit; where two peaks are closer than 1.2 radii (overlapping
circles) the interval is widened by half a radius and the reading says so.
"""

import numpy as np
from scipy import ndimage, signal

THRESHOLD = 0.25
LOW = 0.12
COVER = 0.85
OWN_MIN = 0.4


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def axes(dark):
    H, W = dark.shape
    rows = dark[H // 2:].sum(1)
    xr = np.flatnonzero(rows > 0.8 * rows.max()) + H // 2
    cols = np.array([max([b - a for a, b in _runs(dark[:, j])] or [0]) for j in range(W // 2)])
    # the y axis: the leftmost narrow group of columns with long runs (the gray band is wider)
    groups = [(a, b) for a, b in _runs(cols > 0.6 * cols.max()) if b - a <= 12]
    y_left, y_right = groups[0][0], groups[0][1] - 1
    x_top, x_bot = int(xr.min()), int(xr.max())
    top = min(a for a, b in _runs(dark[:, y_left]) if b - a >= 30)
    return {"xrow0": x_top, "xrow1": x_bot, "ycol0": y_left, "ycol1": y_right, "top": top}


def _inward(line):
    n = 0
    while n < len(line) and line[n]:
        n += 1
    return n


def _groups(lengths, off, lo=6, hi=40):
    pos = [i for i, n in enumerate(lengths) if lo <= n <= hi]
    out, cur = [], []
    for p in pos + [None]:
        if cur and (p is None or p != cur[-1] + 1):
            if len(cur) <= 10:
                out.append(off + (cur[0] + cur[-1]) / 2.0 + 0.5)
            cur = []
        if p is not None:
            cur.append(p)
    return out


def ticks(dark, ax):
    xt = [_inward(dark[: ax["xrow0"], c][::-1]) for c in range(ax["ycol1"] + 1, dark.shape[1])]
    yt = [_inward(dark[r, ax["ycol1"] + 1:]) for r in range(ax["top"], ax["xrow0"])]
    return _groups(xt, ax["ycol1"] + 1), _groups(yt, ax["top"])


def fit_even(cands, labels, what):
    """The evenly spaced set of len(labels) positions that the most candidates fit (within 4 px)."""
    c = np.array(sorted(cands), float)
    n = len(labels)
    best = None
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            for k0 in range(n):
                for k1 in range(k0 + 1, n):
                    step = (c[j] - c[i]) / (k1 - k0)
                    if step < 20:
                        continue
                    pred = c[i] + (np.arange(n) - k0) * step
                    d = np.abs(c[None, :] - pred[:, None])
                    hit = d.min(1) <= 4
                    m = int(hit.sum())
                    if best is None or m > best[0]:
                        best = (m, [float(c[d[q].argmin()]) for q in range(n) if hit[q]],
                                [labels[q] for q in range(n) if hit[q]])
    if best is None or best[0] < max(3, n - 1):
        raise ValueError(f"{what}: ticks {cands} do not match {labels}")
    p, v = np.array(best[1]), np.array(best[2], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - a) / b - p)))
    return a, b, mis, best[1]


def ring_scores(mask, r, w):
    R = int(np.ceil(r + w / 2 + 7))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    d = np.hypot(yy, xx)
    ring = (np.abs(d - r) <= w / 2).astype(float)
    inside = (d < r - w / 2 - 2).astype(float)
    outside = ((d > r + w / 2 + 2) & (d < r + w / 2 + 6)).astype(float)
    k = ring / ring.sum() - 0.5 * inside / max(inside.sum(), 1) - 0.5 * outside / outside.sum()
    return signal.fftconvolve(mask.astype(float), k[::-1, ::-1], mode="same")


def _peaks(s, r, thr):
    mx = ndimage.maximum_filter(s, size=int(1.2 * r) | 1)
    pk = [tuple(p) for p in np.argwhere((s == mx) & (s > thr))]
    out = []
    for p in sorted(pk, key=lambda q: -s[q]):
        if all(np.hypot(p[0] - q[0], p[1] - q[1]) >= 0.6 * r for q in out):
            out.append(p)
    return out


def line_width(mask):
    """Most common run length of the ink, along rows and columns."""
    lens = []
    for line in list(mask[::7]) + list(mask.T[::7]):
        lens += [b - a for a, b in _runs(line)]
    lens = np.array(lens)
    lens = lens[(lens >= 2) & (lens <= 20)]
    return float(np.median(lens)) if len(lens) else 5.0


def centres(mask, ax, other):
    """Circle centres in `mask`; `other` is the ink of the other series, which may hide part of a circle."""
    w = line_width(mask)
    box = np.zeros_like(mask)
    box[ax["top"]: ax["xrow0"] - 2, ax["ycol1"] - 40:] = True  # circles at x = 0 sit on the y axis
    m = mask & box
    both = (mask | other) & box
    best = None
    for r in range(8, 31):
        s = ring_scores(m, r, w)
        top = sorted((s[p] for p in _peaks(s, r, 0.2)), reverse=True)[:10]
        sc = float(np.mean(top)) if top else 0.0
        if best is None or sc > best[0]:
            best = (sc, r, s)
    _, r, s = best
    keep, hidden = [], []
    for p in _peaks(s, r, LOW):
        own = coverage(m, p, r, w)
        if s[p] >= THRESHOLD and own >= COVER:
            keep.append(p)
        elif own >= OWN_MIN and coverage(both, p, r, w) >= COVER:
            hidden.append(p)  # partly hidden under the other series' ink
    return r, w, keep, hidden


def coverage(mask, p, r, w, n=24):
    """Fraction of n angular sectors of the ring around p in which at least half the ring is inked."""
    R = int(np.ceil(r + w))
    r0, c0 = p
    sub = mask[max(r0 - R, 0): r0 + R + 1, max(c0 - R, 0): c0 + R + 1]
    yy, xx = np.mgrid[max(r0 - R, 0) - r0: max(r0 - R, 0) - r0 + sub.shape[0],
                      max(c0 - R, 0) - c0: max(c0 - R, 0) - c0 + sub.shape[1]]
    d = np.hypot(yy, xx)
    ring = np.abs(d - r) <= w / 2
    sec = ((np.arctan2(yy, xx) + np.pi) / (2 * np.pi) * n).astype(int) % n
    good = 0
    for k in range(n):
        sel = ring & (sec == k)
        if sel.sum() and sub[sel].mean() >= 0.5:
            good += 1
    return good / n


def read_spec(image, at, spec):
    img = np.asarray(image)[:, :, :3].astype(int)
    ink = img.max(2) < 200
    ax = axes(ink)
    xc, yc = ticks(ink, ax)
    xa, xb, xm, _ = fit_even(xc, spec["x"], "x ticks")
    ya, yb, ym, _ = fit_even(yc, spec["y"], "y ticks")
    black = img.max(2) < 90
    red = (img[:, :, 0] > 150) & (img[:, :, 1] < 130) & (img[:, :, 2] < 130)
    mask, other = (black, red) if spec["curve"] == "forward" else (red, black)
    r, w, pts, hidden = centres(mask, ax, other)
    allp = sorted(pts + hidden, key=lambda p: p[1])
    out = []
    for (row, col) in allp:
        near = min([np.hypot(row - q[0], col - q[1]) for q in allp if q != (row, col)] or [1e9])
        e = w / 4 + 2 + ym  # px
        note = f"circle centre, ring radius {r} px, line {w:.0f} px; misfit x {xm:.1f} px, y {ym:.1f} px"
        if near < 1.2 * r:
            e += 0.5 * r
            note += f"; overlaps another circle ({near:.0f} px apart)"
        if (row, col) in hidden:
            e += 0.25 * r
            note += "; partly hidden under the other series' circle"
        x = xa + xb * (col + 0.5)
        lv = ya + yb * (row + 0.5)
        l1, l2 = ya + yb * (row + 0.5 + e), ya + yb * (row + 0.5 - e)
        out.append({"x": float(x), "y": float(10 ** lv), "lo": float(10 ** min(l1, l2)),
                    "hi": float(10 ** max(l1, l2)), "px": [float(col), float(row)],
                    "px_lo": float(row - e), "px_hi": float(row + e), "note": note})
    return out
