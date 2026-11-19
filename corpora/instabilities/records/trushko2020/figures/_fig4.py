"""Shared reading code for Fig. 4H and 4I (PDF p. 9), rendered at 1200 dpi.

Both panels are raster images inside the PDF, so lines are soft. Calibration, from the image only:
- dark grey pixels (all channels below 110, nearly neutral) make the axes; the x axis is the row
  with the longest dark run in the lower part of the crop, the y axis the column with the longest
  dark run in the left part;
- tick marks point outwards: x ticks are dark columns just below the x axis, y ticks dark rows
  just left of the y axis. They are equally spaced; the first x tick is the origin. The printed
  labels give the step: Fig. 4H x 0, 0.5, 1 on every second of five ticks (step 0.25), y 0, 20, 40
  on every second tick (step 10); Fig. 4I x 0, 100, 200 on every second of five ticks (step 50),
  y 0, 20, 40 (step 10). A line is fitted through (pixel, value) per axis; its rms misfit is kept.
Curves are found by colour (dark green, purple) column by column; markers (blue dots) as blobs.
"""
import numpy as np
from scipy import ndimage

GREEN = np.array([20, 85, 45])
PURPLE = np.array([105, 75, 165])
BLUE = np.array([30, 110, 190])


def _groups(idx):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= 1:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def _longest_run(v):
    best, cur = 0, 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def _indices(ticks):
    """Tick indices from the first (origin) tick, allowing for ticks too faint to be found: the
    spacing is the largest that makes every gap a whole number of spacings."""
    p = np.array(ticks, float)
    gaps = np.abs(np.diff(p))
    d = gaps.min()
    for k in range(1, 6):
        s = d / k
        if np.all(np.abs(gaps / s - np.round(gaps / s)) < 0.08):
            break
    return [int(round(abs(q - p[0]) / s)) for q in p]


