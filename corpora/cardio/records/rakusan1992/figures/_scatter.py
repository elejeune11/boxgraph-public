"""Shared reading code for Figs. 2 and 3 (PDF p. 5): scatter plots of one value per heart against heart
mass, four marker kinds (open circle normal, open square congenital AS, filled circle acquired AS,
open triangle coarctation), with three drawn curves (the fitted polynomial, thick, between two thin
band lines).

Calibration, all from the image: the frame is found with boxgraph.digitize.find_axes and its four
spine lines located as the rows/columns that are mostly ink. Tick marks point inward from all four
spines; a tick is a column (row) where the 15 pixels just inside a spine are all ink and the inked
group is under 30 px wide. Ticks within 20 px of a frame corner are the corners themselves and are
dropped. The remaining ticks on the bottom and top spines are matched, left to right, to the printed
x labels between the ends of the axis, and those on the left and right spines, top to bottom, to the
printed y labels between its ends (the caller gives these lists; a mismatch in count is an error).
The scan is slightly rotated (the top and bottom ticks differ by a few pixels), so each axis is
fitted as a plane: column = a + b x + c row, and row = a' + b' y + c' column, by least squares on
the ticks of both spines. The largest tick misfit (pixels) is added to every interval.

Markers: the four legend symbols are the templates (each the largest ink component in a legend box
the caller gives, with an 8 px margin). The binary ink image is correlated with each template by
zero-mean normalized cross-correlation over the template window (ink and paper both count, so a line
passing through a window scores low). Local maxima (21 px neighbourhood) above the kind's threshold,
inside the plot frame (12 px inset) and outside the legend box, are candidates; all candidates of all
kinds are then taken in order of score and one is kept only if no kept marker lies within MIN_SEP px
(a filled circle over an open one is the filled circle). A marker's position is the template centre
at the correlation peak, +-3 px (half the stroke), plus the calibration misfit, converted to values.
Markers drawn exactly over another (same heart mass and value to within a few pixels) cannot be
separated; their count is compared with the paper's n in the record's figures.md.

Filled markers (read_filled) are found as solid ink instead, which separates two filled discs that
overlap (template correlation sees them as one): see that function.

The fitted curve: the ink inside the frame is opened with a disc of radius 5 px, which removes the
thin band lines (9-11 px thick at 900 dpi) and the open markers' strokes and keeps the thick middle
line (14-18 px). The thick line is traced with boxgraph.digitize.trace from several seeds the caller
gives (points on it between markers); each column takes the trace of the nearest seed that reaches
it, and the line is read at the requested x. Where a marker or another line merges with it the
trace keeps the prediction and widens the interval to the merged run.
"""

import math

import numpy as np
from scipy import ndimage, signal

from boxgraph.digitize import _column_center, find_axes, trace

INK = 127.5
MIN_SEP = 24


def _ink(image):
    return image.astype(float).mean(axis=2) < INK


def _groups(v):
    idx = np.nonzero(v)[0]
    out, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            out.append(cur)
            cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return [((g[0] + g[-1]) / 2 + 0.5, len(g)) for g in out]


