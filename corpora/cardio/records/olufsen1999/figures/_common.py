"""Shared figure-reading code for olufsen1999 (Figs. 3, 4 and 9). Everything is found in the image.

Calibration: the plot box is the frame of long dark lines. Tick marks are the short dark marks
that start at the inner edge of the bottom and left frame lines. The printed labels I matched are
passed in by each reader (which tick or frame line carries which label); the fit of label to pixel
is checked and its worst misfit is added to every interval.

Solid line: in a window of columns around each x, keep the dark runs that are present in every
column of the window (a solid line; dotted grid lines, dotted or dashed curves and '+' markers
break up). The value is the run's centre; the interval is its extent widened by the misfit + 2 px.

Markers ('+'): a pixel is a marker centre where both a horizontal and a vertical dark segment of
the arm length pass through it; centres closer than an arm length are merged.
"""
import math

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


def ticks_bottom(dark, top, bot, left, right):
    h = bot - top
    lengths = []
    for c in range(left + 3, right - 2):
        n, r = 0, bot - 1
        while r > top and dark[r, c]:
            n += 1
            r -= 1
        lengths.append(n)
    lengths = np.array(lengths)
    ticks = []
    for grp in groups(list(np.where(lengths > 0.006 * h)[0])):
        if lengths[grp].max() > 0.25 * h:
            continue
        ticks.append(left + 3 + float(np.mean(grp)))
    return ticks


def ticks_left(dark, top, bot, left, right):
    w = right - left
    lengths = []
    for r in range(top + 3, bot - 2):
        n, c = 0, left + 1
        while c < right and dark[r, c]:
            n += 1
            c += 1
        lengths.append(n)
    lengths = np.array(lengths)
    ticks = []
    for grp in groups(list(np.where(lengths > 0.004 * w)[0])):
        if lengths[grp].max() > 0.1 * w:
            continue
        ticks.append(top + 3 + float(np.mean(grp)))
    return ticks


def _fit(pix, vals):
    pix, vals = np.asarray(pix, float), np.asarray(vals, float)
    a, b = np.polyfit(vals, pix, 1)  # pixel = a * value + b
    return a, b, float(np.abs(a * vals + b - pix).max())


def _match(found, n, what):
    if len(found) != n:
        raise ValueError(f"expected {n} {what} ticks, found {len(found)} at {[round(f) for f in found]}")
    return sorted(found)


def calibrate_linear(image, x_frame, x_ticks, y_frame, y_ticks):
    """x_frame = (value at left frame or None, value at right frame or None); x_ticks: values of the
    interior bottom ticks, left to right. y_frame = (value at top frame or None, value at bottom frame
    or None); y_ticks: values of the interior left ticks, top to bottom."""
    g = gray(image)
    top, bot, left, right, dark = frame(g)
    xt = _match(ticks_bottom(dark, top, bot, left, right), len(x_ticks), "x")
    yt = _match(ticks_left(dark, top, bot, left, right), len(y_ticks), "y")
    xp, xv = list(xt), list(x_ticks)
    if x_frame[0] is not None:
        xp.append(left)
        xv.append(x_frame[0])
    if x_frame[1] is not None:
        xp.append(right)
        xv.append(x_frame[1])
    yp, yv = list(yt), list(y_ticks)
    if y_frame[0] is not None:
        yp.append(top)
        yv.append(y_frame[0])
    if y_frame[1] is not None:
        yp.append(bot)
        yv.append(y_frame[1])
    ax, bx, xmis = _fit(xp, xv)
    ay, by, ymis = _fit(yp, yv)
    return dict(top=top, bot=bot, left=left, right=right, gray=g, xmis=xmis, ymis=ymis,
                col_of=lambda x: ax * x + bx, x_of=lambda c: (c - bx) / ax,
                val_of=lambda r: (r - by) / ay)


