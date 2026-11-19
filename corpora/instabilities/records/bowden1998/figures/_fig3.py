"""Fig. 3 (PDF p. 3): buckle wavelength (um) against the thickness ratio t1/t, two model curves.

Shared reading code for both curves (solid: E1/Ep = 4; dashed: E1/Ep = 2).

Calibration, all from the image:
- the plot frame is found as the long dark rows and columns (bottom, left);
- tick marks stand inward from the frame; the long ones are the labelled majors: on the x axis
  10, 20, 30, 40, 50 (left to right), on the y axis 5, 10, ..., 30 (bottom to top). A straight
  line is fitted through (pixel, label) for each axis and its residuals are kept as misfit.
Curves: both are black. Dark runs are collected column by column inside the frame, away from
the tick band. Each curve is followed from the right edge of the frame, where the solid curve is
the upper and the dashed curve the lower run, leftwards by taking in each column the run nearest
to the position extrapolated from the last points followed; a run much thicker than the line
(where an annotation arrow touches the curve or both curves merge near t1/t = 0) is not taken
as a centre and is marked ambiguous. Gaps (between dashes) are bridged up to a limit.
The value at x is the followed centre at that column, or the linear interpolation across a dash
gap. The 95% interval is the line half-thickness plus twice the y calibration rms, widened by
twice the x calibration rms times the local slope, and by the gap size times the slope where the
value is interpolated.
"""
import numpy as np


def _groups(idx):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= 1:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def _frame(dk):
    H, W = dk.shape
    rows = [r for r in range(H) if dk[r, int(0.2 * W):int(0.8 * W)].mean() > 0.8]
    cols = [c for c in range(W) if dk[int(0.2 * H):int(0.8 * H), c].mean() > 0.8]
    rg, cg = _groups(rows), _groups(cols)
    top, bottom = rg[0], rg[-1]
    left, right = cg[0], cg[-1]
    return top, bottom, left, right


def _ticks(dk, top, bottom, left, right):
    """Inward ticks: x ticks above the bottom frame, y ticks right of the left frame.
    Returns (centre, length) lists."""
    b0 = bottom[0] - 1
    band = dk[b0 - 20:b0, left[-1] + 2:right[0] - 2].mean(0)
    xt = []
    for g in _groups(np.where(band > 0.5)[0] + left[-1] + 2):
        c = (g[0] + g[-1]) // 2
        r, n = b0, 0
        while dk[r, c]:
            r -= 1
            n += 1
        xt.append(((g[0] + g[-1]) / 2, n))
    l0 = left[-1] + 1
    band = dk[top[-1] + 2:bottom[0] - 2, l0:l0 + 20].mean(1)
    yt = []
    for g in _groups(np.where(band > 0.5)[0] + top[-1] + 2):
        r = (g[0] + g[-1]) // 2
        c, n = l0, 0
        while dk[r, c]:
            c += 1
            n += 1
        yt.append(((g[0] + g[-1]) / 2, n))
    return xt, yt


def _majors(ticks):
    lens = np.array([n for _, n in ticks])
    short = np.median(lens)
    return [p for p, n in ticks if 1.4 * short < n < 4 * short]


def _fit(px, val):
    a, b = np.polyfit(px, val, 1)
    res = np.array(val) - (a * np.array(px) + b)
    return a, b, float(np.sqrt(np.mean(res ** 2)))


def calibrate(dk):
    top, bottom, left, right = _frame(dk)
    xt, yt = _ticks(dk, top, bottom, left, right)
    xm = _majors(xt)            # left to right: 10, 20, 30, 40, 50
    ym = _majors(yt)[::-1]      # bottom to top: 5, 10, ..., 30
    xv = [10.0 * (i + 1) for i in range(len(xm))]
    yv = [5.0 * (i + 1) for i in range(len(ym))]
    assert xv[-1] == 50 and yv[-1] == 30, (xm, ym)
    ax, bx, rx = _fit(xm, xv)
    ay, by, ry = _fit(ym, yv)
    return dict(top=top, bottom=bottom, left=left, right=right,
                ax=ax, bx=bx, rx=rx, ay=ay, by=by, ry=ry)


def _runs(col, r0, r1):
    idx = np.where(col[r0:r1])[0] + r0
    return [(g[0], g[-1]) for g in _groups(idx)]


