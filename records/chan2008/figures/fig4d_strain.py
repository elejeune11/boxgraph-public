"""Fig. 4D (PDF p. 5): histograms of bead displacements, read bar by bar.

MATLAB grouped bar chart: in each 5 nm bin a blue bar (Bead Strains) sits left
of a red bar (REF Bead RMS). Everything is found in the image:
  y: the x axis line (0) and the box top (0.5), with the inner tick marks on the
     right edge at 0.1 ... 0.4 found as short dark strokes;
  x: the box's left edge (under the label "0") and the inner tick marks on the
     bottom edge at 25, 50, 75 and 100, matched in order.
A bar's top is where its colour ends going up from the axis. The bin centre of
a group is midway between its blue and red bars; where a group has one bar, the
offset found in the full groups places the centre. A bin with no bar of this
colour reads 0. The last group, labelled "100+", collects everything above
100 nm and is not a bin centre: it is not read.
"""
import numpy as np
from scipy.ndimage import uniform_filter1d

WHICH = "blue"                       # this reading: the blue bars (Bead Strains)
Y_TICKS = [0.1, 0.2, 0.3, 0.4]       # matched: the y labels between 0 and 0.5
X_TICKS = [25.0, 50.0, 75.0, 100.0]  # matched: the x labels (the last printed "100+")
EDGE_PX = 3.0


def _masks(img):
    f = img.astype(float)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    blue = (B - R > 12) & (B - G > 20) & (f.mean(axis=2) < 175)
    red = (R - G > 35) & (R - B > 25)
    return blue, red


def _minima(prof, depth, win=31):
    """Dark strokes in a profile: (position, depth), strokes closer than 8 px merged."""
    base = uniform_filter1d(prof, win)
    d = base - prof
    out = []
    for i in range(3, len(prof) - 3):
        if d[i] > depth and d[i] == d[i - 2:i + 3].max():
            w = np.clip(d[i - 4:i + 5], 0, None)
            pos = (np.arange(i - 4, i + 5) * w).sum() / w.sum()
            if out and pos - out[-1][0] < 8:
                if d[i] > out[-1][1]:
                    out[-1] = (pos, d[i])
                continue
            out.append((pos, d[i]))
    return out


def _calibrate(img):
    f = img.astype(float)
    g = f.mean(axis=2)
    sat = f.max(axis=2) - f.min(axis=2)
    h, w = g.shape
    neutral = ((sat < 40) & (g < 185)).astype(float)

    def _peak(prof, lo, hi):
        i = lo + int(np.argmax(prof[lo:hi]))
        win = np.arange(max(lo, i - 3), min(hi, i + 4))
        wt = prof[win]
        return float((win * wt).sum() / wt.sum())

    cols = neutral[int(0.1 * h):int(0.8 * h)].mean(axis=0)
    left = _peak(cols, 0, int(0.3 * w))
    right = _peak(cols, int(0.7 * w), w)
    rows = neutral[:, int(left) + 50:int(right) - 50].mean(axis=1)
    top = _peak(rows, 0, int(0.3 * h))
    bottom = _peak(rows, int(0.6 * h), h)
    # y ticks: dark strokes just inside the right edge
    strip = g[:, int(right) - 22:int(right) - 6].mean(axis=1)
    ys = [r for r, d in _minima(strip, 6) if top + 30 < r < bottom - 30]
    marks_y = [(bottom, 0.0), (top, 0.5)]
    step = (bottom - top) / 5.0
    for k, v in enumerate(Y_TICKS, start=1):       # the legend also sits by this edge: keep
        want = bottom - k * step                    # only strokes where a tick belongs
        near = [r for r in ys if abs(r - want) < 0.06 * step]
        if near:
            marks_y.append((min(near, key=lambda r: abs(r - want)), v))
    M = np.array(marks_y)
    by, ay = np.polyfit(M[:, 1], M[:, 0], 1)
    misfit_y = float(np.max(np.abs(M[:, 0] - (ay + by * M[:, 1]))))
    # x ticks: dark strokes just inside the bottom edge, above the bars' reach is not
    # possible, so use the top edge, where nothing else is drawn but the legend
    stripx = g[int(top) + 6:int(top) + 22].mean(axis=0)
    xs = [c for c, d in _minima(stripx, 12) if left + 30 < c < right - 30]
    marks_x = [(left, 0.0)]
    if len(xs) == len(X_TICKS):
        marks_x += list(zip(sorted(xs), X_TICKS))
    X = np.array(marks_x)
    bx, ax = np.polyfit(X[:, 1], X[:, 0], 1)
    misfit_x = float(np.max(np.abs(X[:, 0] - (ax + bx * X[:, 1]))))
    return dict(top=top, bottom=bottom, left=left, right=right, ay=ay, by=by, ax=ax, bx=bx,
                misfit_y=misfit_y, misfit_x=misfit_x, n_y=len(M), n_x=len(X), xticks=xs, yticks=ys)


