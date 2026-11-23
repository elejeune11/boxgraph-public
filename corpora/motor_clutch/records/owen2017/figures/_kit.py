"""Shared reading code for the data figures of Owen et al. 2017 (MATLAB-style raster plots).

Each reading file (figures/<reading id>.py) calls the functions below and pins this file's SHA-256,
because the build caches a reading by the bytes of the reading file only.

Everything is found in the image. The only things typed in are the printed tick labels, matched in
order to the tick marks found, and colours of the series.

Calibration (`calibrate`)
- the axis lines are the longest dark vertical run (left part of the crop: the y axis) and the
  longest dark horizontal run (lower part: the x axis); their centre lines are taken.
- ticks are short dark stubs perpendicular to an axis line, inside or outside the plot (both
  bands are searched). Candidates are clusters of columns (rows) whose stub band is dark over at
  least 60% of its length; the evenly spaced subset with as many members as printed labels is kept
  (curves running through the band give stray candidates, which are not evenly spaced). A label
  may instead be pinned to the other axis line (for example x = 0 at the y-axis column).
- the value of a pixel is a straight-line fit through (tick position, label); the misfit is the
  largest residual in pixels.

Values are returned with a 95% interval made of: the half-width of the stroke or edge that was
read, the calibration misfit (twice, in value units), and any reader-specific term documented
where it is computed.
"""
import numpy as np
from scipy import ndimage


# ---------------------------------------------------------------- masks
def rgb(image):
    return image[..., :3].astype(float)


def dark_mask(image, thr=110):
    img = rgb(image)
    return img.mean(axis=2) < thr


def color_mask(image, color, tol=40):
    img = rgb(image)
    return np.sqrt(((img - np.array(color, float)) ** 2).sum(axis=2)) < tol


# ---------------------------------------------------------------- utilities
def clusters(idx, gap=2):
    idx = sorted(int(i) for i in idx)
    if not idx:
        return []
    out, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - prev > gap:
            out.append((start, prev))
            start = i
        prev = i
    out.append((start, prev))
    return out


def runs(v, gap=1):
    """(start, end) inclusive of True runs in a 1D boolean array."""
    return clusters(np.where(v)[0], gap)


def even_subset(cands, n, tol_frac=0.03):
    """The evenly spaced subset of n candidates with the smallest spread of spacing."""
    c = sorted(cands)
    best, best_err = None, None
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            step = c[j] - c[i]
            if step < 8:
                continue
            members = [c[i]]
            ok = True
            for k in range(1, n):
                if len(members) > 1:  # re-estimate the spacing from the members so far
                    step = (members[-1] - members[0]) / (len(members) - 1)
                target = c[i] + k * step
                near = [x for x in c if abs(x - target) <= max(2.5, tol_frac * step)]
                if not near:
                    ok = False
                    break
                members.append(min(near, key=lambda x: abs(x - target)))
            if not ok:
                continue
            d = np.diff(members)
            err = float(d.std())
            if best is None or err < best_err - 1e-9 or (abs(err - best_err) < 1e-9 and step > best[1] - best[0]):
                best, best_err = members, err
    return best


# ---------------------------------------------------------------- axes
class Lin:
    """value = a + b * pixel, fitted through (pixel, value) marks."""

    def __init__(self, marks, log=False):
        p = np.array([m[0] for m in marks], float)
        v = np.array([m[1] for m in marks], float)
        self.log = log
        u = np.log10(v) if log else v
        self.b, self.a = np.polyfit(p, u, 1)
        self.misfit_px = float(np.max(np.abs(p - (u - self.a) / self.b)))
        self.marks = marks

    def val(self, p):
        u = self.a + self.b * p
        return 10 ** u if self.log else u

    def pix(self, v):
        u = np.log10(v) if self.log else v
        return (u - self.a) / self.b

    def per_px(self, p):
        """|d value / d pixel| at pixel p."""
        return abs(self.val(p + 0.5) - self.val(p - 0.5))