def calibrate(image, x_labels, y_labels):
    """x_labels: printed x tick values left to right (interior ticks only); y_labels: printed y tick
    values top to bottom (interior ticks only). Returns (to_xy, misfit_px, frame)."""
    d = _ink(image)
    f = find_axes(image)
    c0, r0, c1, r1 = [int(round(v)) for v in f.box]
    top = max(r for r in range(max(0, r0 - 15), r0 + 15) if d[r, c0 + 50:c1 - 50].mean() > 0.6)
    bot = min(r for r in range(r1 - 15, r1 + 15) if d[r, c0 + 50:c1 - 50].mean() > 0.6)
    left = max(c for c in range(c0 - 15, c0 + 15) if d[r0 + 50:r1 - 50, c].mean() > 0.6)
    right = min(c for c in range(c1 - 15, c1 + 15) if d[r0 + 50:r1 - 50, c].mean() > 0.6)
    W, H = d.shape[1], d.shape[0]

    def ticks(v, lo, hi):
        return [p for p, n in _groups(v) if n < 30 and lo + 20 < p < hi - 20]

    t_top = ticks(np.array([d[top + 3:top + 18, c].all() for c in range(W)]), left, right)
    t_bot = ticks(np.array([d[bot - 18:bot - 3, c].all() for c in range(W)]), left, right)
    t_left = ticks(np.array([d[r, left + 3:left + 18].all() for r in range(H)]), top, bot)
    t_right = ticks(np.array([d[r, right - 18:right - 3].all() for r in range(H)]), top, bot)
    for name, t, lab in (("top", t_top, x_labels), ("bottom", t_bot, x_labels),
                         ("left", t_left, y_labels), ("right", t_right, y_labels)):
        if len(t) != len(lab):
            raise ValueError(f"{name} spine: {len(t)} ticks found, {len(lab)} labels: {t}")
    # x: column = a + b x + c row
    A, z = [], []
    for t, row in ((t_top, top + 0.5), (t_bot, bot + 0.5)):
        for p, v in zip(t, x_labels):
            A.append([1.0, v, row])
            z.append(p)
    px, *_ = np.linalg.lstsq(np.array(A), np.array(z), rcond=None)
    mx = float(np.max(np.abs(np.array(A) @ px - np.array(z))))
    B, w = [], []
    for t, col in ((t_left, left + 0.5), (t_right, right + 0.5)):
        for p, v in zip(t, y_labels):
            B.append([1.0, v, col])
            w.append(p)
    py, *_ = np.linalg.lstsq(np.array(B), np.array(w), rcond=None)
    my = float(np.max(np.abs(np.array(B) @ py - np.array(w))))

    def to_xy(col, row):
        # solve col = a + b x + c row, row = a' + b' y + c' col
        x = (col - px[0] - px[2] * row) / px[1]
        y = (row - py[0] - py[2] * col) / py[1]
        return x, y

    def x_to_col(x, row):
        return px[0] + px[1] * x + px[2] * row

    return {"to_xy": to_xy, "x_to_col": x_to_col, "misfit": max(mx, my, 0.5), "mx": mx, "my": my,
            "frame": (left, top, right, bot), "dy_dpx": 1.0 / py[1], "py": py}


def _template(d, box):
    r0, r1, c0, c1 = box
    m = d[r0 - 8:r1 + 8, c0 - 8:c1 + 8]
    lab, n = ndimage.label(m)
    big = int(np.argmax(ndimage.sum(m, lab, range(1, n + 1)))) + 1
    return (lab == big).astype(float)


def _ncc(d, t):
    n = t.size
    tz = t - t.mean()
    ones = np.ones_like(t)
    df = d.astype(float)
    sd = signal.fftconvolve(df, ones, mode="same")
    sd2 = signal.fftconvolve(df * df, ones, mode="same")
    num = signal.fftconvolve(df, tz[::-1, ::-1], mode="same")
    var = np.maximum(sd2 - sd * sd / n, 1e-6)
    return num / np.sqrt(var * (tz ** 2).sum())


