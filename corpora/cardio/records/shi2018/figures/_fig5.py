"""Shared reading code for Fig. 5 (PDF p. 7), the four panels (a) pressure, (b) flow-rate,
(c) volume and (d) pressure-volume loop of the Fig. 1(d) model. Each reading renders one panel.

The figure is an embedded raster, black on white; ink is darker than halfway between the paper
and the darkest pixel.

Calibration, all from the image:
- the y axis is the column (left third) with the most ink, the x axis the row (lower half) with
  the most ink; each line is a few pixels thick, and its centre is used;
- tick marks point inwards from both axes. Every short run of ink leaving the axis is a
  candidate; the labelled (major) ticks are the longest ones. They are matched in order to the
  printed labels the reading names (bottom to top, left to right); where the axis line itself
  carries the lowest label (the corner), the other axis's centre line is that mark;
- a straight line is fitted to the marks of each axis; its largest misfit (px) widens every
  interval. The figure is a low-resolution raster embedded in the PDF and resampled, so ticks
  meant to be evenly spaced land 3-4 px (at 900 dpi) off a straight line; a misfit over 6 px
  raises an error (a label is on the wrong tick).

Curves are separated by their pattern: a solid line is ink that is continuous over long column
spans; dotted and dashed lines are broken. Each reading function documents what it reads.
"""

import numpy as np
from scipy import ndimage


def gray(image):
    return image[..., :3].astype(float).mean(axis=2)