def follow(dk, cal, which, max_gap=80, avoid=None):
    """Follow one curve from the right frame leftwards. which: 0 = upper (solid), 1 = lower (dashed).
    avoid: the other curve's followed points; a run on it is taken only where this curve's own
    extrapolation also lands on it (the two curves drawn over each other near t1/t = 0).
    Returns {column: (centre, half_thickness, ambiguous)}."""
    r0 = cal["top"][-1] + 45            # below the ticks of the top frame
    r1 = cal["bottom"][0] - 45          # above the x tick band
    cstart = cal["right"][0] - 45       # left of the ticks of the right frame
    cend = cal["left"][-1] + 4
    # start: the first column, from the right, with at least two thin runs
    c = cstart
    while True:
        runs = [r for r in _runs(dk[:, c], r0, r1) if 4 <= r[1] - r[0] < 40]
        if len(runs) >= 2:
            break
        c -= 1
    runs.sort()
    a, b = runs[which]
    lw = b - a + 1                      # this curve's own run thickness where it is followed from
    pts = {c: ((a + b) / 2, (b - a + 1) / 2, False)}
    hist = [(c, (a + b) / 2)]
    thicks = [lw]
    last = c
    for c in range(c - 1, cend, -1):
        if len(hist) >= 2:
            (c1, y1), (c2, y2) = hist[-1], hist[max(0, len(hist) - 120)]
            slope = (y1 - y2) / (c1 - c2) if c1 != c2 else 0.0
            pred = y1 + slope * (c - c1)
        else:
            pred = hist[-1][1]
        runs = _runs(dk[:, c], r0, r1)
        best = None
        for a, b in runs:
            centre = (a + b) / 2
            if len(thicks) > 60 and b - a + 1 < 0.5 * lw:
                continue                    # thinner than the line: an arrow shaft, a letter, a dash tip
            if abs(centre - pred) < 12 + 0.5 * (b - a) and (best is None or abs(centre - pred) < abs(best[0] - pred)):
                best = (centre, a, b)
        if best is None:
            if last - c > max_gap:
                break
            continue
        centre, a, b = best
        thick = b - a + 1
        thicks.append(thick)
        lw = np.median(thicks[:200])        # the line's run thickness, from the first columns followed
        on_other = avoid is not None and c in avoid and abs(avoid[c][0] - centre) < 0.3 * lw
        if len(thicks) > 60 and thick > 1.8 * lw:
            # an arrow or the other curve touches the line: keep the prediction, mark ambiguous
            pts[c] = (pred, thick / 2, True)
        elif on_other and abs(centre - pred) > 0.3 * lw:
            # in a dash gap the run found is the other curve, not where this one is heading
            pts[c] = (pred, thick / 2, True)
        else:
            pts[c] = (centre, thick / 2, False)
            hist.append((c, centre))
        last = c
    return pts, lw


def read_curve(image, at, which):
    gray = image.mean(axis=2) if image.ndim == 3 else image
    dk = gray < 128
    cal = calibrate(dk)
    avoid = follow(dk, cal, 0)[0] if which == 1 else None
    pts, lw = follow(dk, cal, which, avoid=avoid)
    cols = np.array(sorted(pts))
    out = []
    for x in at:
        x = float(x)
        col = (x - cal["bx"]) / cal["ax"]
        ci = int(round(col))
        note = f"x calibration rms {cal['rx']:.3f}, y rms {cal['ry']:.3f} um"
        if ci in pts and not pts[ci][2]:
            row, half, _ = pts[ci]
            gap = 0
        else:
            left = cols[cols < ci]
            right = cols[cols > ci]
            left = [c for c in left[::-1] if not pts[c][2]][:1]
            right = [c for c in right if not pts[c][2]][:1]
            if not left or not right or right[0] - left[0] > 120:
                out.append({"x": x, "y": None, "note": "no curve found near this column"})
                continue
            cl, cr = left[0], right[0]
            row = pts[cl][0] + (pts[cr][0] - pts[cl][0]) * (ci - cl) / (cr - cl)
            half = max(pts[cl][1], pts[cr][1])
            gap = cr - cl
            note += f"; interpolated across a gap of {gap} px"
        y = cal["ay"] * row + cal["by"]
        # local slope (um per px column) from followed points 30 px either side
        near = [c for c in cols if abs(c - ci) <= 30 and not pts[c][2]]
        if len(near) >= 2:
            sl = np.polyfit(near, [cal["ay"] * pts[c][0] for c in near], 1)[0]
        else:
            sl = 0.0
        dy_line = abs(cal["ay"]) * half
        dy = dy_line + 2 * cal["ry"] + abs(sl) * (2 * cal["rx"] / abs(cal["ax"])) + abs(sl) * gap * 0.25
        out.append({"x": x, "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [float(col), float(row)], "note": note})
    return out