def axis_lines(dark, left_frac=0.5, low_frac=0.5):
    """Centre column of the y-axis line and centre row of the x-axis line."""
    H, W = dark.shape
    best = (0, None)
    for c in range(int(W * left_frac)):
        r = runs(dark[:, c], 2)
        if r:
            L = max(b - a + 1 for a, b in r)
            if L > best[0]:
                best = (L, c)
    L0 = best[0]
    ycols = [c for c in range(int(W * left_frac)) if max([b - a + 1 for a, b in runs(dark[:, c], 2)] or [0]) > 0.9 * L0]
    ycol = float(np.mean(clusters(ycols)[0])) if ycols else None
    best = (0, None)
    for r_ in range(int(H * (1 - low_frac)), H):
        rr = runs(dark[r_, :], 2)
        if rr:
            L = max(b - a + 1 for a, b in rr)
            if L > best[0]:
                best = (L, r_)
    L0 = best[0]
    xrows = [r_ for r_ in range(int(H * (1 - low_frac)), H)
             if max([b - a + 1 for a, b in runs(dark[r_, :], 2)] or [0]) > 0.9 * L0]
    xrow = float(np.mean(clusters(xrows)[-1])) if xrows else None
    return ycol, xrow


def line_half_thickness(dark, ycol, xrow):
    c, r = int(round(ycol)), int(round(xrow))
    col = dark[:, max(c - 15, 0):c + 16]
    th_y = max((b - a + 1 for a, b in runs(dark[int(r * 0.5), max(c - 15, 0):c + 16], 1)), default=3)
    th_x = max((b - a + 1 for a, b in runs(dark[max(r - 15, 0):r + 16, int(c + (dark.shape[1] - c) * 0.5)], 1)), default=3)
    del col
    return th_y / 2.0, th_x / 2.0


def tick_candidates(dark, along, at, half, length, lo, hi):
    """Stub candidates along an axis line. along='x': stubs are vertical, at the x-axis row `at`;
    along='y': stubs horizontal at the y-axis column `at`. Both sides are searched."""
    out = {}
    for side in (-1, 1):
        s0 = int(round(at + side * (half + 2)))
        s1 = int(round(at + side * (half + 2 + length)))
        a_, b_ = sorted((s0, s1))
        if along == "x":
            band = dark[max(a_, 0):b_ + 1, :]
            frac = band.mean(axis=0)
        else:
            band = dark[:, max(a_, 0):b_ + 1]
            frac = band.mean(axis=1)
        idx = [i for i in np.where(frac > 0.6)[0] if lo <= i <= hi]
        out[side] = [(a + b) / 2 for a, b in clusters(idx, 1) if b - a < 25]
    return out


def calibrate(image, xlabels, ylabels, dark=None, x_pin=None, y_pin=None, tick_len=14,
              xr=None, yr=None, xlog=False, ylog=False):
    """Find axis lines and ticks; return (xaxis Lin, yaxis Lin, info).

    xlabels/ylabels: printed labels of the ticks to find, in increasing order.
    x_pin: a label sitting on the y-axis column (e.g. 0), y_pin: a label on the x-axis row.
    xr, yr: (lo, hi) pixel ranges in which to look for the ticks (defaults: along the axis line).
    """
    if dark is None:
        dark = dark_mask(image)
    ycol, xrow = axis_lines(dark)
    hy, hx = line_half_thickness(dark, ycol, xrow)
    H, W = dark.shape
    xr = xr or (ycol + hy + 3, W - 1)
    yr = yr or (0, xrow - hx - 3)
    xc = tick_candidates(dark, "x", xrow, hx, tick_len, *xr)
    yc = tick_candidates(dark, "y", ycol, hy, tick_len, *yr)
    xt = None
    for side in (-1, 1):
        if len(xc[side]) >= len(xlabels):
            s = even_subset(xc[side], len(xlabels))
            if s and (xt is None):
                xt = s
    yt = None
    for side in (1, -1):
        if len(yc[side]) >= len(ylabels):
            s = even_subset(sorted(yc[side], reverse=False), len(ylabels))
            if s and yt is None:
                yt = s
    if xt is None or yt is None:
        raise RuntimeError(f"ticks not found: x candidates {xc}, y candidates {yc}")
    xm = list(zip(sorted(xt), xlabels))
    if x_pin is not None:
        xm.append((ycol, x_pin))
    ym = list(zip(sorted(yt, reverse=True), ylabels))  # rows grow downwards
    if y_pin is not None:
        ym.append((xrow, y_pin))
    X, Y = Lin(xm, xlog), Lin(ym, ylog)
    return X, Y, {"ycol": ycol, "xrow": xrow, "hy": hy, "hx": hx, "dark": dark}


