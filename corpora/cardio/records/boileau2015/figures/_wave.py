"""Shared reading code for the waveform panels of Figs. 3-9 (matplotlib plots, vector graphics,
rendered at 1200 dpi): the red curve of each panel (the 3D solution of [33] in Figs. 3-5, the in
vitro measurement of [45], 'Exp.', in Figs. 6-9).

Calibration, all from the image:
- black ink: gray < 110 and channel spread < 50 (frame, ticks, dotted grid, text; also the black
  DCG curve where it shows);
- the plot frame: the two rows (columns) of black ink spanning more than half the crop; their
  centres are the frame lines;
- the dotted grid lines: bands of rows (columns) at most 12 px wide, at least 12 px inside the
  frame, holding 5-70% black ink along the frame, with ink in at least 5 of 10 equal stretches
  of it and broken into at least 15 separate dots (a dotted grid line crosses the whole plot,
  partly hidden under the curves and the legend box; a legend border or the black DCG curve is
  not dotted);
- the printed labels of each axis are matched in order to the grid lines, plus the frame lines
  where a label sits on them (FRAME flags per panel); the count must agree exactly;
- a straight line is fitted to each axis' marks; its largest misfit (px) widens every interval;
  a misfit over 4 px raises an error.

The red curve: pixels with R > 200, G < 90 and B < 90 (the line's core is pure red; blends of other
colours at anti-aliased crossings, such as (189, 95, 96), are left out), outside the legend box
the panel names. At each x, the red pixels in the columns within +-1 px are split into runs; runs
closer than 30 px are merged, and so are runs up to 120 px apart whose gap (in the centre column)
is at least 80% covered by other ink (gray < 230: the 1D curves drawn over the red one split it); the
merged run then spans the covered part and its interval grows with it. Exactly one merged run is
required. Where the red line is wholly hidden under the 1D curves (drawn over it) the value
is not read. The value is the centre of the run. With w the red line's width (the median height
of single short runs over the panel), a run shorter than w is part of a partly covered line whose
centre lies within (w - run)/2 of the run's centre; a run taller than w is a steep stretch whose
centre is uncertain by (run - w)/2. The interval is |w - run|/2 + 1.5 px (anti-aliasing) plus the
calibration misfit, plus the local slope (from +-8 px) times the x misfit. A run taller than
250 px is a near-vertical stretch and is not read.
"""

import numpy as np


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def masks(image):
    im = image[..., :3].astype(float)
    g = im.mean(axis=2)
    spread = im.max(axis=2) - im.min(axis=2)
    black = (g < 110) & (spread < 50)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    red = (R > 200) & (G < 90) & (B < 90)
    return black, red


def _frame(frac):
    fr = [(a + b - 1) / 2.0 for a, b in _runs(frac > 0.5)]
    if len(fr) != 2:
        raise RuntimeError(f"frame lines: {fr}")
    return fr


def _grid(black, along, lo, hi, other_lo, other_hi):
    """Grid bands perpendicular to `along` (0: rows, 1: columns), between lo and hi, measured
    over the other axis from other_lo to other_hi."""
    if along == 0:
        sub = black[:, int(other_lo) + 12: int(other_hi) - 12]
    else:
        sub = black[int(other_lo) + 12: int(other_hi) - 12, :].T
    frac = sub.mean(axis=1)
    out = []
    for a, b in _runs((frac >= 0.05) & (frac <= 0.7)):
        if b - a > 12 or a < lo + 12 or b > hi - 12:
            continue
        band = sub[a:b].any(axis=0)
        segs = np.array_split(band, 10)
        if sum(s.any() for s in segs) >= 5 and len(_runs(band)) >= 15:
            out.append((a + b - 1) / 2.0)
    return out


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    if mis > 4.0:
        raise RuntimeError(f"calibration misfit {mis:.1f} px: {marks}")
    return a, b, max(mis, 0.5)


