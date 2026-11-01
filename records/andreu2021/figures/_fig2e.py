"""Shared reading code for the model lines (black) of Fig. 2e, Andreu et al. 2021 (PDF p. 4).

Each panel of Fig. 2e is a raster plot with a left axis (YAP Nuc/Cyt), a right axis
(adhesion length, um: ticks 0, 1, 2, 3) and a log frequency axis with ticks for
Ns, then (after an axis break //) 0.125, 0.25, 0.5, 1 and 2 Hz.

Method, all from the image:
- axes: the bottom axis is the longest dark horizontal row; the left and right axes are
  the two longest dark vertical columns;
- x calibration: tick marks are dark columns just below the bottom axis that do not
  continue above it (the two break marks // do); the first tick is Ns (categorical) and is
  skipped; the other five are matched to 0.125, 0.25, 0.5, 1, 2 Hz and fitted as a straight
  line in log2(f); the misfit is reported;
- y calibration: tick marks to the right of the right axis, matched to 0, 1, 2, 3 um
  from the bottom up, fitted as a straight line; the misfit is reported;
- the model line: near-black, unsaturated pixels inside the plot box. It is traced column
  by column from the right axis leftwards, each column taking the dark run nearest to the
  line found in the columns just to its right (legend text and the legend line are far from
  it). At a requested frequency the value is the centre of the traced run there, averaged
  over +-3 columns; where the line is hidden behind a marker the trace is interpolated
  between the nearest traced columns on each side, and the note says so;
- 95% interval: half the vertical extent of the dark run (line thickness, which also grows
  where the line is steep) plus two pixels, plus twice the y-calibration misfit.
"""
import numpy as np

X_LABELS = [0.125, 0.25, 0.5, 1.0, 2.0]   # printed tick labels after the break (Hz)
Y_LABELS = [0.0, 1.0, 2.0, 3.0]           # printed right-axis labels (um), bottom up


def _dark(img):
    rgb = img[..., :3].astype(float)
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    return (mx < 120) & (mx - mn < 45)


def _runs(mask_1d):
    """Start/end (inclusive) of True runs."""
    m = np.concatenate([[False], mask_1d, [False]]).astype(int)
    d = np.diff(m)
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1))


def _groups(idx, gap=3):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return [float(np.mean(g)) for g in out]