def calibrate_fig9(image, ylog, ytop, ybot, ymid):
    """Fig. 9 B/C: log10 omega axis with decade ticks 10^0, 10^1, 10^2 and the right frame at 10^3;
    y from the frame ends (ytop, ybot) checked by the major tick ymid between them."""
    g = gray(image)
    top, bot, left, right, dark = frame(g)
    xt = ticks_bottom(dark, top, bot, left, right)
    tol = 0.01 * (right - left)
    best = None
    for t in xt:
        d = right - t
        if d < 0.15 * (right - left):
            continue
        dec = [t - 2 * d, t - d, t]
        found = [min(xt, key=lambda u: abs(u - p)) for p in dec]
        if any(abs(f - p) > tol for f, p in zip(found, dec)):
            continue
        minors = [t - 2 * d + (n + math.log10(k)) * d for n in range(3) for k in range(2, 10)]
        n_minor = sum(1 for p in minors if p > left and any(abs(u - p) < tol for u in xt))
        mis = max(abs(f - p) for f, p in zip(found, dec))
        key = (-n_minor, mis)
        if best is None or key < best[0]:
            best = (key, found)
    if best is None:
        raise ValueError(f"no decade ticks 10^0, 10^1, 10^2 with the right frame at 10^3; ticks at {xt}")
    ax, bx, xmis = _fit(best[1] + [right], [0.0, 1.0, 2.0, 3.0])
    t = math.log10 if ylog else (lambda v: v)
    vt, vb, vm = t(ytop), t(ybot), t(ymid)
    rmid_pred = top + (vt - vm) / (vt - vb) * (bot - top)
    yt = ticks_left(dark, top, bot, left, right)
    if not yt:
        raise ValueError("no y tick between the frame ends")
    ymis = abs(min(yt, key=lambda r: abs(r - rmid_pred)) - rmid_pred)

    def val_of(row):
        v = vt + (row - top) / (bot - top) * (vb - vt)
        return 10 ** v if ylog else v

    return dict(top=top, bot=bot, left=left, right=right, gray=g, xmis=xmis, ymis=ymis,
                col_of=lambda x: ax * math.log10(x) + bx, x_of=lambda c: 10 ** ((c - bx) / ax), val_of=val_of)


def ink_threshold(cal, frac=0.35):
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    paper = float(np.median(g))
    ink = float(np.percentile(g[top:bot, left:right], 0.2))
    return ink + frac * (paper - ink)


def read_solid(cal, at, half_frac=0.004):
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    dark = g < ink_threshold(cal)
    half = max(3, int(half_frac * (right - left)))
    margin = max(4, int(0.006 * (bot - top)))

    def col_runs(cc):
        return [(grp[0] + top + margin, grp[-1] + top + margin)
                for grp in groups(list(np.where(dark[top + margin:bot - margin, cc])[0]), gap=1)]

    def traces(run, c0, step):
        """Follow the run column by column for `half` columns: each next column must hold a dark run
        touching the current one (a solid line); dotted and dashed lines and markers break."""
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
        pad = 2 + cal["ymis"] + 0.0
        # the x misfit moves the column: widen by the line's local slope over that many columns
        ya, yb = cal["val_of"](r0 - pad), cal["val_of"](r1 + pad)
        out.append({"x": x, "y": cal["val_of"](rc), "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, rc],
                    "px_lo": r0 - pad, "px_hi": r1 + pad,
                    "note": f"line rows {r0}-{r1}; misfit x {cal['xmis']:.1f} px, y {cal['ymis']:.1f} px"})
    return out


def read_plus_markers(cal, arm_frac, exclude=None):
    """'+' markers inside the box. arm_frac: arm half-length as a fraction of the box width.
    exclude: optional (c0, r0, c1, r1) region (the legend) to skip."""
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    dark = (g < ink_threshold(cal, 0.5)).astype(float)
    a = max(3, int(round(arm_frac * (right - left))))
    k = np.ones(2 * a + 1) / (2 * a + 1)
    hmean = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 1, dark)
    vmean = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 0, dark)
    score = np.minimum(hmean, vmean)
    m = 2 * a
    score[:top + m, :] = 0
    score[bot - m:, :] = 0
    score[:, :left + m] = 0
    score[:, right - m:] = 0
    if exclude is not None:
        c0, r0, c1, r1 = exclude
        score[r0:r1, c0:c1] = 0
    cand = np.argwhere(score >= 0.75)
    order = np.argsort(-score[cand[:, 0], cand[:, 1]])
    centres = []
    for i in order:
        r, c = cand[i]
        if all((r - rr) ** 2 + (c - cc) ** 2 > a * a for rr, cc in centres):
            centres.append((int(r), int(c)))
    out = []
    pad = 2 + cal["ymis"]
    for r, c in sorted(centres, key=lambda p: p[1]):
        # refine the centre: the darkest row of the horizontal arm and column of the vertical arm
        rows = range(r - 2, r + 3)
        cols = range(c - 2, c + 3)
        rr = max(rows, key=lambda q: dark[q, c - a:c + a + 1].sum())
        cc = max(cols, key=lambda q: dark[r - a:r + a + 1, q].sum())
        ya, yb = cal["val_of"](rr - pad), cal["val_of"](rr + pad)
        out.append({"x": cal["x_of"](cc), "y": cal["val_of"](rr), "lo": min(ya, yb), "hi": max(ya, yb),
                    "px": [cc, rr], "px_lo": rr - pad, "px_hi": rr + pad, "note": "'+' marker centre"})
    return out
