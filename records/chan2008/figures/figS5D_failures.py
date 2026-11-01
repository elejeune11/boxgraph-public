"""Fig. S5D (PDF p. 48): failure frequency on 260, 730 and 1300 Pa gels, with error bars.

Calibration, from the image:
  y: the plot box top (0.0175) and bottom (0.005) and the dashed gridlines at
     0.0075 ... 0.015, found as minima of the grey profile across the plot;
  x (log10): the three tick strokes under the bottom edge, labelled 100, 1000
     and 10000, matched in order.
Markers: the three diamonds are the only strongly coloured pixels (the line
joining them is grey, the fitted line black); the centroid of each blob is the
point. Error bars: thin dark vertical lines through each marker ending in short
caps. Going up and down from the marker, the bar ends where the darkness of the
narrow column against its brighter flank stops; the cap is the strongest stroke
darkening both sides of the bar near that end.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.ndimage import uniform_filter1d

Y_LABELS = [0.0175, 0.015, 0.0125, 0.01, 0.0075, 0.005]   # matched: top to bottom
X_LABELS = [100.0, 1000.0, 10000.0]                       # matched: left to right


def _minima(prof, depth, win=41):
    base = uniform_filter1d(prof, win)
    d = base - prof
    out = []
    for i in range(4, len(prof) - 4):
        if d[i] > depth and d[i] == d[i - 3:i + 4].max():
            w = np.clip(d[i - 4:i + 5], 0, None)
            pos = (np.arange(i - 4, i + 5) * w).sum() / w.sum()
            if out and pos - out[-1][0] < 8:
                if d[i] > out[-1][1]:
                    out[-1] = (pos, d[i])
                continue
            out.append((pos, d[i]))
    return out


def _calibrate(img):
    g = img.astype(float).mean(axis=2)
    h, w = g.shape
    # rows: profile over the right part of the plot (no markers there)
    rows = [r for r, d in _minima(np.median(g[:, int(0.66 * w):int(0.9 * w)], axis=1), 40)]
    rows = sorted(rows)
    # the box and gridlines are the evenly spaced strong lines; take the run of six with even spacing
    best = None
    for i in range(len(rows) - len(Y_LABELS) + 1):
        seq = rows[i:i + len(Y_LABELS)]
        sd = float(np.std(np.diff(seq)))
        if best is None or sd < best[0]:
            best = (sd, seq)
    M = np.array(list(zip(best[1], Y_LABELS)))
    by, ay = np.polyfit(M[:, 1], M[:, 0], 1)
    misfit_y = float(np.max(np.abs(M[:, 0] - (ay + by * M[:, 1]))))
    bottom = max(best[1])
    # x: tick strokes just below the bottom edge
    strip = g[int(bottom) + 8:int(bottom) + 28].mean(axis=0)
    xs = sorted(c for c, d in _minima(strip, 30) if c > 0.25 * w)   # the y labels lie further left
    X = np.array(list(zip(xs, np.log10(X_LABELS)))) if len(xs) == len(X_LABELS) else None
    bx, ax = np.polyfit(X[:, 1], X[:, 0], 1)
    misfit_x = float(np.max(np.abs(X[:, 0] - (ax + bx * X[:, 1]))))
    return dict(ay=ay, by=by, ax=ax, bx=bx, misfit_y=misfit_y, misfit_x=misfit_x, top=min(best[1]),
                bottom=bottom, left=xs[0], right=xs[-1])


def _markers(img, cal):
    f = img.astype(float)
    sat = f.max(axis=2) - f.min(axis=2)
    m = sat > 120
    m[:int(cal["top"]) + 3] = False
    m[int(cal["bottom"]) - 3:] = False
    m[:, :int(cal["left"]) + 3] = False
    m[:, int(cal["right"]) - 3:] = False
    lab, n = ndi.label(ndi.binary_opening(m, iterations=2))
    out = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        if len(rr) >= 300:
            out.append((cc.mean(), rr.mean(), 0.5 * (rr.max() - rr.min())))
    return sorted(out)


def _bar_end(g, c, r0, direction, half):
    ci = int(round(c))
    flank = np.maximum(g[:, ci - 30:ci - 18].mean(axis=1), g[:, ci + 19:ci + 31].mean(axis=1))
    core = flank - g[:, ci - 3:ci + 4].min(axis=1)
    r = int(r0 + direction * (half + 3))
    last, low = None, 0
    while 0 < r < g.shape[0] - 1 and low < 8:
        if core[r] > 40:
            last, low = r, 0
        else:
            low += 1
        r += direction
    if last is None or abs(last - r0) < half + 6:
        return None
    sym = flank - np.maximum(g[:, ci - 14:ci - 5].mean(axis=1), g[:, ci + 6:ci + 15].mean(axis=1))
    edge = int(r0 + direction * (half + 5))
    win = np.arange(last - 3, min(last + 40, edge)) if direction < 0 else np.arange(max(last - 40, edge + 1), last + 4)
    s = sym[win]
    strong = np.where(s > 0.6 * s.max())[0]
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
    unit = abs(cal["by"])
    note = f"y 6 marks misfit {cal['misfit_y']:.2f} px, x 3 marks misfit {cal['misfit_x']:.2f} px"
    out = []
    for c, r, half in _markers(image, cal):
        y = yv(r)
        e = (1.5 + cal["misfit_y"]) / unit
        row = {"x": float(xv(c)), "y": float(y), "lo": float(y - e), "hi": float(y + e), "px": [c, r],
               "note": "marker centroid; " + note}
        up, dn = _bar_end(g, c, r, -1, half), _bar_end(g, c, r, +1, half)
        if up is not None and dn is not None:
            hi, lo = yv(up), yv(dn)
            p = (2.0 + cal["misfit_y"]) / unit
            row.update({"bar_lo": float(lo), "bar_hi": float(hi), "bar_lo_outer": float(lo - p),
                        "bar_hi_outer": float(hi + p), "px_lo": up, "px_hi": dn})
            row["note"] += "; error bar caps found above and below"
        else:
            row["note"] += "; error bar end not found"
        out.append(row)
    return out
