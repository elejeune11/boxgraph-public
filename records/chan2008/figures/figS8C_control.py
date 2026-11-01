"""Fig. S8C (PDF p. 51): mean retrograde flow on 260 Pa and 24 kPa gels, control and
GFP-actin transfected, with error bars.

Calibration, from the image: the plot box top (180) and the x axis line (0), and
the dashed gridlines every 20 nm/s between, found as minima of the grey profile
in the gap between the two bar groups and kept where a gridline belongs. Bars
are found by colour: lavender (Control) and magenta (GFP-Actin Transfected).
The group labels under the axis, "260 Pa" and "24 kPa", give x left to right.
A bar's top is where its colour starts going down its inner columns. Each error
bar is a thin dark line through the bar top; its ends are short caps, found
going up and down from the bar top as the first rows where the dark stroke
through the error-bar column is several times the line's own width (darkness
measured against each row's own surroundings, so caps on the bar are found too).
"""
import numpy as np
from scipy.ndimage import uniform_filter1d

WHICH = "control"
Y_LABELS = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0]   # matched, bottom to top
X_LABELS = [260.0, 24000.0]   # matched: "260 Pa", "24 kPa", in Pa


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


def _masks(img):
    f = img.astype(float)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    control = (B - G > 50) & (B - R > 40) & (R > 140)
    gfp = (R - G > 90) & (B - G > 20) & (R > 150)
    return {"control": control, "gfp": gfp}


def _bars(m):
    """Bars of one colour: (c0, c1, top) for each wide column run."""
    cols = np.where(m.mean(axis=0) > 0.15)[0]
    out = []
    for grp in np.split(cols, np.where(np.diff(cols) > 3)[0] + 1):
        if len(grp) < 60:
            continue
        c0, c1 = grp[0], grp[-1]
        core = m[:, c0 + 25:c1 - 25]
        rows = np.where(core.mean(axis=1) > 0.6)[0]
        out.append((float(c0), float(c1), float(rows.min())))
    return out


def _calibrate(img, all_bars):
    g = img.astype(float).mean(axis=2)
    spans = sorted((b[0], b[1]) for b in all_bars)
    # the widest gap between bars (between the two groups)
    gaps = [(spans[i + 1][0] - spans[i][1], spans[i][1], spans[i + 1][0]) for i in range(len(spans) - 1)]
    _, g0, g1 = max(gaps)
    rows = _minima(np.median(g[:, int(g0) + 20:int(g1) - 20], axis=1), 4)
    strong = [r for r, d in rows if d > 30]
    top, bottom = min(strong), max(strong)
    step = (bottom - top) / (len(Y_LABELS) - 1)
    marks = [(bottom, Y_LABELS[0]), (top, Y_LABELS[-1])]
    for k in range(1, len(Y_LABELS) - 1):
        want = bottom - k * step
        near = [r for r, d in rows if abs(r - want) < 0.05 * step]
        if near:
            marks.append((min(near, key=lambda r: abs(r - want)), Y_LABELS[k]))
    M = np.array(marks)
    b, a = np.polyfit(M[:, 1], M[:, 0], 1)
    misfit = float(np.max(np.abs(M[:, 0] - (a + b * M[:, 1]))))
    return dict(a=a, b=b, misfit=misfit, n=len(M), bottom=bottom)


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
    return read_which(image, WHICH)


def read_which(image, which):
    """Read one colour's bars; figS8C_gfp.py calls this with "gfp"."""
    g = image.astype(float).mean(axis=2)
    masks = _masks(image)
    allb = _bars(masks["control"]) + _bars(masks["gfp"])
    cal = _calibrate(image, allb)
    yv = lambda r: (r - cal["a"]) / cal["b"]
    unit = abs(cal["b"])
    out = []
    for (c0, c1, top), xlab in zip(sorted(_bars(masks[which])), X_LABELS):
        # error-bar column: the darkest column just above the bar top, near the bar's middle
        mid0, mid1 = int(c0 + 0.25 * (c1 - c0)), int(c1 - 0.25 * (c1 - c0))
        above = g[int(top) - 25:int(top) - 4, mid0:mid1].mean(axis=0)
        ce = mid0 + int(np.argmin(above))
        local = np.median(g[:, ce - 90:ce + 91], axis=1)
        dark = g < (local[:, None] - 40)
        widths = [_run_width(dark[r], ce) for r in range(int(top) - 25, int(top) - 4)]
        lw = float(np.percentile([wd for wd in widths if wd > 0] or [6], 25))

        def is_cap(r):
            wd = _run_width(dark[r], ce)
            return max(2.0 * lw, lw + 10) <= wd <= 120

        ends = []
        for direction in (-1, +1):
            r = int(top) + direction * 4
            rows = []
            while int(top) - 400 < r < int(top) + 400:
                if is_cap(r):
                    rows.append(r)
                elif rows:
                    break
                r += direction
            ends.append(float(np.mean(rows)) if rows else None)
        y = yv(top)
        e = (2.0 + cal["misfit"]) / unit
        row = {"x": xlab, "y": float(y), "lo": float(y - e), "hi": float(y + e), "px": [ce, top],
               "note": f"bar top; y {cal['n']} marks misfit {cal['misfit']:.2f} px"}
        if ends[0] is not None and ends[1] is not None:
            hi, lo = yv(ends[0]), yv(ends[1])
            p = (2.0 + cal["misfit"]) / unit
            row.update({"bar_lo": float(lo), "bar_hi": float(hi), "bar_lo_outer": float(lo - p),
                        "bar_hi_outer": float(hi + p), "px_lo": ends[0], "px_hi": ends[1]})
            row["note"] += "; error bar caps found above and below the bar top"
        else:
            row["note"] += "; error bar cap not found"
        out.append(row)
    return out
