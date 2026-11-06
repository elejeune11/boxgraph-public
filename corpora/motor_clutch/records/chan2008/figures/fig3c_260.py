"""Fig. 3C (PDF p. 4): histogram of measured retrograde flow rates, read bar by bar.

Excel clustered histogram: each 10 nm/s category holds a blue (260 Pa) and a
red (57 kPa) bar. Everything is found in the image:
  y: the x axis line (0.00) and the faint dashed gridlines every 0.02, found as
     minima of the background grey profile (bar pixels masked out);
  x: the box edges and the tick marks below the axis give the category width;
     the label blobs under the axis ("0", "40", ..., "200", "More") are matched
     to categories 0, 4, ..., 20, 24, which gives 10 nm/s per category.
A bar's top is where the bar colour ends going up from the axis. A category
without a bar reads 0 (the smallest drawn bar is far taller than the edge blur).
x is the category label, the upper edge of the bin in Excel's convention.
"""
import numpy as np
from scipy.ndimage import uniform_filter1d

WHICH = "blue"          # this reading: the blue bars (260 Pa)
Y_STEP = 0.02           # matched: the y labels 0.00, 0.02, ..., 0.20 sit on the gridlines
LABEL_STEP = 40.0       # matched: the x labels 0, 40, ..., 200 are every 4th category
EDGE_PX = 3.0           # blur of a scanned bar top, in pixels (half-width of the colour ramp)


