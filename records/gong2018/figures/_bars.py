"""Shared code for the bar charts of gong2018 (Figs. 6D-E, S5A, S5C, S8B-C).

Axis: only y is calibrated.  The y axis is the longest vertical dark line in the
crop; its tick marks point outward (left, `ticks: out`) or inward (right, `in`)
and are the rows where a band `tick_len` px wide on that side is dark; they are
matched, top to bottom, to the printed labels in the stub (`y_labels`, times
`y_mult` when the axis label carries a power of ten).  A linear fit gives the
calibration and its misfit.

x: the bars of one colour, left to right, are the categories printed under them
(`categories`, as printed, in the stub): the x of a reading is that label.

A bar is a large blob of its fill colour.  Its value is the top of the bar: the
middle of the band between the last white row above the fill and the first fill
row (the outline, if any), read at a quarter of the bar's width (away from the
error bar).  Error bars (`bars: true`): the error-bar column is the darkest
column of the fill; from the bar's top the dark line is followed upward (on the
paper) and downward (inside the fill, darker than the fill by `contrast`),
bridging gaps of `gap` rows; the ends are the caps, taken half a line width
inside the last dark row; the outer interval adds that line width, one source
pixel and the calibration misfit.  An end hidden inside the bar (a bar without a
lower whisker) is taken as the mirror of the upper one, and the note says so.

Interval of the value (95%): half the outline band, one source pixel of the
upsampled image (`src_px`), the calibration misfit and half a pixel.
"""
import numpy as np
from scipy import ndimage as ndi

from boxgraph import digitize as dg


def _gray(img):
    return img.astype(float).mean(axis=2)


def calibrate_y(img, s):
    g = _gray(img)
    d = (g < s.get("dark", 140)) & ((img.max(axis=2).astype(int) - img.min(axis=2)) < 60)
    H, W = d.shape
    # the y axis: the column with the longest vertical dark run, left of `axis_max_col`
    best = (0, 0, 0, 0)
    for c in range(s.get("axis_min_col", 0), min(W, s.get("axis_max_col", W))):
        n, a, b = dg._longest_run(d[:, c], gap=2)
        if n > best[0]:
            best = (n, c, a, b)
    n, col, a, b = best
    cols = [c for c in range(max(col - 15, 0), min(col + 16, W)) if dg._longest_run(d[:, c], gap=2)[0] >= 0.9 * n]
    c0, c1 = min(cols), max(cols)
    L = s.get("tick_len", 40)
    if s.get("ticks", "out") == "out":
        band = d[:, max(c0 - L, 0):c0 - 3]
    else:
        band = d[:, c1 + 4:c1 + L]
    frac = band.mean(axis=1)
    hit = np.nonzero(frac > s.get("tick_frac", 0.6))[0]
    hit = hit[(hit >= a - 6) & (hit <= b + 6)]
    groups, cur = [], []
    for i in list(hit) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            if len(cur) <= 30:
                groups.append((cur[0] + cur[-1] + 1) / 2)
            cur = []
        if i is not None:
            cur.append(i)
    labels = [v * s.get("y_mult", 1.0) for v in s["y_labels"]]
    if len(groups) != len(labels):
        raise dg.CalibrationError(f"found {len(groups)} y ticks {groups}, expected {len(labels)}")
    return dg.Axis("linear", list(zip(groups, labels))), (c0, c1, a, b)


def read_bars(img, s):
    ya, axis = calibrate_y(img, s)
    f = img.astype(float)
    m = np.sqrt(((f - np.asarray(s["color"], float)) ** 2).sum(axis=2)) <= s["tol"]
    m[:, :axis[1] + 3] = False
    for ea, eb, ec, ed in s.get("exclude", []):
        m[eb:ed, ea:ec] = False
    # the error bar drawn through the fill would split a bar in two: close across it
    m = ndi.binary_closing(m, structure=np.ones((1, 21), bool))
    m = ndi.binary_opening(m, structure=np.ones((5, 5), bool))
    lab, n = ndi.label(m)
    blobs = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        area = (lab[sl] == i).sum()
        if area >= s.get("min_area", 20000) and sl[1].stop - sl[1].start >= s.get("min_w", 60):
            blobs.append((sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, i))
    blobs.sort()
    cats = s["categories"]
    if len(blobs) != len(cats):
        raise dg.CalibrationError(f"found {len(blobs)} bars of colour {s['color']}, expected {len(cats)}")
    g = _gray(img)
    src = s.get("src_px", 8)
    res = max(ya.residual_px, 0.5)
    out = []
    for (ca, cb, ra, rb, li), cat in zip(blobs, cats):
        w = cb - ca
        qc = int(ca + w / 4)
        # top of the bar: the band between the last white row and the first fill row
        top_fill = int(np.nonzero(lab[:, qc] == li)[0].min())
        r = top_fill
        while r > 0 and g[r - 1, qc] < s.get("white", 200):
            r -= 1
        band = top_fill - r
        row = (r + top_fill) / 2
        e = band / 2 + src + 0.5 + res
        lo, hi = sorted((ya.to_value(row + e), ya.to_value(row - e)))
        rec = {"x": float(cat), "y": ya.to_value(row), "lo": lo, "hi": hi, "px": [(ca + cb) / 2, row],
               "px_lo": row - e, "px_hi": row + e, "note": f"bar columns {ca}-{cb}, top band rows {r}-{top_fill}"}
        if s.get("bars"):
            inner = slice(top_fill + 5, top_fill + max(10, (rb - top_fill) // 3))
            # away from the bar's own outline
            colmeans = g[inner, ca + 20:cb - 20].mean(axis=0)
            wc = ca + 20 + int(np.argmin(colmeans))
            fill_g = float(np.median(g[inner, qc]))
            strip = g[:, wc - 2:wc + 3].min(axis=1)
            gap = s.get("gap", 3)
            # up, on paper
            i, last, miss = r, r, 0
            while i > 0:
                i -= 1
                if strip[i] < s.get("white", 200) - 40:
                    last, miss = i, 0
                else:
                    miss += 1
                    if miss > gap:
                        break
            up_end = last
            # down, inside the fill
            i, last, miss = top_fill, top_fill, 0
            while i < rb - 2:
                i += 1
                if strip[i] < fill_g - s.get("contrast", 15):
                    last, miss = i, 0
                else:
                    miss += 1
                    if miss > gap:
                        break
            down_end = last
            lw = s.get("line_w", 8)
            t_mid = up_end + lw / 2
            if down_end > top_fill + 2 * lw:
                b_mid = down_end + 1 - lw / 2
                rec["note"] += f"; error bar rows {up_end}-{down_end} at column {wc}"
            else:
                b_mid = 2 * row - t_mid
                rec["note"] += f"; upper error bar to row {up_end} at column {wc}; lower end hidden, taken as its mirror"
            ew = lw / 2 + src + res
            rec["bar_hi"] = ya.to_value(t_mid)
            rec["bar_lo"] = ya.to_value(b_mid)
            rec["bar_hi_outer"] = ya.to_value(t_mid - ew)
            rec["bar_lo_outer"] = ya.to_value(b_mid + ew)
        out.append(rec)
    return out