# ---------------------------------------------------------------- curves
def column_runs(mask, col, r0=0, r1=None, gap=1):
    r1 = mask.shape[0] if r1 is None else r1
    return [(a + r0, b + r0) for a, b in runs(mask[r0:r1, int(col)], gap)]


def curve_value(X, Y, mask, x, pick, r0=0, r1=None, avg=2, note=""):
    """Read one curve at value x: in the column, choose a run of the mask by `pick`
    (a function of the list of (start, end) runs returning one), average its centre over
    +-avg columns. Interval: half the run's length (stroke cut by the column), the change of
    the centre over +-avg columns, and twice the calibration misfits (x misfit through the
    local slope)."""
    c = int(round(X.pix(x)))
    centres, lens = [], []
    for cc in range(c - avg, c + avg + 1):
        rs = column_runs(mask, cc, r0, r1)
        if not rs:
            continue
        run = pick(rs)
        if run is None:
            continue
        centres.append((run[0] + run[1]) / 2)
        lens.append(run[1] - run[0] + 1)
    if len(centres) < avg + 1:
        return {"x": x, "y": None, "note": f"no curve pixels at this column {note}".strip()}
    row = float(np.median(centres))
    y = float(Y.val(row))
    dy = Y.per_px(row)
    spread = float(max(centres) - min(centres))
    slope = spread / (2 * avg) if avg else 0.0
    half_px = 0.5 * float(np.median(lens)) + 0.5 * spread + slope * 2 * X.misfit_px + 2 * Y.misfit_px + 1.0
    return {"x": x, "y": y, "lo": float(Y.val(row + half_px)), "hi": float(Y.val(row - half_px)),
            "px": [c, row], "px_lo": row - half_px, "px_hi": row + half_px,
            "note": f"run {np.median(lens):.0f} px; x misfit {X.misfit_px:.2g} px, y misfit {Y.misfit_px:.2g} px {note}".strip()}


def curve_band(X, Y, line, band, x, r0=0, r1=None, note=""):
    """A line drawn inside a shaded band (median or mean with its SD, SE or confidence band).
    The value is read by `curve_value` on the line mask, choosing the run nearest the band's
    centre; the band's top and bottom in the same column (the connected run of band-or-line
    pixels containing the line, gaps up to 3 px bridged) are the error bar ends, given as
    bar_lo/bar_hi, with bar_lo_outer/bar_hi_outer one pixel and twice the y misfit wider."""
    c = int(round(X.pix(x)))
    both = band | line
    rs = [ab for ab in runs(both[r0:r1, c], 3)]
    if not rs:
        return {"x": x, "y": None, "note": f"no band or line at this column {note}".strip()}
    rs = [(a + r0, b + r0) for a, b in rs]
    # the band run with most line pixels
    best = max(rs, key=lambda ab: line[ab[0]:ab[1] + 1, c].sum())
    mid = (best[0] + best[1]) / 2
    r = curve_value(X, Y, line, x, lambda q: min(q, key=lambda ab: abs((ab[0] + ab[1]) / 2 - mid)),
                    r0=best[0] - 2, r1=best[1] + 3, note=note)
    if r.get("y") is None:
        return r
    e = 1 + 2 * Y.misfit_px
    r.update({"bar_hi": float(Y.val(best[0])), "bar_lo": float(Y.val(best[1])),
              "bar_hi_outer": float(Y.val(best[0] - e)), "bar_lo_outer": float(Y.val(best[1] + e))})
    if Y.val(best[0]) < Y.val(best[1]):  # an inverted axis
        r["bar_hi"], r["bar_lo"] = r["bar_lo"], r["bar_hi"]
        r["bar_hi_outer"], r["bar_lo_outer"] = r["bar_lo_outer"], r["bar_hi_outer"]
    return r