def _masks(img):
    f = img.astype(float)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    blue = (B - R > 20) & (B - G > 25) & (f.mean(axis=2) < 200)
    red = (R - G > 40) & (R - B > 30) & (f.mean(axis=2) < 215)
    return blue, red


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
    g = img.astype(float).mean(axis=2)
    f = img.astype(float)
    sat = f.max(axis=2) - f.min(axis=2)
    h, w = g.shape
    neutral_dark = (sat < 35) & (g < 200)
    # axis line: the lower-half row with most neutral dark pixels
    frac = neutral_dark.mean(axis=1)
    axis = h // 2 + int(np.argmax(frac[h // 2:]))
    # subpixel axis row from the darkness profile around it
    win = np.arange(axis - 4, axis + 5)
    dk = np.clip(220 - np.median(g[win][:, w // 4: 3 * w // 4], axis=1), 0, None)
    axis_row = float((win * dk).sum() / dk.sum())
    # box left/right edges: strong vertical neutral lines above the axis
    band = slice(int(axis_row) - 1300, int(axis_row) - 50)
    vfrac = ((sat[band] < 35) & (g[band] < 210)).mean(axis=0)
    on = np.where(vfrac > 0.5)[0]
    groups = np.split(on, np.where(np.diff(on) > 3)[0] + 1)
    edges = []
    for gr in groups:
        wts = vfrac[gr]
        edges.append(float((gr * wts).sum() / wts.sum()))
    left, right = edges[0], edges[-1]
    # gridlines: background profile with coloured pixels masked out
    blue, red = _masks(img)
    bg = np.where(blue | red, np.nan, g)
    rowprof = np.nanmean(bg[:, int(left) + 5:int(right) - 5], axis=1)
    rowprof = np.where(np.isnan(rowprof), np.nanmedian(rowprof), rowprof)
    mins = [r for r, d in _minima(rowprof, 4) if r < axis_row - 50]
    diffs = np.diff(sorted(mins))
    s0 = np.median([d for d in diffs if 80 < d < 300])
    pts = [(axis_row, 0.0)]
    for r in mins:
        k = (axis_row - r) / s0
        if abs(k - round(k)) < 0.12 and round(k) >= 1:
            pts.append((r, round(k) * Y_STEP))
    P = np.array(pts)
    b, a = np.polyfit(P[:, 1], P[:, 0], 1)     # row = a + b * value
    misfit_y = float(np.max(np.abs(P[:, 0] - (a + b * P[:, 1]))))
    # x: tick marks just below the axis give 2 categories each
    strip = g[int(axis_row) + 6:int(axis_row) + 20]
    ticks = [c for c, _ in _minima(strip.mean(axis=0), 5) if left - 3 < c < right + 3]
    tdiff = np.diff(ticks)
    two_w = np.median([d for d in tdiff if d > 60])
    cw = two_w / 2.0
    # label blobs under the ticks
    lab = (g[int(axis_row) + 40:int(axis_row) + 140] < 140).any(axis=0)
    lab[:int(left) - 60] = False
    on = np.where(lab)[0]
    blobs = np.split(on, np.where(np.diff(on) > 25)[0] + 1)
    centers = [(bl[0] + bl[-1]) / 2.0 for bl in blobs if len(bl)]
    cats = [(cc - left) / cw - 0.5 for cc in centers]
    numeric = [k for k in cats if -0.5 < k < 21]     # "0" ... "200"; "More" is the last blob
    idx = [round(k) for k in numeric]
    vals = [LABEL_STEP * i for i in range(len(idx))]
    per_cat, x0 = np.polyfit(idx, vals, 1)
    misfit_x_cat = float(np.max(np.abs(np.array(numeric) - np.array(idx))))
    n_cat = int(round((right - left) / cw))
    return dict(axis_row=axis_row, a=a, b=b, misfit_y=misfit_y, left=left, right=right, cw=cw,
                per_cat=per_cat, x0=x0, n_cat=n_cat, misfit_x_cat=misfit_x_cat, n_marks=len(P))


def read(image, at):
    return read_which(image, WHICH)


def read_which(image, which):
    """Read the bars of one colour; fig3c_57k.py calls this with "red"."""
    cal = _calibrate(image)
    blue, red = _masks(image)
    m = blue if which == "blue" else red
    axis = int(round(cal["axis_row"]))
    h, w = m.shape
    heights = np.zeros(w)
    tops = np.full(w, np.nan)
    for c in range(int(cal["left"]), int(cal["right"])):
        r, gap = axis - 3, 0
        top = None
        while r > 0 and gap <= 2:
            if m[r, c]:
                top, gap = r, 0
            else:
                gap += 1
            r -= 1
        if top is not None and axis - top > 8:
            heights[c] = axis - top
            tops[c] = top
    # group columns into bars
    bars, c = [], 0
    while c < w:
        if heights[c] > 0:
            c0 = c
            while c < w and heights[c] > 0:
                c += 1
            if c - c0 >= 12:
                core = tops[c0 + 4:c - 4]
                bars.append(((c0 + c - 1) / 2.0, float(np.nanmedian(core)), float(np.nanstd(core))))
        c += 1
    by_cat = {}
    for cx, top, sd in bars:
        k = int(np.floor((cx - cal["left"]) / cal["cw"]))
        by_cat[k] = (cx, top, sd)
    out = []
    unit = abs(cal["b"])                       # pixels per frequency unit
    for k in range(cal["n_cat"] - 1):          # the last category is "More": not a number
        x = cal["x0"] + cal["per_cat"] * k
        x = float(round(x, 6))
        if k in by_cat:
            cx, top, sd = by_cat[k]
            y = (top - cal["a"]) / cal["b"]
            err = (EDGE_PX + 1.0 + cal["misfit_y"] + 2 * sd) / unit
            out.append({"x": x, "y": float(y), "lo": float(y - err), "hi": float(y + err), "px": [cx, top],
                        "px_lo": top - err * unit, "px_hi": top + err * unit,
                        "note": f"bar top; y marks {cal['n_marks']}, misfit {cal['misfit_y']:.2f} px; "
                                f"x labels misfit {cal['misfit_x_cat']:.2f} category"})
        else:
            cx = cal["left"] + (k + (0.27 if which == "blue" else 0.8)) * cal["cw"]
            err = (EDGE_PX + 1.0 + cal["misfit_y"]) / unit
            out.append({"x": x, "y": 0.0, "lo": 0.0, "hi": float(err), "px": [cx, cal["axis_row"]],
                        "note": "no bar drawn in this category: frequency 0"})
    return out