def calibrate(image, xstep, ystep):
    im = image.astype(float)
    dark = (im.max(axis=2) < 150) & (im.max(axis=2) - im.min(axis=2) < 40)
    H, W = dark.shape
    rows = range(H // 2, H)
    xrow = max(rows, key=lambda r: _longest_run(dark[r]))
    cols = range(0, W // 2)
    ycol = max(cols, key=lambda c: _longest_run(dark[:, c]))
    # thickness of the axis lines
    xr = [r for r in range(xrow - 15, xrow + 16) if _longest_run(dark[r]) > 0.5 * _longest_run(dark[xrow])]
    yc = [c for c in range(ycol - 15, ycol + 16) if _longest_run(dark[:, c]) > 0.5 * _longest_run(dark[:, ycol])]
    xr0, xr1, yc0, yc1 = min(xr), max(xr), min(yc), max(yc)
    # x ticks: below the axis, from the y axis rightwards (labels lie further below)
    band = dark[xr1 + 4:xr1 + 14, :].mean(0) > 0.5
    band[:yc0 - 4] = False
    xt = [np.mean(g) for g in _groups(np.where(band)[0])]
    # y ticks: left of the axis, from the x axis upwards
    band = dark[:, yc0 - 14:yc0 - 4].mean(1) > 0.5
    band[xr1 + 4:] = False
    yt = [np.mean(g) for g in _groups(np.where(band)[0])]
    xt = sorted(xt)
    yt = sorted(yt, reverse=True)       # bottom to top
    xv = [xstep * i for i in _indices(xt)]
    yv = [ystep * i for i in _indices(yt)]
    ax, bx = np.polyfit(xt, xv, 1)
    ay, by = np.polyfit(yt, yv, 1)
    rx = float(np.sqrt(np.mean((np.array(xv) - (ax * np.array(xt) + bx)) ** 2)))
    ry = float(np.sqrt(np.mean((np.array(yv) - (ay * np.array(yt) + by)) ** 2)))
    return dict(xrow=xr0, ycol=yc1, ax=ax, bx=bx, ay=ay, by=by, rx=rx, ry=ry, xt=xt, yt=yt)


def mask(image, colour, tol=55.0):
    d = np.sqrt(((image.astype(float) - colour) ** 2).sum(axis=2))
    return d < tol


def _core(image, colour, m):
    """Keep only the runs of the colour mask whose mean colour is close to the curve's: the
    anti-aliased rims of the blue dots come close to the purple, but not on average (used for the
    purple curve only; the green is far from the blue)."""
    d = np.sqrt(((image.astype(float) - colour) ** 2).sum(axis=2))
    out = np.zeros_like(m)
    for c in range(m.shape[1]):
        for g in _groups(np.where(m[:, c])[0]):
            if np.mean(d[g, c]) < 35:
                out[g, c] = True
    return out


def read_curve(image, at, colour, xstep, ystep, pick="top", core=False):
    cal = calibrate(image, xstep, ystep)
    m = mask(image, colour)
    if core:
        m = _core(image, colour, m)
    out = []
    for x in at:
        x = float(x)
        col = (x - cal["bx"]) / cal["ax"]
        ci = int(round(col))
        idx = np.where(m[:cal["xrow"] - 3, ci])[0]
        runs = [g for g in _groups(idx) if len(g) >= 3]
        if not runs:
            out.append({"x": x, "y": None, "note": "no curve of that colour in this column"})
            continue
        g = runs[0] if pick == "top" else runs[-1]
        row = (g[0] + g[-1]) / 2
        half = (g[-1] - g[0] + 1) / 2
        # local slope from neighbouring columns
        rs = []
        for c in (ci - 15, ci + 15):
            i2 = np.where(m[:cal["xrow"] - 3, c])[0]
            r2 = [h for h in _groups(i2) if len(h) >= 3]
            if r2:
                h = r2[0] if pick == "top" else r2[-1]
                rs.append((c, (h[0] + h[-1]) / 2))
        slope = abs((rs[1][1] - rs[0][1]) / (rs[1][0] - rs[0][0])) if len(rs) == 2 else 0.0
        y = cal["ay"] * row + cal["by"]
        # the line is drawn thicker where it is steep: the centre is known to half the vertical run
        # divided by the slope factor, but keep the full half-run as a safe bound
        dy = abs(cal["ay"]) * (half + 2) + 2 * cal["ry"] + abs(cal["ay"]) * slope * (2 * cal["rx"] / abs(cal["ax"]) + 2)
        out.append({"x": x, "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [float(col), float(row)], "px_lo": float(row + dy / abs(cal["ay"])),
                    "px_hi": float(row - dy / abs(cal["ay"])),
                    "note": f"x rms {cal['rx']:.4g}, y rms {cal['ry']:.4g}; line half-run {half:.1f} px"})
    return out


def read_markers(image, colour, xstep, ystep, top_exclude):
    """Blue dots inside the plot (the legend dot, above `top_exclude` of the plot height, is left out).
    A blob about twice the median area is two overlapping dots: it is split along its long axis."""
    cal = calibrate(image, xstep, ystep)
    m = mask(image, colour, tol=70.0)
    m[cal["xrow"] - 2:, :] = False
    m[:, :cal["ycol"] + 2] = False
    lab, n = ndimage.label(m)
    blobs = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        if len(rr) < 200:
            continue
        blobs.append((rr, cc))
    areas = np.array([len(b[0]) for b in blobs])
    med = float(np.median(areas))
    rad = np.sqrt(med / np.pi)
    pts = []
    for rr, cc in blobs:
        k = int(round(len(rr) / med))
        cr, cc0 = rr.mean(), cc.mean()
        if cr < top_exclude * cal["xrow"]:
            continue                   # the legend
        if k <= 1:
            pts.append((cc0, cr, 1))
            continue
        X = np.stack([cc - cc0, rr - cr], axis=1)
        w, v = np.linalg.eigh(X.T @ X)
        u = v[:, -1]
        proj = X @ u
        L = proj.max() - proj.min()
        for j in range(k):
            t = -L / 2 + rad + j * (L - 2 * rad) / (k - 1)
            pts.append((cc0 + t * u[0], cr + t * u[1], k))
    pts.sort()
    out = []
    for col, row, k in pts:
        x = cal["ax"] * col + cal["bx"]
        y = cal["ay"] * row + cal["by"]
        e = 3.0 if k == 1 else rad / 2      # centre of a dot; of a dot split from an overlap
        dx = abs(cal["ax"]) * e + 2 * cal["rx"]
        dy = abs(cal["ay"]) * e + 2 * cal["ry"]
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [float(col), float(row)],
                    "note": ("split from an overlap of %d dots; " % k if k > 1 else "")
                    + f"x +- {dx:.3g}"})
    return out