def band_extent(Y, mask, col, row, gap=3):
    """Top and bottom rows of the connected band of `mask` that contains or is nearest to `row`
    in column `col`."""
    rs = runs(mask[:, int(col)], gap)
    if not rs:
        return None
    best = min(rs, key=lambda ab: 0 if ab[0] <= row <= ab[1] else min(abs(ab[0] - row), abs(ab[1] - row)))
    return best


# ---------------------------------------------------------------- histograms
def base_row_of(union):
    """The baseline of a bar chart: the commonest last row of the bars' fill over all columns."""
    lasts = [int(np.nonzero(union[:, c])[0][-1]) for c in range(union.shape[1]) if union[:, c].any()]
    vals, cnt = np.unique(lasts, return_counts=True)
    return float(vals[np.argmax(cnt)])


def histogram(X, Y, series, overlap, outline, c0, c1, note=""):
    """Overlaid, outlined histograms (MATLAB `histogram` with transparent faces).

    series: {name: mask of that series' own face colour}; overlap: mask of the colour where faces
    overlap (or None); outline: mask of the dark bar outlines. c0..c1: the columns of the plot.
    - baseline: the commonest last row of the faces.
    - bins: in the row 6 px above the baseline, the runs of face pixels between the dark outline
      columns are the insides of bins. Bins are of equal width, so the period is the median
      spacing of the starts of consecutive runs of typical width, refined by a straight-line fit of
      the starts against their bin numbers, and the grid is laid across the plot (so a faint separator, which merges two runs,
      or an empty bin does not shift the grid; an empty bin is reported as 0). x is the centre of
      the bin's inside; the bin's edges are in the note.
    - a series' value in a bin: over the inner half of the bin's columns, the top of the run of
      (own face or overlap or outline) that reaches the baseline, bridging gaps of up to 8 px
      (the outline of the other series' bar crosses it). If that top is outline, the outline's
      centre line is taken. A series without face in the bin is reported as 0 (no bar).
      Floating patches (the legend) do not reach the baseline and are not taken.
    Interval: half the outline thickness, 1 px, half the spread of the top over the bin's columns
    and twice the y misfit."""
    any_face = np.zeros_like(outline)
    for m in series.values():
        any_face = any_face | m
    if overlap is not None:
        any_face = any_face | overlap
    base = base_row_of(any_face[:, int(c0):int(c1)])
    row6 = int(base) - 6
    face_cols = [c for c in range(int(c0), int(c1)) if any_face[row6, c]]
    found = [(a, b) for a, b in clusters(face_cols, 1) if b - a >= 4]
    # bins are of equal width: the starts of runs of typical width are numbered by the median
    # spacing and fitted by a line (start = a0 + period * index); the grid is laid over c0..c1.
    widths = np.array([b - a + 1 for a, b in found], float)
    wmed = float(np.median(widths))
    single = [(a, b) for a, b in found if abs((b - a + 1) - wmed) < 0.3 * wmed and a > c0 + 1 and b < c1 - 2]
    starts = np.array([a for a, b in single], float)
    d = np.diff(starts)
    d = d[(d > 0.7 * wmed) & (d < 1.6 * wmed)]
    period, a0 = float(np.median(d)), starts[0]
    for span in (6, 12, 24, 48, 1e9):  # number runs near the first, fit, then extend the range
        use = starts <= a0 + span * period
        idx = np.round((starts[use] - a0) / period)
        if len(set(idx)) < 2:
            continue
        period, a0 = np.polyfit(idx, starts[use], 1)  # start = a0 + period * index
        period, a0 = float(period), float(a0)
    phase = float(np.mod(a0, period))
    first = phase + period * np.ceil((c0 - phase) / period)
    if first - period >= c0 - 2:
        first -= period
    bins = []
    s = first
    while s + 0.6 * period <= c1:
        bins.append((int(round(s)), int(round(s + period - (period - wmed)))))
        s += period
    if first - c0 > 0.6 * period:  # a partial first bin against the left spine
        bins.insert(0, (int(c0), int(round(first - (period - wmed)))))
    out = []
    for a, b in bins:
        w = b - a + 1
        inner = list(range(a + w // 4, b - w // 4 + 1))
        mid = (a + b) / 2
        for name, m in series.items():
            own_all = m if overlap is None else (m | overlap)
            full = own_all | outline
            tops, cols_used, has_face = [], [], 0
            for c in inner:
                rr = [ab for ab in runs(full[:int(base) + 1, c], 8) if ab[1] >= base - 3]
                if not rr:
                    continue
                t = rr[-1][0]
                if own_all[t:int(base) + 1, c].sum() >= 1:
                    has_face += 1
                k_ = t
                while k_ < base and outline[k_, c]:
                    k_ += 1
                tops.append((t + k_ - 1) / 2 if k_ > t else t - 0.5)
                cols_used.append(c)
            edges = f"bin x {X.val(a - 1):.4g} to {X.val(b + 1):.4g}"
            if has_face < len(inner) / 2 or not tops:
                out.append({"x": float(X.val(mid)), "y": 0.0, "lo": 0.0,
                            "hi": float(abs(Y.val(base - 3) - Y.val(base))), "px": [mid, base], "series": name,
                            "note": f"{name}: no bar in this bin; {edges} {note}".strip()})
                continue
            row = float(np.median(tops))
            spread = float(np.max(tops) - np.min(tops))
            th = float(np.median([outline[max(int(r) - 5, 0):int(r) + 6, c].sum() for r, c in zip(tops, cols_used)]))
            half = th / 2 + 1 + spread / 2 + 2 * Y.misfit_px
            out.append({"x": float(X.val(mid)), "y": float(Y.val(row)), "lo": float(Y.val(row + half)),
                        "hi": float(Y.val(row - half)), "px": [mid, row], "px_lo": row - half, "px_hi": row + half,
                        "series": name,
                        "note": f"{name}; {edges}; baseline reads {Y.val(base):.3g}; y misfit {Y.misfit_px:.2g} px {note}".strip()})
    return out


# ---------------------------------------------------------------- boxed axes
def box_lines(dark, frac=0.5):
    """Centres of the full-length dark vertical lines (spines) and horizontal lines of a boxed plot."""
    H, W = dark.shape
    vc = [(a + b) / 2 for a, b in clusters([c for c in range(W) if dark[:, c].sum() > frac * H])]
    hr = [(a + b) / 2 for a, b in clusters([r for r in range(H) if dark[r, :].sum() > frac * W])]
    return vc, hr


def spine_stubs(dark, spine_col, side, r0, r1, length=14, half=4):
    """Rows of short horizontal stubs touching a vertical spine on one side (side=+1: right of it)."""
    c0 = int(round(spine_col + side * (half + 2)))
    c1 = int(round(spine_col + side * (half + 2 + length)))
    a_, b_ = sorted((c0, c1))
    frac = dark[:, a_:b_ + 1].mean(axis=1)
    idx = [i for i in np.where(frac > 0.6)[0] if r0 <= i <= r1]
    return [(a + b) / 2 for a, b in clusters(idx, 1) if b - a < 25]


def line_stubs(dark, line_row, side, c0, c1, length=14, half=4):
    """Columns of short vertical stubs touching a horizontal line on one side (side=+1: below it)."""
    r0 = int(round(line_row + side * (half + 2)))
    r1 = int(round(line_row + side * (half + 2 + length)))
    a_, b_ = sorted((r0, r1))
    frac = dark[a_:b_ + 1, :].mean(axis=0)
    idx = [i for i in np.where(frac > 0.6)[0] if c0 <= i <= c1]
    return [(a + b) / 2 for a, b in clusters(idx, 1) if b - a < 25]


def read_disks(X, Y, mask, r, box, legend=None, note=""):
    """Plotted round markers of one colour. Peaks of the distance transform of the colour mask at
    least 0.6 r deep (lines are thinner and fall below it), merged within r; each component of
    (distance >= 0.6 r) is one marker or several overlapping ones. y is the centre of the peak
    region; interval: 0.25 r (blur and anti-aliasing of the edge), half the extra height of the
    component beyond one marker (overlapping markers of the same colour, whose centres cannot be
    told apart), and twice the y misfit. `box` = (c0, r0, c1, r1) limits the search; `legend` is
    a list of (c0, r0, c1, r1) regions to skip."""
    c0, r0, c1, r1 = [int(v) for v in box]
    sub = np.zeros_like(mask)
    sub[r0:r1, c0:c1] = mask[r0:r1, c0:c1]
    for (a, b, c, e) in legend or []:
        sub[int(b):int(e), int(a):int(c)] = False
    dt = ndimage.distance_transform_edt(sub)
    core = dt >= 0.6 * r
    lab, n = ndimage.label(core)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        m = lab[sl] == i
        sub_dt = np.where(m, dt[sl], 0)
        top = sub_dt.max()
        if top < 0.6 * r:
            continue
        pk = sub_dt >= top - 1.0
        rr, cc = np.nonzero(pk)
        row = float(rr.mean() + sl[0].start)
        col = float(cc.mean() + sl[1].start)
        hgt = sl[0].stop - sl[0].start
        wid = sl[1].stop - sl[1].start
        extra = max(0.0, hgt - 2 * (top - 0.6 * r) - 2)
        half = 0.25 * r + extra / 2 + 2 * Y.misfit_px
        flag = "; elongated: probably overlapping markers" if extra > 0.5 * r or wid > 2 * (top - 0.6 * r) + 2 + 0.5 * r else ""
        out.append({"x": float(X.val(col)), "y": float(Y.val(row)), "lo": float(Y.val(row + half)),
                    "hi": float(Y.val(row - half)), "px": [col, row], "px_lo": row - half, "px_hi": row + half,
                    "note": f"marker depth {top:.0f} px{flag} {note}".strip()})
    out.sort(key=lambda p: (p["x"], p["y"]))
    return out


# ---------------------------------------------------------------- markers
def blobs(mask, min_area):
    lab, n = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        m = lab[sl] == i
        area = int(m.sum())
        if area < min_area:
            continue
        rr, cc = np.nonzero(m)
        out.append({"row": float(rr.mean() + sl[0].start), "col": float(cc.mean() + sl[1].start), "area": area,
                    "h": sl[0].stop - sl[0].start, "w": sl[1].stop - sl[1].start})
    return out


def disks(mask, radius, min_frac=0.8):
    """Centres of filled disks of a given radius in a mask: local maxima of the distance transform
    at least min_frac*radius, merged within one radius."""
    dt = ndimage.distance_transform_edt(mask)
    mx = ndimage.maximum_filter(dt, size=int(radius))
    pk = (dt == mx) & (dt >= min_frac * radius)
    lab, n = ndimage.label(pk)
    cents = ndimage.center_of_mass(pk, lab, range(1, n + 1))
    out = []
    for r, c in cents:
        if all((r - a) ** 2 + (c - b) ** 2 > radius ** 2 for a, b in out):
            out.append((r, c))
    return out
