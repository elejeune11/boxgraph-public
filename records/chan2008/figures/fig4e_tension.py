"""Fig. 4E (PDF p. 5): scaled surface tension on 730 Pa and 1300 Pa gels, mean ± SEM.

Calibration, from the image: the plot box top (10) and the x axis line (0), and
the dashed gridlines at 2, 4, 6, 8, found as minima of the grey profile. The
axis label says values are in units of 1e-5 ("*10^-5"); the reading returns
them multiplied out. The two bars are found by colour (light blue, red); the
category labels under them, "730 Pa" and "1300 Pa", give x in Pa, left to right.
A bar's top is where its colour starts going down a column. Each error bar is a
dark vertical line inside the bar's columns; its ends are short horizontal caps,
found going up and going down from the bar top as the first rows where the dark
stroke through the error-bar column is cap-wide (rows on gridlines are skipped,
since a dash could pass for a cap). Lower caps lie on the bar, so darkness is
measured against each row's own surroundings.
"""
import numpy as np
from scipy.ndimage import uniform_filter1d

Y_LABELS = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]   # matched: the y labels, bottom to top
Y_FACTOR = 1e-5                               # matched: "(*10^-5, pixels^2/pixels^2)"
X_LABELS = [730.0, 1300.0]                    # matched: the category labels, in Pa


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


def _calibrate(img, bars):
    g = img.astype(float).mean(axis=2)
    h, w = g.shape
    # rows between the bars (no bar, no error bar): gridlines, box top, axis
    gap = slice(int(bars[0][1]) + 30, int(bars[1][0]) - 30)
    rows = _minima(g[:, gap].mean(axis=1), 6)
    bottom = max((r for r, d in rows if d > 15), key=lambda r: r)
    top = min((r for r, d in rows if d > 15), key=lambda r: r)
    step = (bottom - top) / (len(Y_LABELS) - 1)
    marks = [(bottom, Y_LABELS[0]), (top, Y_LABELS[-1])]
    for k in range(1, len(Y_LABELS) - 1):
        want = bottom - k * step
        near = [r for r, d in rows if abs(r - want) < 0.06 * step]
        if near:
            marks.append((min(near, key=lambda r: abs(r - want)), Y_LABELS[k]))
    M = np.array(marks)
    b, a = np.polyfit(M[:, 1], M[:, 0], 1)
    misfit = float(np.max(np.abs(M[:, 0] - (a + b * M[:, 1]))))
    return dict(a=a, b=b, misfit=misfit, n=len(M), grid=[m[0] for m in marks], bottom=bottom)


def _bars(img):
    f = img.astype(float)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    blue = (B - R > 30) & (B - G > 20) & (f.mean(axis=2) > 120)
    red = (R - G > 60) & (R - B > 50)
    out = []
    for m in (blue, red):
        cols = np.where(m.mean(axis=0) > 0.1)[0]
        c0, c1 = cols.min(), cols.max()
        core = m[:, c0 + 15:c1 - 15]
        rows = np.where(core.mean(axis=1) > 0.5)[0]
        out.append((float(c0), float(c1), float(rows.min()), float(rows.max())))
    return out


def _run_width(dark_row, c):
    if not dark_row[c]:
        return 0
    i = j = c
    while i > 0 and dark_row[i - 1]:
        i -= 1
    while j < len(dark_row) - 1 and dark_row[j + 1]:
        j += 1
    return j - i + 1


def read(image, at):
    g = image.astype(float).mean(axis=2)
    bars = _bars(image)
    cal = _calibrate(image, bars)
    yv = lambda r: (r - cal["a"]) / cal["b"]
    unit = abs(cal["b"])
    out = []
    for (c0, c1, top, bot), xlab in zip(bars, X_LABELS):
        ci0, ci1 = int(c0) + 10, int(c1) - 10
        # the error-bar column: darkest column just above the bar top
        above = g[int(top) - 30:int(top) - 3, ci0:ci1].mean(axis=0)
        ce = ci0 + int(np.argmin(above))
        # darkness of each row against its own surroundings (paper above, bar colour on the bar)
        local = np.median(g[:, ce - 60:ce + 61], axis=1)
        dark = g < (local[:, None] - 40)
        # on the bar the contrast is lower (a dark stroke on a mid-tone bar)
        dark[int(top) + 3:] = g[int(top) + 3:] < (local[int(top) + 3:, None] - 25)
        # the error bar's own line width, just above the bar top
        widths = [_run_width(dark[r], ce) for r in range(int(top) - 30, int(top) - 3)]
        lw = float(np.percentile([wd for wd in widths if wd > 0] or [6], 25))

        def is_cap(r):
            if any(abs(r - gr) < 8 for gr in cal["grid"]):
                return False
            wd = _run_width(dark[r], ce)
            return max(2.0 * lw, lw + 10) <= wd <= 80
        ends = []
        for direction in (-1, +1):
            r = int(top) + direction * 5
            rows = []
            while int(top) - 600 < r < cal["bottom"] - 5:
                if is_cap(r):
                    rows.append(r)
                elif rows:
                    break
                r += direction
            ends.append(float(np.mean(rows)) if rows else None)
        y = yv(top)
        e = (2.0 + cal["misfit"]) / unit
        row = {"x": xlab, "y": y * Y_FACTOR, "lo": (y - e) * Y_FACTOR, "hi": (y + e) * Y_FACTOR,
               "px": [ce, top], "note": f"bar top; y {cal['n']} marks misfit {cal['misfit']:.2f} px"}
        mirrored = None
        if (ends[0] is None) != (ends[1] is None):
            # one end lies on a gridline (or under the bracket): take it as the mirror of the other
            known = ends[0] if ends[0] is not None else ends[1]
            mirrored = "upper" if ends[0] is None else "lower"
            ends = [2 * top - known, known] if ends[0] is None else [known, 2 * top - known]
        if ends[0] is not None and ends[1] is not None:
            hi, lo = yv(ends[0]), yv(ends[1])
            p = (2.0 + cal["misfit"]) / unit
            row.update({"bar_lo": lo * Y_FACTOR, "bar_hi": hi * Y_FACTOR, "bar_lo_outer": (lo - p) * Y_FACTOR,
                        "bar_hi_outer": (hi + p) * Y_FACTOR, "px_lo": ends[0], "px_hi": ends[1]})
            if mirrored:
                p2 = p + 4.0 / unit                 # mirroring assumes a symmetric bar: widen
                if mirrored == "upper":
                    row["bar_hi_outer"] = (hi + p2) * Y_FACTOR
                else:
                    row["bar_lo_outer"] = (lo - p2) * Y_FACTOR
                row["note"] += (f"; error bar: the {mirrored} cap was not found (gridline or low contrast) "
                                f"and is taken as the mirror of the other about the bar top")
            else:
                row["note"] += "; error bar caps found above and below the bar top"
        else:
            row["note"] += "; error bar cap not found"
        out.append(row)
    return out
