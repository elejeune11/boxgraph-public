"""Fig. 3D (PDF p. 4): the six measured means (coloured squares) with their error bars.

Calibration, all from the image:
  y: the plot box top (120) and bottom (60) and the faint dashed gridlines at
     110 ... 70, found as minima of the median grey profile across the plot;
  x (log10): the box edges carry 0.1 and 100; the label blobs "1" and "10"
     under the axis are matched to the decades between (checked, not fitted alone).
Markers: pixels clearly coloured (saturation > 50, not the pale blue band), in
connected blobs of a marker's size; the centroid is the point. The legend's
marker lies below the 70 nm/s gridline, where no data point lies, and is dropped.
Error bars: thin dark vertical lines through each marker, ending in short caps.
Going up and down from the marker along its column, the bar ends where the
darkness stops; the cap is the darkest horizontal stroke within a few pixels of
that end, and its centre row is the bar's end.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.ndimage import uniform_filter1d

Y_LABELS = [120.0, 110.0, 100.0, 90.0, 80.0, 70.0, 60.0]   # matched: the y labels, top to bottom
X_LABELS = [0.1, 1.0, 10.0, 100.0]                          # matched: the x labels, left to right


def _minima(prof, depth, win=41):
    base = uniform_filter1d(prof, win)
    d = base - prof
    out = []
    for i in range(3, len(prof) - 3):
        if d[i] > depth and d[i] == d[i - 2:i + 3].max():
            w = np.clip(d[i - 3:i + 4], 0, None)
            out.append(((np.arange(i - 3, i + 4) * w).sum() / w.sum(), d[i]))
    return out


def _calibrate(img):
    f = img.astype(float)
    g = f.mean(axis=2)
    h, w = g.shape
    # box: the strongest row minima near top and bottom, the strongest column minima at the sides
    rows = _minima(np.median(g[:, int(0.4 * w):int(0.55 * w)], axis=1), 3)
    top = min((r for r, d in rows if d > 12), key=lambda r: r)
    bottom = max((r for r, d in rows if d > 20 and r < 0.95 * h), key=lambda r: r)
    cols = _minima(np.median(g[int(top) + 20:int(bottom) - 20], axis=0), 3)
    left = max((t for t in cols if t[0] < w / 3), key=lambda t: t[1])[0]
    right = max((t for t in cols if t[0] > 2 * w / 3), key=lambda t: t[1])[0]
    # y: gridlines near their expected rows
    step = (bottom - top) / (len(Y_LABELS) - 1)
    marks = [(top, Y_LABELS[0]), (bottom, Y_LABELS[-1])]
    for k in range(1, len(Y_LABELS) - 1):
        want = top + k * step
        near = [r for r, d in rows if abs(r - want) < 0.08 * step]
        if near:
            marks.append((min(near, key=lambda r: abs(r - want)), Y_LABELS[k]))
    M = np.array(marks)
    by, ay = np.polyfit(M[:, 1], M[:, 0], 1)
    misfit_y = float(np.max(np.abs(M[:, 0] - (ay + by * M[:, 1]))))
    # x: box edges carry the end labels; label blobs check the inner decades
    lab = (g[int(bottom) + 40:int(bottom) + 140] < 150).any(axis=0)
    on = np.where(lab)[0]
    blobs = [b for b in np.split(on, np.where(np.diff(on) > 30)[0] + 1) if len(b)]
    centers = [(b[0] + b[-1]) / 2.0 for b in blobs]
    xm = [(left, np.log10(X_LABELS[0])), (right, np.log10(X_LABELS[-1]))]
    if len(centers) == len(X_LABELS):
        for c, v in zip(centers[1:-1], X_LABELS[1:-1]):
            xm.append((c, np.log10(v)))
    X = np.array(xm)
    bx, ax = np.polyfit(X[:, 1], X[:, 0], 1)
    misfit_x = float(np.max(np.abs(X[:, 0] - (ax + bx * X[:, 1]))))
    return dict(ay=ay, by=by, ax=ax, bx=bx, misfit_y=misfit_y, misfit_x=misfit_x, n_y=len(M), n_x=len(X),
                top=top, bottom=bottom, left=left, right=right, y70=ay + by * 70.0)


def _markers(img, cal):
    f = img.astype(float)
    sat = f.max(axis=2) - f.min(axis=2)
    m = (sat > 50) & (f.mean(axis=2) < 190)
    m[:int(cal["top"]) + 3] = False
    m[int(cal["bottom"]) - 3:] = False
    m[:, :int(cal["left"]) + 3] = False
    m[:, int(cal["right"]) - 3:] = False
    m = ndi.binary_opening(m, iterations=2)
    lab, n = ndi.label(m)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        if len(rr) < 400:
            continue
        r, c = rr.mean(), cc.mean()
        if r > cal["y70"]:
            continue                                  # the legend's marker
        half = 0.5 * np.sqrt(len(rr))
        out.append((c, r, half))
    return sorted(out)


def _bar_end(g, c, r0, direction, half):
    """Row of the cap ending the error bar from the marker edge r0, going up (-1) or down (+1)."""
    ci = int(round(c))
    # darkness of the 21 columns around the bar against its flanks, row by row: a line
    # crossing the whole neighbourhood (gridline, dashed curve) cancels; the bar adds a
    # little, its cap a lot
    # the brighter flank, so a sloping line passing one side does not hide the bar
    flank = np.maximum(g[:, ci - 26:ci - 14].mean(axis=1), g[:, ci + 15:ci + 27].mean(axis=1))
    wide = flank - g[:, ci - 10:ci + 11].mean(axis=1)
    r = int(r0 + direction * (half + 3))
    last, low = None, 0
    while 0 < r < g.shape[0] - 1 and low < 8:
        if wide[r] > 20:
            last, low = r, 0
        else:
            low += 1
        r += direction
    if last is None or abs(last - r0) < half + 6:
        return None
    # the cap is the strongest stroke within 60 rows inside the end of the dark run (a line
    # running close along the bar can carry the run a little past the cap)
    edge = int(r0 + direction * (half + 5))
    if direction < 0:
        win = np.arange(last - 2, min(last + 60, edge))
    else:
        win = np.arange(max(last - 60, edge + 1), last + 3)
    # a cap darkens both sides of the bar in the same row; a sloping line only one side
    sym = flank - np.maximum(g[:, ci - 10:ci - 4].mean(axis=1), g[:, ci + 5:ci + 11].mean(axis=1))
    s = sym[win]
    strong = np.where(s > 0.6 * s.max())[0]
    # of the strong rows, the peak nearest the end of the run
    j = strong[0] if direction < 0 else strong[-1]
    while 0 < j < len(s) - 1 and s[j + (1 if direction < 0 else -1)] > s[j]:
        j += 1 if direction < 0 else -1
    k = win[j]
    a, b, cc = sym[k - 1], sym[k], sym[k + 1]
    den = a - 2 * b + cc
    off = float(np.clip(0.5 * (a - cc) / den, -1, 1)) if den < 0 else 0.0
    return float(k + off)


def read(image, at):
    cal = _calibrate(image)
    g = image.astype(float).mean(axis=2)
    yv = lambda r: (r - cal["ay"]) / cal["by"]
    xv = lambda c: 10 ** ((c - cal["ax"]) / cal["bx"])
    out = []
    pad_px = 2.0 + cal["misfit_y"]
    for c, r, half in _markers(image, cal):
        y = yv(r)
        ey = (1.5 + cal["misfit_y"]) / abs(cal["by"])
        row = {"x": float(xv(c)), "y": float(y), "lo": float(y - ey), "hi": float(y + ey), "px": [c, r],
               "note": f"marker centroid; y {cal['n_y']} marks misfit {cal['misfit_y']:.2f} px, "
                       f"x {cal['n_x']} marks misfit {cal['misfit_x']:.2f} px"}
        up = _bar_end(g, c, r, -1, half)
        dn = _bar_end(g, c, r, +1, half)
        if up is not None and dn is not None:
            hi, lo = yv(up), yv(dn)
            p = pad_px / abs(cal["by"])
            row.update({"bar_lo": float(lo), "bar_hi": float(hi), "bar_lo_outer": float(lo - p),
                        "bar_hi_outer": float(hi + p), "px_lo": up, "px_hi": dn})
            row["note"] += "; error bar caps found above and below"
        else:
            row["note"] += "; error bar end not found"
        out.append(row)
    return out
