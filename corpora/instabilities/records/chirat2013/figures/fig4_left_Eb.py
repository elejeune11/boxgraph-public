"""Fig. 4 left (p. 3): the bending-stiffness profile Eb(s0), the grey curve (solid, dashed near the middle).

Calibration comes from the image: the axes are the longest black lines; the major tick marks are
black (grey level ~35), the curve is grey (~93 solid, ~122 dashed), so ticks and curve are told apart
by grey level. Major x ticks are matched to the printed labels 0.2, 0.4, 0.6, 0.8, 1.0, major y ticks
to 0.5 ... 1.0, each by a straight-line fit whose misfit is reported.
"""

import numpy as np


def _runs(idx):
    """Split sorted indices into runs of consecutive values."""
    if len(idx) == 0:
        return []
    cuts = np.where(np.diff(idx) > 1)[0] + 1
    return np.split(idx, cuts)


def _calibrate(g):
    black = g < 60
    ycol = int(np.argmax(black.sum(0)))  # the y axis: the longest black column
    xrow = int(np.argmax(black.sum(1)))  # the x axis: the longest black row
    # major x ticks: black above the x axis, reaching 20 px up (minor ticks are shorter)
    probe = xrow - 20
    xt = [r.mean() for r in _runs(np.where(black[probe, ycol + 5:])[0] + ycol + 5)]
    # major y ticks: black right of the y axis, reaching 22 px out
    yt = [r.mean() for r in _runs(np.where(black[: xrow - 5, ycol + 22])[0])]
    xlab = [0.2, 0.4, 0.6, 0.8, 1.0][: len(xt)]
    ylab = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0][::-1][-len(yt):]  # from the bottom: 0.5 is the lowest tick
    yt = sorted(yt)
    ax, bx = np.polyfit(xt, xlab, 1)
    ay, by = np.polyfit(yt, ylab, 1)
    mx = float(np.max(np.abs(np.polyval([ax, bx], xt) - xlab)))
    my = float(np.max(np.abs(np.polyval([ay, by], yt) - ylab)))
    return ycol, xrow, (ax, bx), (ay, by), mx, my, len(xt), len(yt)


def read(image, at):
    g = image[..., :3].mean(axis=2)
    ycol, xrow, (ax, bx), (ay, by), mx, my, nx, ny = _calibrate(g)
    grey = (g > 80) & (g < 135)
    out = []
    for xv in at:
        c = int(round((xv - bx) / ax))
        # centres of the single grey run in each column within 12 px; in the dashed part a column that cuts
        # the end of a dash gives a truncated run, so only runs at least 80% of the longest are kept
        cols = []
        for cc in range(c - 12, c + 13):
            rows = np.where(grey[: xrow - 3, cc])[0]
            runs = [r for r in _runs(rows) if len(r) >= 3]
            if len(runs) == 1:
                cols.append((cc, float(runs[0].mean()), len(runs[0]), int(runs[0][0]), int(runs[0][-1])))
        if len(cols) < 3:
            out.append({"x": xv, "y": None, "note": "no single grey curve run near this column (gap or annotation)"})
            continue
        longest = max(k[2] for k in cols)
        keep = [k for k in cols if k[2] >= 0.8 * longest]
        cc_ = np.array([k[0] for k in keep], float)
        mid = np.array([k[1] for k in keep])
        deg = 2 if len(keep) >= 5 else 1
        p = np.polyfit(cc_ - c, mid, deg)
        rmid = float(np.polyval(p, 0.0))
        resid = float(np.max(np.abs(np.polyval(p, cc_ - c) - mid)))
        y = float(np.polyval([ay, by], rmid))
        # 95% interval: half the line's vertical extent, the fit residual, one pixel, calibration misfit
        half = 0.5 * float(np.median([k[2] for k in keep]))
        dy = abs(ay) * (half + resid + 1.0) + my
        out.append({
            "x": xv, "y": y, "lo": y - dy, "hi": y + dy,
            "px": [c, rmid], "px_lo": rmid - half, "px_hi": rmid + half,
            "note": f"{len(keep)} columns; {nx} x ticks (misfit {mx:.4f}), {ny} y ticks (misfit {my:.4f})",
        })
    return out