def calibrate(img):
    dk = _dark(img)
    h, w = dk.shape
    # bottom axis: the row with the longest dark run in the lower half
    best = (0, None)
    for r in range(h // 2, h):
        for a, b in _runs(dk[r]):
            if b - a > best[0]:
                best = (b - a, (r, a, b))
    _, (r_axis, xa, xb) = best
    rows = [r for r in range(max(0, r_axis - 15), min(h, r_axis + 15))
            if dk[r, (xa + xb) // 2 - 50:(xa + xb) // 2 + 50].mean() > 0.9]
    y_axis_top, y_axis_bot = min(rows), max(rows)
    # left and right axes: columns dark over most of the height above the bottom axis
    colfrac = dk[: y_axis_top, :].mean(axis=0)
    tall = np.flatnonzero(colfrac > 0.55)
    cols = _groups(tall, gap=4)
    x_left, x_right = cols[0], cols[-1]
    # bottom ticks: dark just below the axis, not dark just above it
    below = dk[y_axis_bot + 6: y_axis_bot + 30, :].mean(axis=0) > 0.6
    above = dk[y_axis_top - 30: y_axis_top - 6, :].mean(axis=0) > 0.3
    tick_cols = np.flatnonzero(below & ~above)
    cands = [t for t in _groups(tick_cols, gap=3) if x_left - 5 < t < x_right + 5]
    # the five frequency ticks are the rightmost five candidates, equally spaced (log axis);
    # Ns is the leftmost; anything between them is a break mark //
    if len(cands) < 6:
        raise RuntimeError(f"expected Ns + break + 5 ticks, found {cands}")
    tx = np.array(cands[-5:])
    sp = np.diff(tx)
    if sp.max() - sp.min() > 0.05 * sp.mean():
        raise RuntimeError(f"frequency ticks not equally spaced: {tx}")
    ticks = [cands[0]] + list(tx)
    pair = cands[1:-5]
    lx = np.log2(X_LABELS)
    ax, bx = np.polyfit(lx, tx, 1)
    x_misfit = float(np.sqrt(np.mean((np.polyval([ax, bx], lx) - tx) ** 2)))
    # right ticks: dark just right of the right axis
    xr = int(round(x_right))
    right = dk[:, xr + 8: xr + 30].mean(axis=1) > 0.6
    ty = np.array([t for t in _groups(np.flatnonzero(right), gap=3)])
    if len(ty) != 4:
        raise RuntimeError(f"expected 4 right-axis ticks, found {len(ty)} at {ty}")
    ty = np.sort(ty)[::-1]  # bottom (0) first
    ay, by = np.polyfit(Y_LABELS, ty, 1)
    y_misfit = float(np.sqrt(np.mean((np.polyval([ay, by], Y_LABELS) - ty) ** 2)))
    break_cols = [t for t in np.flatnonzero(below & above) if t < tx[0]] + [t for t in pair if t < tx[0]]
    x_break = float(max(break_cols)) if break_cols else float(tx[0] - 20)
    return dict(dk=dk, x_left=x_left, x_right=x_right, y_axis_top=y_axis_top, ax=ax, bx=bx, ay=ay, by=by,
                x_misfit=x_misfit, y_misfit=y_misfit, x_break=x_break, ticks=ticks, yticks=list(ty))


def trace(cal):
    dk = cal["dk"]
    top = 5
    bot = cal["y_axis_top"] - 3
    x0 = int(cal["x_break"]) + 8
    x1 = int(round(cal["x_right"])) - 8
    path = {}
    prev = None
    for x in range(x1, x0 - 1, -1):
        runs = [(a + top, b + top) for a, b in _runs(dk[top:bot, x]) if 3 <= b - a <= 160]
        if not runs:
            continue
        if prev is None:
            # start: the lowest-lying run of plausible thickness at the right edge
            a, b = max(runs, key=lambda r: r[0])
        else:
            a, b = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - prev))
            if abs((a + b) / 2 - prev) > 40:
                continue  # hidden here (marker on top); leave a gap
        path[x] = (a, b)
        prev = (a + b) / 2
    return path


def read(image, at):
    img = np.asarray(image)
    cal = calibrate(img)
    path = trace(cal)
    xs = np.array(sorted(path))
    out = []
    for f in at:
        col = cal["ax"] * np.log2(f) + cal["bx"]
        near = [x for x in range(int(round(col)) - 3, int(round(col)) + 4) if x in path]
        note = f"x ticks misfit {cal['x_misfit']:.1f} px, y ticks misfit {cal['y_misfit']:.1f} px"
        if near:
            c = np.mean([(path[x][0] + path[x][1]) / 2 for x in near])
            half = np.mean([(path[x][1] - path[x][0]) / 2 for x in near])
        else:
            left = xs[xs < col]
            rightx = xs[xs > col]
            if not len(left) or not len(rightx):
                out.append({"x": f, "y": None, "note": "line not found here"})
                continue
            xl, xr = left.max(), rightx.min()
            cl = (path[xl][0] + path[xl][1]) / 2
            cr = (path[xr][0] + path[xr][1]) / 2
            c = cl + (cr - cl) * (col - xl) / (xr - xl)
            half = max((path[xl][1] - path[xl][0]) / 2, (path[xr][1] - path[xr][0]) / 2) + abs(cr - cl) / 2
            note += f"; line hidden over columns {xl + 1}-{xr - 1}, interpolated"
        y = (c - cal["by"]) / cal["ay"]
        dy = (half + 2 + 2 * cal["y_misfit"]) / abs(cal["ay"])
        out.append({"x": f, "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [float(col), float(c)], "px_lo": float(c - half), "px_hi": float(c + half), "note": note})
    return out