def calibrate(image, X, Y, xframe, yframe, legend=None):
    """X: x labels left to right; Y: y labels bottom to top. xframe = (left frame carries X[0],
    right frame carries X[-1]); yframe = (bottom frame carries Y[0], top frame carries Y[-1]).
    The legend box (crop px) is blanked before the grid lines are looked for."""
    black, red = masks(image)
    top, bot = _frame(black.mean(axis=1))
    left, right = _frame(black.mean(axis=0))
    bg = black.copy()
    if legend is not None:
        c0, r0, c1, r1 = legend
        bg[r0:r1, c0:c1] = False
    gx = _grid(bg, 1, left, right, top, bot)
    gy = _grid(bg, 0, top, bot, left, right)
    xin = X[1 if xframe[0] else 0: len(X) - 1 if xframe[1] else len(X)]
    yin = Y[1 if yframe[0] else 0: len(Y) - 1 if yframe[1] else len(Y)]
    if len(gx) != len(xin) or len(gy) != len(yin):
        raise RuntimeError(f"grid lines x {gx} for {xin}; y {gy} for {yin}")
    xm = list(zip(gx, xin))
    if xframe[0]:
        xm.append((left, X[0]))
    if xframe[1]:
        xm.append((right, X[-1]))
    ym = list(zip(gy[::-1], yin))       # rows grow downwards; labels bottom to top
    if yframe[0]:
        ym.append((bot, Y[0]))
    if yframe[1]:
        ym.append((top, Y[-1]))
    xa, xb, xmis = _fit(xm)
    ya, yb, ymis = _fit(ym)
    return dict(black=black, red=red, frame=(left, top, right, bot), xa=xa, xb=xb, xmis=xmis,
                ya=ya, yb=yb, ymis=ymis)


def _centre(m, c, cover=None):
    rows = np.flatnonzero(m[:, max(c - 1, 0): c + 2].any(axis=1))
    if not len(rows):
        return []
    rr = _runs(np.isin(np.arange(m.shape[0]), rows))
    merged = []
    for a, b in rr:
        gap = a - merged[-1][1] if merged else None
        covered = (cover is not None and gap is not None and gap <= 120
                   and float(np.mean(cover[merged[-1][1]:a, c])) >= 0.8)
        if merged and (gap <= 30 or covered):
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


def read_red(image, at, X, Y, xframe, yframe, legend=None):
    cal = calibrate(image, X, Y, xframe, yframe, legend)
    m = cal["red"].copy()
    left, top, right, bot = cal["frame"]
    m[:, : int(left) + 4] = False
    m[:, int(right) - 3:] = False
    if legend is not None:
        c0, r0, c1, r1 = legend
        m[r0:r1, c0:c1] = False
    # the red line's width: median run height over all columns where one short run is found
    hs = []
    for c in range(int(left) + 10, int(right) - 10, 7):
        rr = _runs(m[:, c])
        if len(rr) == 1 and rr[0][1] - rr[0][0] < 40:
            hs.append(rr[0][1] - rr[0][0])
    lw = float(np.median(hs)) if hs else 8.0
    # ink of other curves (anything not near-white) that may cover the red line
    cover = image[..., :3].astype(float).mean(axis=2) < 230
    out = []
    for x in at:
        x = float(x)
        col = (x - cal["xa"]) / cal["xb"]
        c = int(round(col))
        runs = _centre(m, c, cover)
        if not runs:
            out.append({"x": x, "y": None, "note": "the red line is hidden under the 1D curves here"})
            continue
        if len(runs) > 1:
            out.append({"x": x, "y": None, "note": f"{len(runs)} separate red runs in this column"})
            continue
        a, b = runs[0]
        if b - a > 250:
            out.append({"x": x, "y": None, "note": f"red run {b - a} px tall: a near-vertical stretch"})
            continue
        row = (a + b - 1) / 2.0
        nb = []
        for k in (c - 8, c + 8):
            rk = _centre(m, k)
            if len(rk) == 1:
                nb.append((rk[0][0] + rk[0][1] - 1) / 2.0)
        sl = abs(nb[1] - nb[0]) / 16.0 if len(nb) == 2 else 0.0
        e = abs(lw - (b - a)) / 2.0 + 1.5 + cal["ymis"] + sl * cal["xmis"]
        y = cal["ya"] + cal["yb"] * row
        ylo = cal["ya"] + cal["yb"] * (row + e)
        yhi = cal["ya"] + cal["yb"] * (row - e)
        out.append({"x": x, "y": y, "lo": min(ylo, yhi), "hi": max(ylo, yhi), "px": [col, row],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": f"red run {b - a} px; line {lw:.0f} px; misfit x {cal['xmis']:.1f}, y {cal['ymis']:.1f} px"})
    return out


def panel(X, Y, xframe, yframe, legend=None):
    def read(image, at):
        return read_red(image, at, X, Y, xframe, yframe, legend)
    return read