def markers(image, legend, thresholds, legend_exclude):
    """All markers of all kinds: list of (kind, col, row, score)."""
    d = _ink(image)
    f = find_axes(image)
    c0, r0, c1, r1 = f.box
    cands = []
    for kind, box in legend.items():
        t = _template(d, box)
        s = _ncc(d, t)
        mxf = ndimage.maximum_filter(s, size=21)
        pk = (s == mxf) & (s > thresholds[kind])
        # the "same" mode centre of an even-sized template is offset by half a pixel; correct to the
        # ink's centre of mass within the template
        cy, cx = ndimage.center_of_mass(t)
        oy, ox = cy - (t.shape[0] // 2), cx - (t.shape[1] // 2)
        th, tw = t.shape
        tr, tc = np.nonzero(t > 0)
        sector = (np.floor((np.arctan2(tr - cy, tc - cx) + math.pi) / (2 * math.pi) * 8).astype(int)) % 8
        for r, c in zip(*np.nonzero(pk)):
            col, row = c + 0.5 + ox, r + 0.5 + oy
            wr, wc = r - th // 2, c - tw // 2
            if wr < 0 or wc < 0 or wr + th > d.shape[0] or wc + tw > d.shape[1]:
                continue
            hit = d[wr + tr, wc + tc]
            # the whole outline must be there: ink in at least 7 of 8 angular sectors (a line passing
            # through the window inks two opposite sectors only)
            full = sum(hit[sector == k].mean() >= 0.6 for k in range(8))
            if full < 7:
                continue
            if not (c0 + 30 < col < c1 - 30 and r0 + 30 < row < r1 - 30):
                continue
            er0, er1, ec0, ec1 = legend_exclude
            if er0 <= row <= er1 and ec0 <= col <= ec1:
                continue
            cands.append((float(s[r, c]), kind, col, row))
    cands.sort(key=lambda x: -x[0])
    kept = []
    for sc, kind, col, row in cands:
        if all(math.hypot(col - k[1], row - k[2]) >= MIN_SEP for k in kept):
            kept.append((kind, col, row, sc))
    return kept


def read_markers(image, kind, cfg):
    cal = calibrate(image, cfg["x_labels"], cfg["y_labels"])
    found = markers(image, cfg["legend"], cfg["thresholds"], cfg["legend_exclude"])
    out = []
    h = 3.0 + cal["misfit"]
    for k, col, row, sc in sorted(found, key=lambda m: m[1]):
        if k != kind:
            continue
        x, y = cal["to_xy"](col, row)
        _, ya = cal["to_xy"](col, row - h)
        _, yb = cal["to_xy"](col, row + h)
        out.append({"x": float(x), "y": float(y), "lo": float(min(ya, yb)), "hi": float(max(ya, yb)),
                    "px": [float(col), float(row)],
                    "note": f"template correlation {sc:.2f}; +-3 px marker centre and {cal['misfit']:.1f} px calibration misfit"})
    return out


def _kmeans(pts, k, iters=50):
    # deterministic start: points spread along the blob's major axis
    c = pts.mean(axis=0)
    u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    proj = (pts - c) @ vt[0]
    order = np.argsort(proj)
    cent = np.array([pts[order[int((i + 0.5) * len(pts) / k)]] for i in range(k)], dtype=float)
    for _ in range(iters):
        lab = np.argmin(((pts[:, None, :] - cent[None, :, :]) ** 2).sum(axis=2), axis=1)
        new = np.array([pts[lab == i].mean(axis=0) if (lab == i).any() else cent[i] for i in range(k)])
        if np.allclose(new, cent):
            break
        cent = new
    return cent


def read_filled(image, cfg):
    """Filled markers found as solid ink: the ink is opened with a disc of 0.6 of the legend
    marker's radius, which removes every line, outline and letter stroke and keeps only solid discs.
    Each remaining blob inside the frame counts round(area / area of the opened legend marker)
    markers; a blob of two or more overlapping discs is split by k-means on its pixels, started along
    its major axis. A marker centre is the blob (or cluster) centroid: +-3 px for a single disc, +-a
    quarter of the marker diameter for a split one, plus the calibration misfit."""
    cal = calibrate(image, cfg["x_labels"], cfg["y_labels"])
    d = _ink(image)
    r0, r1, c0, c1 = cfg["legend"][cfg["filled"]]
    t = _template(d, (r0, r1, c0, c1))
    diam = max(t.shape) - 16
    R = max(3, int(0.3 * diam))
    yy, xx = np.ogrid[-R:R + 1, -R:R + 1]
    disc = xx * xx + yy * yy <= R * R
    single = float(ndimage.binary_opening(np.pad(t > 0, R + 2), disc).sum())
    left, top, right, bot = cal["frame"]
    m = np.zeros_like(d)
    m[top + 6:bot - 5, left + 6:right - 5] = d[top + 6:bot - 5, left + 6:right - 5]
    op = ndimage.binary_opening(m, disc)
    lab, n = ndimage.label(op)
    er0, er1, ec0, ec1 = cfg["legend_exclude"]
    out = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        k = int(round(len(rr) / single))
        if k < 1:
            continue
        pts = np.stack([cc + 0.5, rr + 0.5], axis=1).astype(float)
        cents = [pts.mean(axis=0)] if k == 1 else list(_kmeans(pts, k))
        h = (3.0 if k == 1 else diam / 4) + cal["misfit"]
        for col, row in cents:
            if er0 <= row <= er1 and ec0 <= col <= ec1:
                continue
            x, y = cal["to_xy"](col, row)
            xa, ya = cal["to_xy"](col - h, row - h)
            xb, yb = cal["to_xy"](col + h, row + h)
            note = f"solid blob of {len(rr)} px = {len(rr) / single:.2f} markers"
            if k > 1:
                note += f"; split into {k} overlapping markers, centre +-{diam / 4:.0f} px"
            out.append({"x": float(x), "y": float(y), "lo": float(min(ya, yb)), "hi": float(max(ya, yb)),
                        "x_lo": float(min(xa, xb)), "x_hi": float(max(xa, xb)),
                        "px": [float(col), float(row)], "note": note})
    return sorted(out, key=lambda o: (o["x"], o["y"]))


def read_fit(image, at, cfg):
    cal = calibrate(image, cfg["x_labels"], cfg["y_labels"])
    d = _ink(image)
    left, top, right, bot = cal["frame"]
    m = np.zeros_like(d)
    m[top + 6:bot - 5, left + 6:right - 5] = d[top + 6:bot - 5, left + 6:right - 5]
    # keep only ink at least 2 R + 1 px thick in every direction: the thick fitted line and the
    # filled markers survive, the thin band lines and the open markers' strokes do not
    R = cfg.get("open_radius", 6)
    yy, xx = np.ogrid[-R:R + 1, -R:R + 1]
    line = ndimage.binary_opening(m, xx * xx + yy * yy <= R * R)
    # one trace per seed (a band line running close to it, or a stack of markers on it, can lead a
    # trace astray far from its seed); each column takes the trace of the nearest seed reaching it
    path, owner = {}, {}
    for seed in cfg["seeds"]:
        for k, v in trace(line, seed, max_gap=40).items():
            dist = abs(k - seed[0])
            if k not in path or dist < owner[k]:
                path[k], owner[k] = v, dist
    # the filled markers are solid discs: opened with a disc of 0.3 of the legend marker's diameter
    # they survive and the line does not. A traced column whose centre lies on a disc (the trace
    # stepped onto a marker touching the line, or the line passes under one) is replaced by the
    # interpolation between the nearest clean traced columns either side (at most 140 px apart),
    # with an interval that covers the marker's run in that column.
    r0, r1, c0, c1 = cfg["legend"][cfg["filled"]]
    t = _template(d, (r0, r1, c0, c1))
    Rf = max(3, int(0.3 * (max(t.shape) - 16)))
    yy, xx = np.ogrid[-Rf:Rf + 1, -Rf:Rf + 1]
    discs = ndimage.binary_dilation(ndimage.binary_opening(m, xx * xx + yy * yy <= Rf * Rf), iterations=3)
    on_disc = {k for k, (c, h, a) in path.items() if discs[min(max(int(c), 0), d.shape[0] - 1), k]}
    clean = sorted(k for k in path if k not in on_disc)
    under = set()
    for a, b in zip(clean, clean[1:]):
        if 1 < b - a <= 140:
            for k in range(a + 1, b):
                centre = path[a][0] + (path[b][0] - path[a][0]) * (k - a) / (b - a)
                half = max(path[a][1], path[b][1])
                for cc, hh in _column_center(discs, k):
                    if abs(cc - centre) <= hh + half:
                        half = max(half, abs(cc - centre) + hh)
                path[k] = (centre, half, True)
                under.add(k)
    for k in on_disc - under:
        del path[k]
    out = []
    for xv in at:
        # the column at x, on the row the curve is near (the axis is a plane, rotation is small)
        col_guess = cal["x_to_col"](xv, (top + bot) / 2)
        cands = [k for k in path if abs(k + 0.5 - col_guess) < 3]
        if not cands:
            out.append({"x": xv, "y": None, "note": "the traced thick curve does not reach this x"})
            continue
        row_c = path[min(cands, key=lambda k: abs(k + 0.5 - col_guess))][0]
        col = cal["x_to_col"](xv, row_c)
        k = int(math.floor(col))
        if k not in path:
            out.append({"x": xv, "y": None, "note": "the traced thick curve does not reach this x"})
            continue
        centre, half, amb = path[k]
        nb = [path[j][0] for j in (k - 1, k + 1) if j in path]
        slope = (nb[-1] - nb[0]) / 2 if len(nb) == 2 else 0.0
        hh = half + 0.5 + abs(slope) * (abs(col - (k + 0.5)) + cal["misfit"]) + cal["misfit"]
        _, y = cal["to_xy"](col, centre)
        _, ya = cal["to_xy"](col, centre - hh)
        _, yb = cal["to_xy"](col, centre + hh)
        if k in under:
            note = "the line passes under a filled marker here; interpolated across it, the interval covers the marker"
        elif amb:
            note = "a marker or another line merges with the curve here; the interval covers the merged run"
        else:
            note = ""
        out.append({"x": xv, "y": float(y), "lo": float(min(ya, yb)), "hi": float(max(ya, yb)),
                    "px": [float(col), float(centre)], "px_lo": float(centre - hh), "px_hi": float(centre + hh),
                    "note": note})
    return out


def debug(image, cfg):
    cal = calibrate(image, cfg["x_labels"], cfg["y_labels"])
    found = markers(image, cfg["legend"], cfg["thresholds"], cfg["legend_exclude"])
    return cal, found


# Per-figure settings, in pixels of the crop at the dpi of figures.yaml. Legend boxes are
# [row0, row1, col0, col1] around each legend symbol (found as the ink component there); seeds are
# (column, row) points on the thick fitted line, chosen in clean stretches between markers along its
# whole length; x_labels / y_labels are the printed tick labels between the frame corners.
FIG2 = {
    "x_labels": [200, 400, 600, 800, 1000],
    "y_labels": [4500, 4000, 3500, 3000, 2500, 2000, 1500],
    "legend": {"normal": [237, 297, 1072, 1134], "cong": [326, 375, 1072, 1125],
               "acq": [243, 299, 1840, 1896], "coa": [338, 389, 1842, 1896]},
    "thresholds": {"normal": 0.38, "cong": 0.4, "acq": 0.5, "coa": 0.45},
    "legend_exclude": [200, 420, 1040, 2450],
    "filled": "acq",
    "seeds": [[420, 976], [516, 1091], [612, 1182], [802, 1323], [1100, 1424], [1600, 1467], [1900, 1518]],
    "open_radius": 5,
}
FIG3 = {
    "x_labels": [200, 400, 600, 800, 1000],
    "y_labels": [800, 600, 400, 200],
    "legend": {"normal": [2114, 2178, 694, 760], "cong": [2207, 2261, 697, 751],
               "acq": [2113, 2171, 1534, 1597], "coa": [2213, 2269, 1539, 1600]},
    "thresholds": {"normal": 0.38, "cong": 0.4, "acq": 0.5, "coa": 0.45},
    "legend_exclude": [2050, 2340, 600, 2300],
    "filled": "acq",
    "seeds": [[828, 907], [1100, 769], [1900, 552]],
    "open_radius": 5,
}


__all__ = ["calibrate", "markers", "read_markers", "read_filled", "read_fit", "debug", "FIG2", "FIG3"]
