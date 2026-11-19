"""Fig. 4 right (p. 3): the deformed mantle shape, height y against position x, the grey curve.

Calibration comes from the image: the axes are the longest black lines (the y axis stands at x = 0.5).
Major x ticks (black, the longer marks above the x axis) are matched to the printed labels
0.0, 0.2, ..., 1.0 (the y axis column itself is skipped). Major y ticks (black, right of the y axis)
are at equal spacing; the two labelled ones are 0.2 and 0.4, so the four are 0.1, 0.2, 0.3, 0.4 from
the bottom; the fit misfit checks the equal spacing. The curve is grey (~93 solid, ~122 dashed), told
apart from black axes, ticks and annotations by grey level.
"""

import numpy as np


def _runs(idx):
    if len(idx) == 0:
        return []
    cuts = np.where(np.diff(idx) > 1)[0] + 1
    return np.split(idx, cuts)


def _calibrate(g):
    black = g < 60
    ycol = int(np.argmax(black.sum(0)))
    xrow = int(np.argmax(black.sum(1)))
    xt = [r.mean() for r in _runs(np.where(black[xrow - 20])[0]) if abs(r.mean() - ycol) > 5]
    yt = [r.mean() for r in _runs(np.where(black[: xrow - 5, ycol + 20])[0])]
    xlab = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0][: len(xt)]
    yt = sorted(yt)  # top first
    ylab = [0.4, 0.3, 0.2, 0.1][: len(yt)]
    ax, bx = np.polyfit(xt, xlab, 1)
    ay, by = np.polyfit(yt, ylab, 1)
    mx = float(np.max(np.abs(np.polyval([ax, bx], xt) - xlab)))
    my = float(np.max(np.abs(np.polyval([ay, by], yt) - ylab)))
    return xrow, (ax, bx), (ay, by), mx, my, len(xt), len(yt)


def read(image, at):
    g = image[..., :3].mean(axis=2)
    xrow, (ax, bx), (ay, by), mx, my, nx, ny = _calibrate(g)
    grey = (g > 80) & (g < 135)
    out = []
    for xv in at:
        c = int(round((xv - bx) / ax))
        found = None
        for dc in (0, -1, 1, -2, 2, -3, 3, -4, 4, -6, 6, -8, 8):
            rows = np.where(grey[:, c + dc])[0]
            runs = [r for r in _runs(rows) if len(r) >= 3]
            if len(runs) == 1:
                found = (c + dc, runs[0])
                break
        if found is None:
            out.append({"x": xv, "y": None, "note": "no single grey curve run in this column (gap, axis or annotation)"})
            continue
        cc, run = found
        rmid = float(run.mean())
        y = float(np.polyval([ay, by], rmid))
        half = 0.5 * (run[-1] - run[0] + 1)
        dy = abs(ay) * half + my + abs(ay) * 1.0
        if cc != c:
            dy += abs(ay) * abs(cc - c) * max(1.0, (run[-1] - run[0] + 1) / 6.0)
        out.append({
            "x": xv, "y": y, "lo": y - dy, "hi": y + dy,
            "px": [cc, rmid], "px_lo": float(run[0]), "px_hi": float(run[-1]),
            "note": f"{nx} x ticks (misfit {mx:.4f}), {ny} y ticks (misfit {my:.4f})",
        })
    return out
