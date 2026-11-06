"""Shared reading code for the waveform figures of Chapter 5 (Figs. 5-3 to 5-6, PDF pp. 8-11).

Each figure is an embedded raster, black on white, resampled when the page is rendered (its own
pixels show as steps of about 6 px at 900 dpi). Ink is darker than halfway between the paper
and the darkest pixel. Every crop lies inside the figure's outer frame.

Calibration, all from the image:
- the y axis is the column (left third) with the most ink, the x axis the row (lower half) with
  the most ink; each line is a few pixels thick and its centre is used;
- tick marks point inwards from both axes. Every short run of ink leaving the axis is a
  candidate; the labelled (major) ticks are the long ones (over 1.5 times the median candidate,
  the minor ticks being the majority), kept as the longest evenly spaced chain (a curve touching
  the axis is not evenly spaced). They are matched in order to the printed labels each reading
  names (bottom to top, left to right). Where the axis corner itself carries a label, the other
  axis's centre line is that mark;
- a straight line is fitted to each axis's marks; its largest misfit (px) widens every interval;
  a misfit over 8 px raises an error (a label on the wrong tick).
"""

import numpy as np
from scipy import ndimage

BLUR = 6.0  # px at 900 dpi: about one pixel of the embedded raster


def ink_mask(image):
    g = image[..., :3].astype(float).mean(axis=2)
    thr = (np.percentile(g, 99) + g.min()) / 2.0
    return g < thr


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def axes_lines(ink):
    H, W = ink.shape
    cs = ink[:, : W // 3].sum(axis=0)
    ycols = np.flatnonzero(cs > 0.85 * cs.max())
    yl, yr = int(ycols.min()), int(ycols.max()) + 1
    rs = ink[H // 2:, :].sum(axis=1)
    xrows = np.flatnonzero(rs > 0.85 * rs.max()) + H // 2
    xt, xb = int(xrows.min()), int(xrows.max()) + 1
    yc, xc = (yl + yr - 1) / 2.0, (xt + xb - 1) / 2.0
    col = ink[:, int(round(yc))]
    top = min(a for a, b in _runs(col) if b >= xt)
    row = ink[int(round(xc)), :]
    right = max(b for a, b in _runs(row) if a <= yr)
    return dict(yl=yl, yr=yr, xt=xt, xb=xb, yc=yc, xc=xc, top=top, right=right)


def _cands(lengths, offset, min_len=8):
    out = []
    for a, b in _runs(lengths >= min_len):
        if b - a > 40:
            continue
        out.append(((a + b - 1) / 2.0 + offset, int(lengths[a:b].max())))
    return out


def tick_candidates(ink, ax):
    H, W = ink.shape
    ylen = []
    for r in range(ax["top"], ax["xt"]):
        n = 0
        while ax["yr"] + n < W and ink[r, ax["yr"] + n]:
            n += 1
        ylen.append(n)
    xlen = []
    for c in range(ax["yr"], min(ax["right"] + 6, W)):
        n = 0
        while ax["xt"] - 1 - n >= 0 and ink[ax["xt"] - 1 - n, c]:
            n += 1
        xlen.append(n)
    return _cands(np.array(ylen), ax["top"]), _cands(np.array(xlen), ax["yr"])


def _majors(cands):
    L = 1.5 * float(np.median([l for _, l in cands]))
    c = sorted(p for p, l in cands if l > L)
    gaps = [b - a for a, b in zip(c, c[1:]) if b - a > 100]
    d = float(np.median(gaps))
    best = []
    for s in c:
        chain = [s]
        while True:
            nxt = [p for p in c if abs(p - chain[-1] - d) <= 0.12 * d]
            if not nxt:
                break
            chain.append(min(nxt, key=lambda p: abs(p - chain[-1] - d)))
        if len(chain) > len(best):
            best = chain
    return best


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    if mis > 8.0:
        raise RuntimeError(f"calibration misfit {mis:.1f} px: {marks}")
    return a, b, mis


def calibrate(image, ylabels, xlabels, y_corner=None, x_corner=None):
    ink = ink_mask(image)
    ax = axes_lines(ink)
    yt, xt = tick_candidates(ink, ax)
    ym = _majors([q for q in yt if q[0] < ax["xt"] - 15])[::-1]  # bottom to top
    xm = _majors([q for q in xt if q[0] > ax["yr"] + 15])
    if len(ym) != len(ylabels) or len(xm) != len(xlabels):
        raise RuntimeError(f"major ticks: y {ym} for {ylabels}; x {xm} for {xlabels}")
    ymarks = list(zip(ym, ylabels))
    xmarks = list(zip(xm, xlabels))
    if y_corner is not None:
        ymarks.append((ax["xc"], y_corner))
    if x_corner is not None:
        xmarks.append((ax["yc"], x_corner))
    ya, yb, ymis = _fit(ymarks)
    xa, xb, xmis = _fit(xmarks)
    return dict(ax=ax, ink=ink, xa=xa, xb=xb, xmis=xmis, ya=ya, yb=yb, ymis=ymis)


def to_col(cal, x):
    return (x - cal["xa"]) / cal["xb"]


def yval(cal, row):
    return cal["ya"] + cal["yb"] * row


def xval(cal, col):
    return cal["xa"] + cal["xb"] * col


def interior(cal, legend_box=None):
    """Ink inside the plot, without the axes and their ticks (at most ~45 px long), and
    without an optional legend box (c0, r0, c1, r1)."""
    ax = cal["ax"]
    m = cal["ink"].copy()
    m[:, : ax["yr"] + 50] = False
    m[ax["xt"] - 50:, :] = False
    m[: ax["top"] + 2, :] = False
    m[:, ax["right"] + 2:] = False
    if legend_box is not None:
        c0, r0, c1, r1 = legend_box
        m[r0:r1, c0:c1] = False
    return m


def largest_piece(mask):
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if n == 0:
        return mask
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    return lab == (int(np.argmax(sizes)) + 1)


def _value(cal, x, col, row, half, slope, note):
    e = half + BLUR + cal["ymis"] + abs(slope) * cal["xmis"]
    return {"x": x, "y": yval(cal, row), "lo": yval(cal, row + e), "hi": yval(cal, row - e),
            "px": [float(col), float(row)], "px_lo": row - e, "px_hi": row + e, "note": note}


def read_single_curve(image, at, ylabels, xlabels, y_corner=None, x_corner=None):
    """A panel with one solid curve: the largest connected piece of ink inside the plot. At each
    x, the centre of its single run of ink in that column; the interval is half the run (a steep
    stretch gives a tall run), one raster pixel, the y calibration misfit and the x misfit times
    the local slope (px per px). Refused where the column holds more than one run."""
    cal = calibrate(image, ylabels, xlabels, y_corner, x_corner)
    curve = largest_piece(interior(cal))
    out = []
    for x in at:
        x = float(x)
        col = to_col(cal, x)
        c = int(round(col))
        if c < 0 or c >= curve.shape[1]:
            out.append({"x": x, "y": None, "note": "outside the crop"})
            continue
        runs = _runs(curve[:, c])
        if len(runs) != 1:
            out.append({"x": x, "y": None, "note": f"{len(runs)} runs of the curve in this column"})
            continue
        a, b = runs[0]
        nb = [np.mean(_runs(curve[:, k])[0]) for k in (c - 8, c + 8)
              if 0 <= k < curve.shape[1] and len(_runs(curve[:, k])) == 1]
        slope = abs(nb[1] - nb[0]) / 16.0 if len(nb) == 2 else 0.0
        out.append(_value(cal, x, col, (a + b - 1) / 2.0, (b - a) / 2.0, slope, f"curve run {b - a} px"))
    return out


def read_outermost(image, at, ylabels, xlabels, y_corner=None, x_corner=None, top=True,
                   legend_box=None, window=12, clear=25):
    """A broken (dotted, dashed or dash-dot) curve where it is the highest (top=True) or lowest
    ink of the plot: at each x, over the columns within `window` px either side (a dot or dash
    may miss the column itself), the outermost run of ink of each column; the most outer of those
    is read, at its centre. The interval adds half the run, one raster pixel, the calibration
    misfits and the change of the outermost row across the window (the shift of up to `window`
    px in x). Refused where another run of ink lies within `clear` px of the one read (the
    curve is not apart from the others), or where the window holds no ink."""
    cal = calibrate(image, ylabels, xlabels, y_corner, x_corner)
    m = interior(cal, legend_box)
    out = []
    for x in at:
        x = float(x)
        col = to_col(cal, x)
        c = int(round(col))
        best = None
        rows_seen = []
        for k in range(max(c - window, 0), min(c + window + 1, m.shape[1])):
            rr = _runs(m[:, k])
            if not rr:
                continue
            a, b = rr[0] if top else rr[-1]
            rows_seen.append((a + b - 1) / 2.0)
            score = -a if top else b
            if best is None or score > best[0]:
                best = (score, k, a, b, rr)
        if best is None:
            out.append({"x": x, "y": None, "note": "no ink within the window"})
            continue
        _, k, a, b, rr = best
        others = [q for q in rr if q != (a, b)]
        gap = min([min(abs(q[0] - b), abs(a - q[1])) for q in others], default=1e9)
        if gap < clear:
            out.append({"x": x, "y": None, "note": f"another run {gap} px away: not apart from the other curves"})
            continue
        row = (a + b - 1) / 2.0
        # the same curve's rows across the window (outermost runs within 40 px of the one read;
        # farther ones belong to another curve, seen through a gap between dots)
        near = [r for r in rows_seen if abs(r - row) < 40]
        spread = (max(near) - min(near)) / 2.0
        e = (b - a) / 2.0 + BLUR + cal["ymis"] + spread
        out.append({"x": x, "y": yval(cal, row), "lo": yval(cal, row + e), "hi": yval(cal, row - e),
                    "px": [float(k), float(row)], "px_lo": row - e, "px_hi": row + e,
                    "note": f"{'highest' if top else 'lowest'} ink, column {k - c:+d} px from x, run {b - a} px"})
    return out


def read_extreme(image, ylabels, xlabels, y_corner=None, x_corner=None, top=True, window=None):
    """One point: the highest (top=True) or lowest ink of the single curve, optionally within an
    x window (x0, x1) in axis units, at the line's centre (half the usual line thickness inside the
    outermost ink). x is the mean column of the ink in that extreme band of 4 rows."""
    cal = calibrate(image, ylabels, xlabels, y_corner, x_corner)
    curve = largest_piece(interior(cal))
    if window is not None:
        c0, c1 = int(round(to_col(cal, window[0]))), int(round(to_col(cal, window[1])))
        m = np.zeros_like(curve)
        m[:, max(c0, 0):c1] = curve[:, max(c0, 0):c1]
        curve = m
    hs = [b - a for c in range(0, curve.shape[1], 7) for a, b in _runs(curve[:, c])]
    th = float(np.median(hs)) if hs else 8.0
    rows = np.flatnonzero(curve.any(axis=1))
    r = int(rows.min()) if top else int(rows.max())
    band = curve[r: r + 4] if top else curve[r - 3: r + 1]
    cols = np.flatnonzero(band.any(axis=0))
    half = th / 2.0
    row = r + half - 0.5 if top else r - half + 0.5
    col = float(cols.mean())
    x = xval(cal, col)
    return [_value(cal, x, col, row, half, 0.0,
                   f"{'highest' if top else 'lowest'} ink at row {r}; x read as {x:.4g} over "
                   f"columns {cols.min()}-{cols.max()}")]