def ink_mask(image):
    g = gray(image)
    thr = (np.percentile(g, 99) + g.min()) / 2.0
    return g < thr


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def axes_lines(image):
    ink = ink_mask(image)
    H, W = ink.shape
    cs = ink[:, : W // 3].sum(axis=0)
    ycols = np.flatnonzero(cs > 0.85 * cs.max())
    yl, yr = int(ycols.min()), int(ycols.max()) + 1
    rs = ink[H // 2:, :].sum(axis=1)
    xrows = np.flatnonzero(rs > 0.85 * rs.max()) + H // 2
    xt, xb = int(xrows.min()), int(xrows.max()) + 1
    yc = (yl + yr - 1) / 2.0
    xc = (xt + xb - 1) / 2.0
    # extent of each axis line
    col = ink[:, int(round(yc))]
    top = min(a for a, b in _runs(col) if b >= xt)
    row = ink[int(round(xc)), :]
    right = max(b for a, b in _runs(row) if a <= yr)
    return dict(yl=yl, yr=yr, xt=xt, xb=xb, yc=yc, xc=xc, top=top, right=right)


def tick_candidates(image, ax, min_len=6):
    """(position, length) of runs of ink leaving the y axis to the right and the x axis upwards."""
    ink = ink_mask(image)
    ylen = []
    for r in range(ax["top"], ax["xt"]):
        n = 0
        while ax["yr"] + n < ink.shape[1] and ink[r, ax["yr"] + n]:
            n += 1
        ylen.append(n)
    ylen = np.array(ylen)
    yt = []
    for a, b in _runs(ylen >= min_len):
        if b - a > 40:
            continue
        yt.append(((a + b - 1) / 2.0 + ax["top"], int(ylen[a:b].max())))
    xlen = []
    for c in range(ax["yr"], ax["right"]):
        n = 0
        while ax["xt"] - 1 - n >= 0 and ink[ax["xt"] - 1 - n, c]:
            n += 1
        xlen.append(n)
    xlen = np.array(xlen)
    xt = []
    for a, b in _runs(xlen >= min_len):
        if b - a > 40:
            continue
        xt.append(((a + b - 1) / 2.0 + ax["yr"], int(xlen[a:b].max())))
    return yt, xt


def _majors(cands):
    """The labelled ticks: of the candidates longer than 1.4 times the median candidate (the
    minor ticks), the largest evenly spaced set (a curve touching the axis is not evenly spaced)."""
    L = 1.4 * float(np.median([l for _, l in cands]))
    c = sorted(p for p, l in cands if l > L)
    gaps = [b - a for a, b in zip(c, c[1:]) if b - a > 100]
    d = float(np.median(gaps))
    # the longest chain of candidates each about one spacing (within 12%) after the previous
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
    if mis > 6.0:
        raise RuntimeError(f"calibration misfit {mis:.1f} px: {marks}")
    return a, b, mis


# printed axis labels of each panel: y bottom to top, x left to right, and the corner's y label
PANELS = {
    "a": ([20, 40, 60, 80, 100, 120, 140], [7.0, 7.2, 7.4, 7.6, 7.8, 8.0], 0, None),
    "b": ([0, 200, 400, 600, 800, 1000], [7.0, 7.2, 7.4, 7.6, 7.8, 8.0], None, None),
    "c": ([40, 60, 80, 100, 120, 140, 160], [7.0, 7.2, 7.4, 7.6, 7.8, 8.0], None, None),
    "d": ([20, 40, 60, 80, 100, 120, 140, 160], [40, 60, 80, 100, 120, 140, 160], 0, None),
}


def calibrate_panel(image, panel):
    return calibrate(image, *PANELS[panel])


def calibrate(image, ylabels, xlabels, y_corner=None, x_corner=None):
    """ylabels bottom to top, xlabels left to right, as printed, for the major ticks found off the
    axes. y_corner / x_corner: the printed label carried by the axis corner itself, if any."""
    ax = axes_lines(image)
    yt, xt = tick_candidates(image, ax)
    # ticks within 15 px of the other axis are the corner, not a tick
    ym = [p for p in _majors([c for c in yt if c[0] < ax["xt"] - 15]) ][::-1]  # bottom to top
    xm = _majors([c for c in xt if c[0] > ax["yr"] + 15])
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
    return dict(ax=ax, ink=ink_mask(image), xa=xa, xb=xb, xmis=xmis, ya=ya, yb=yb, ymis=ymis,
                xmarks=xmarks, ymarks=ymarks)


def to_col(cal, x):
    return (x - cal["xa"]) / cal["xb"]


def to_row(cal, y):
    return (y - cal["ya"]) / cal["yb"]


def yval(cal, row):
    return cal["ya"] + cal["yb"] * row


def xval(cal, col):
    return cal["xa"] + cal["xb"] * col


def interior(cal, legend_box=None):
    """Ink inside the plot, without the axes, their ticks and an optional legend box (c0, r0, c1, r1)."""
    ax = cal["ax"]
    m = cal["ink"].copy()
    m[:, : ax["yr"] + 55] = False  # y ticks are at most ~48 px long
    m[ax["xt"] - 45:, :] = False  # x ticks at most ~36 px
    if legend_box is not None:
        c0, r0, c1, r1 = legend_box
        m[r0:r1, c0:c1] = False
    return m


def pieces(mask):
    """Connected pieces of ink, each with its bounding box and pixel count."""
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    sl = ndimage.find_objects(lab)
    out = []
    for i, s in enumerate(sl, start=1):
        rr, cc = s
        out.append(dict(label=i, r0=rr.start, r1=rr.stop, c0=cc.start, c1=cc.stop,
                        n=int((lab[s] == i).sum())))
    return lab, out


# the legend of each panel, (c0, r0, c1, r1) in pixels of the 900 dpi crop: a reader's choice of
# region to ignore (it holds sample lines, not data), like the crop itself
LEGEND = {"a": (2230, 0, 3030, 500), "b": (2050, 120, 2835, 450), "c": (2290, 60, 3030, 280), "d": None}

BLUR = 6.0  # px: one pixel of the embedded raster (about 150 dpi: runs come in 6 px steps at 900 dpi)


def setup(image, panel):
    """Calibration, the plot-interior ink, its pieces, and the solid line: the largest piece."""
    cal = calibrate_panel(image, panel)
    m = interior(cal, LEGEND[panel])
    lab, ps = pieces(m)
    big = max(ps, key=lambda q: q["n"])
    solid = lab == big["label"]
    others = [q for q in ps if q["label"] != big["label"]]
    # the solid line's usual thickness: the commonest run height over its columns
    hs = [b - a for c in range(big["c0"], big["c1"], 5) for a, b in _runs(solid[:, c])]
    th = float(np.median(hs)) if hs else 6.0
    return dict(cal=cal, mask=m, lab=lab, solid=solid, others=others, th=th)


def _subset(S, keep):
    out = np.zeros_like(S["mask"])
    for q in S["others"]:
        if keep(q):
            sl = (slice(q["r0"], q["r1"]), slice(q["c0"], q["c1"]))
            out[sl] |= S["lab"][sl] == q["label"]
    return out


def is_dash(q):
    """A dash: a piece at least 28 px wide and at most 30 px tall (the dashed curves are shallow;
    dashes are 30 px long in (b), 54-78 px in (a))."""
    return (q["c1"] - q["c0"]) >= 28 and (q["r1"] - q["r0"]) <= 30


def is_dot(q):
    """A dot of a dotted line (or a few dots run together where the line is steep): at most 26 px
    wide and smaller than 1500 px of ink."""
    return (q["c1"] - q["c0"]) <= 26 and q["n"] < 1500


def _value(S, x, col, row, half, slope=0.0, note=""):
    cal = S["cal"]
    e = half + BLUR + cal["ymis"] + abs(slope) * cal["xmis"]
    return {"x": x, "y": yval(cal, row), "lo": yval(cal, row + e), "hi": yval(cal, row - e),
            "px": [float(col), float(row)], "px_lo": row - e, "px_hi": row + e, "note": note}


def read_solid(image, at, panel):
    """The solid line, at each x: the centre of its single run of ink in that column. Refused where
    the column holds more than one run of it, or a run over 3 times its usual thickness that is not
    a steep stretch (it touches another curve)."""
    S = setup(image, panel)
    cal, solid, th = S["cal"], S["solid"], S["th"]
    out = []
    for x in at:
        x = float(x)
        col = to_col(cal, x)
        c = int(round(col))
        runs = _runs(solid[:, c])
        if len(runs) != 1:
            out.append({"x": x, "y": None, "note": f"{len(runs)} runs of the solid line in this column"})
            continue
        a, b = runs[0]
        nb = [np.mean(_runs(solid[:, k])[0]) for k in (c - 6, c + 6) if len(_runs(solid[:, k])) == 1]
        slope = abs(nb[1] - nb[0]) / 12.0 if len(nb) == 2 else 0.0
        if (b - a) > 3 * th and (b - a) > 3 * th + 12 * slope:
            out.append({"x": x, "y": None, "note": f"solid run {b - a} px tall (usual {th:.0f}): touches another curve"})
            continue
        out.append(_value(S, x, col, (a + b - 1) / 2.0, (b - a) / 2.0, slope, f"solid line, run {b - a} px"))
    return out


def read_dotted(image, at, panel, clear=12, drop_on_dashes=False):
    """The dotted line, at each x: the centre of the dot covering that column, or the line between
    the nearest dots either side (at most 45 px apart). Where the line is steep, dots stacked in one
    column (spanning at most 75 px) are read at the span's centre. Refused where the solid line or
    a dash is within `clear` px of the reading, or where a column holds dots further apart."""
    S = setup(image, panel)
    cal = S["cal"]
    if drop_on_dashes:
        # dots lying on a dashed track (within 15 px of where its dashes extend) belong to a
        # dash-dot curve, not to the dotted one
        def keep(q):
            if not is_dot(q):
                return False
            cc, rc = (q["c0"] + q["c1"]) / 2.0, (q["r0"] + q["r1"]) / 2.0
            return all(abs(e[0] - rc) > 15 for e in _dash_rows(S, int(cc)))
        dots = _subset(S, keep)
    else:
        dots = _subset(S, is_dot)
    dashes = _subset(S, is_dash)
    other = S["solid"] | dashes
    dcols = np.flatnonzero(dots.any(axis=0))
    out = []
    for x in at:
        x = float(x)
        col = to_col(cal, x)
        c = int(round(col))
        runs = _runs(dots[:, c])
        if len(runs) == 1:
            row, half, note = (runs[0][0] + runs[0][1] - 1) / 2.0, (runs[0][1] - runs[0][0]) / 2.0, "on a dot"
        elif len(runs) > 1 and runs[-1][1] - runs[0][0] <= 75:
            # a steep stretch: dots of the same line stacked in one column; read their span's centre
            a, b = runs[0][0], runs[-1][1]
            row, half, note = (a + b - 1) / 2.0, (b - a) / 2.0, f"{len(runs)} stacked dots spanning {b - a} px"
        elif len(runs) > 1:
            out.append({"x": x, "y": None, "note": f"{len(runs)} dots in this column over {runs[-1][1] - runs[0][0]} px"})
            continue
        else:
            left, right = dcols[dcols < c], dcols[dcols > c]
            if len(left) == 0 or len(right) == 0 or right[0] - left[-1] > 45:
                out.append({"x": x, "y": None, "note": "no dotted line here"})
                continue
            cl, cr = int(left[-1]), int(right[0])
            rl, rr = _runs(dots[:, cl]), _runs(dots[:, cr])
            if len(rl) != 1 or len(rr) != 1:
                out.append({"x": x, "y": None, "note": "dots either side are not single"})
                continue
            yl, yr_ = np.mean(rl[0]) - 0.5, np.mean(rr[0]) - 0.5
            w = (c - cl) / (cr - cl)
            row = (1 - w) * yl + w * yr_
            half = max(rl[0][1] - rl[0][0], rr[0][1] - rr[0][0]) / 2.0 + abs(yr_ - yl) / 2.0
            note = f"between dots {cr - cl} px apart"
        r0, r1 = int(max(row - half - clear, 0)), int(row + half + clear + 1)
        if other[r0:r1, max(c - 3, 0): c + 4].any():
            out.append({"x": x, "y": None, "note": "another curve is within reach: the dotted line is not separable here"})
            continue
        # slope from dots 20 px either side
        sl = 0.0
        rlft, rrgt = _runs(dots[:, max(c - 20, 0)]), _runs(dots[:, c + 20])
        if len(rlft) == 1 and len(rrgt) == 1:
            sl = abs(np.mean(rrgt[0]) - np.mean(rlft[0])) / 40.0
        out.append(_value(S, x, col, row, half, sl, note))
    return out


def _dash_rows(S, c, window=90):
    """Rows at column c of every dash within `window` columns: each dash's own centre at c if it
    covers c, else its centre line (a straight fit over its columns) extended to c."""
    lab = S["lab"]
    est = []
    for q in S["others"]:
        if not is_dash(q) or q["c1"] < c - window or q["c0"] > c + window:
            continue
        cols, rows = [], []
        for k in range(q["c0"], q["c1"]):
            rr = np.flatnonzero(lab[q["r0"]:q["r1"], k] == q["label"])
            if len(rr):
                cols.append(k)
                rows.append(q["r0"] + (rr.min() + rr.max()) / 2.0)
        if len(cols) < 5:
            continue
        b, a = np.polyfit(cols, rows, 1)
        dist = 0 if q["c0"] <= c < q["c1"] else min(abs(c - q["c0"]), abs(c - q["c1"]))
        est.append((a + b * c, dist, b))
    return sorted(est)


def read_dash_track(image, at, panel, which, n_tracks, gap=14):
    """A dashed curve, by its place among the dashed curves: at each x the dashes within 90 columns
    are extended to that column and grouped into tracks (rows more than `gap` px apart start a new
    track). Read only where exactly `n_tracks` tracks are found; `which` is the track's index from the
    top. The value is the nearest dash's row; the interval adds half the track's spread."""
    S = setup(image, panel)
    cal = S["cal"]
    out = []
    for x in at:
        x = float(x)
        col = to_col(cal, x)
        est = _dash_rows(S, int(round(col)))
        tracks = []
        for e in est:
            if tracks and e[0] - tracks[-1][-1][0] <= gap:
                tracks[-1].append(e)
            else:
                tracks.append([e])
        if len(tracks) != n_tracks:
            out.append({"x": x, "y": None, "note": f"{len(tracks)} dashed tracks here, not {n_tracks}"})
            continue
        tr = tracks[which]
        near = min(tr, key=lambda e: e[1])
        rows = [e[0] for e in tr]
        spread = (max(rows) - min(rows)) / 2.0
        half = 6.0 + spread  # dashes are about 12 px thick
        out.append(_value(S, x, col, near[0], half, near[2],
                          f"dashed track {which + 1} of {n_tracks}; nearest dash {near[1]} px away, {len(tr)} dashes"))
    return out


def read_extreme(image, panel, kind, top=True):
    """One point: the highest (top=True) or lowest ink of a curve, at its line centre. kind 'solid'
    or 'dotted'. x is the mean column of the ink in that extreme row band; its interval is the
    width of that band."""
    S = setup(image, panel)
    cal = S["cal"]
    m = S["solid"] if kind == "solid" else _subset(S, is_dot)
    rows = np.flatnonzero(m.any(axis=1))
    r = int(rows.min()) if top else int(rows.max())
    band = m[r: r + 4] if top else m[r - 3: r + 1]
    cols = np.flatnonzero(band.any(axis=0))
    half = (S["th"] if kind == "solid" else 12.0) / 2.0
    row = r + half - 0.5 if top else r - half + 0.5
    col = float(cols.mean())
    x = xval(cal, col)
    return [_value(S, x, col, row, half, 0.0,
                   f"{'highest' if top else 'lowest'} {kind} ink at row {r}; x read as {x:.4g} over "
                   f"columns {cols.min()}-{cols.max()}")]


def read_loop_edge(image, at, left=True):
    """Fig. 5(d): the loop's left (or right) vertical edge, read along rows: at each pressure, the
    centre of the leftmost (rightmost) run of the loop's ink in that row. x is pressure, y volume."""
    S = setup(image, "d")
    cal = S["cal"]
    out = []
    for p in at:
        p = float(p)
        row = to_row(cal, p)
        rr = int(round(row))
        runs = _runs(S["solid"][rr, :])
        if len(runs) < 2:
            out.append({"x": p, "y": None, "note": f"{len(runs)} runs of the loop in this row"})
            continue
        a, b = runs[0] if left else runs[-1]
        c = (a + b - 1) / 2.0
        e = (b - a) / 2.0 + BLUR + cal["xmis"]
        v = xval(cal, c)
        lo, hi = xval(cal, c - e), xval(cal, c + e)
        out.append({"x": p, "y": v, "lo": min(lo, hi), "hi": max(lo, hi), "px": [c, row],
                    "note": f"{'left' if left else 'right'} edge, run {b - a} px wide"})
    return out


def read_loop_branch(image, at, upper=True):
    """Fig. 5(d): the loop's upper (ejection) or lower (filling) branch: at each volume, the top
    (bottom) run of the loop's ink in that column. Refused where that run is over 3 times the line's
    thickness (a corner or a vertical edge)."""
    S = setup(image, "d")
    cal, th = S["cal"], S["th"]
    out = []
    for v in at:
        v = float(v)
        col = to_col(cal, v)
        c = int(round(col))
        runs = _runs(S["solid"][:, c])
        if len(runs) != 2:
            out.append({"x": v, "y": None, "note": f"{len(runs)} runs of the loop in this column"})
            continue
        a, b = runs[0] if upper else runs[1]
        if b - a > 3 * th:
            out.append({"x": v, "y": None, "note": f"run {b - a} px tall: a corner"})
            continue
        nb = []
        for k in (c - 8, c + 8):
            rk = _runs(S["solid"][:, k])
            if len(rk) == 2:
                nb.append(np.mean(rk[0] if upper else rk[1]))
        slope = abs(nb[1] - nb[0]) / 16.0 if len(nb) == 2 else 0.0
        out.append(_value(S, v, col, (a + b - 1) / 2.0, (b - a) / 2.0, slope,
                          f"{'upper' if upper else 'lower'} branch, run {b - a} px"))
    return out