def _bars(m, cal):
    axis = int(round(cal["bottom"]))
    h, w = m.shape
    tops = np.full(w, np.nan)
    for c in range(int(cal["left"]) + 3, int(cal["right"]) - 3):
        r, gap, top = axis - 2, 0, None
        while r > cal["top"] and gap <= (8 if top is None else 2):
            if m[r, c]:
                top, gap = r, 0
            else:
                gap += 1
            r -= 1
        if top is not None and axis - top >= 3:
            tops[c] = top
    on = np.where(~np.isnan(tops))[0]
    out = []
    for grp in np.split(on, np.where(np.diff(on) > 2)[0] + 1):
        if len(grp) >= 8:
            core = tops[grp[2:-2]]
            med = float(np.nanmedian(core))
            mad = 1.4826 * float(np.nanmedian(np.abs(core - med)))   # robust spread of the top
            out.append(((grp[0] + grp[-1]) / 2.0, med, mad))
    return out


def _stub(g, c, cal):
    """Top row of a short dark bar standing on the axis at column c, or None.

    The axis line alone, away from bars, reaches about the grey of the line; a
    bar, however short, is much darker. The top is where the column's grey
    crosses halfway between the stub's darkest and the paper above it."""
    ci = int(round(c))
    axis = int(round(cal["bottom"]))
    col = g[axis - 40:axis + 1, ci - 4:ci + 5].mean(axis=1)
    dark = col.min()
    paper = np.median(g[axis - 60:axis - 40, ci - 4:ci + 5])
    ref = g[axis - 40:axis + 1, int(cal["left"]) + 5:int(cal["right"]) - 5].mean(axis=1)
    if dark > ref.min() - 25:                    # no darker than the bare axis line
        return None
    half = 0.5 * (dark + paper)
    i = int(np.argmin(col))
    while i > 0 and col[i] < half:
        i -= 1
    frac = (half - col[i]) / (col[i + 1] - col[i]) if col[i + 1] != col[i] else 0.0
    return float(axis - 40 + i + frac)


def read(image, at):
    return read_which(image, WHICH)


def read_which(image, which):
    """Read the bars of one colour; fig4d_ref.py calls this with "red"."""
    cal = _calibrate(image)
    blue, red = _masks(image)
    bb, rb = _bars(blue, cal), _bars(red, cal)
    # offset of each bar from its group centre, from groups holding both bars
    offs = []
    for cb, _, _ in bb:
        near = [cr for cr, _, _ in rb if 0 < cr - cb < 60]
        if near:
            offs.append((near[0] - cb) / 2.0)
    d = float(np.median(offs))
    centres = sorted([c + d for c, _, _ in bb] + [c - d for c, _, _ in rb])
    groups = []
    for c in centres:
        if groups and abs(c - groups[-1][-1]) < d:
            groups[-1].append(c)
        else:
            groups.append([c])
    gc = [float(np.mean(gr)) for gr in groups]
    # the bins are evenly spaced: extend the grid over bins whose bars are too short to show
    # their colour (they blur to dark stubs on the axis)
    dif = np.diff(gc)
    s0 = float(np.median(dif[dif < 1.5 * dif.min()]))
    ks = np.array([round((c - gc[0]) / s0) for c in gc])
    s, a = np.polyfit(ks, gc, 1)                 # group centre = a + s k, fitted to the found groups
    gc = [a + s * k for k in range(int(ks[-1]) + 1)]
    g = image.astype(float).mean(axis=2)
    xval = lambda c: (c - cal["ax"]) / cal["bx"]
    yval = lambda r: (r - cal["ay"]) / cal["by"]
    mine = bb if which == "blue" else rb
    sign = -1.0 if which == "blue" else 1.0
    unit = abs(cal["by"])
    out = []
    last_x = (cal["right"] - cal["ax"]) / cal["bx"]
    for c in gc:
        x = xval(c)
        if x > X_TICKS[-1]:
            continue                      # the "100+" group
        hit = [b for b in mine if abs(b[0] - (c + sign * d)) < d]
        note = f"y {cal['n_y']} marks misfit {cal['misfit_y']:.2f} px; x {cal['n_x']} marks misfit {cal['misfit_x']:.2f} px"
        if hit:
            cx, top, sd = hit[0]
            y = yval(top)
            err = (EDGE_PX + 1.0 + cal["misfit_y"] + 2 * sd) / unit
            out.append({"x": float(x), "y": float(y), "lo": float(max(0.0, y - err)), "hi": float(y + err),
                        "px": [cx, top], "px_lo": top - err * unit, "px_hi": top + err * unit,
                        "note": "bar top at the bin centre; " + note})
        elif which == "blue" and _stub(g, c + sign * d, cal) is not None:
            top = _stub(g, c + sign * d, cal)
            y = yval(top)
            err = (EDGE_PX + 4.0 + cal["misfit_y"]) / unit
            out.append({"x": float(x), "y": float(y), "lo": float(max(0.0, y - err)), "hi": float(y + err),
                        "px": [c + sign * d, top], "px_lo": top - err * unit, "px_hi": top + err * unit,
                        "note": "short bar, its colour lost in the blur: top of the dark stub on the axis; " + note})
        else:
            err = (EDGE_PX + 1.0 + cal["misfit_y"]) / unit
            out.append({"x": float(x), "y": 0.0, "lo": 0.0, "hi": float(err),
                        "px": [c + sign * d, cal["bottom"]], "note": "no bar of this colour in this bin: 0; " + note})
    del last_x
    return out
