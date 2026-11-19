"""Shared reading code for the plots of tallinen2015 (vector figures, rendered at high dpi).

All figures of this paper are vector graphics, so lines are sharp at any dpi.

Calibration, all from the image:
  * the axis lines are found as the row (x axis) and column (y axis) of axis ink (black, or the
    spec's frame colour) with the longest run, searched in the spec's region of the crop;
  * tick marks are short runs of axis ink standing on the axis line, on the side the spec gives
    ("in" = into the plot, "out" = outside, "both"); ticks shorter than the spec's `major_len`
    (minor ticks) are dropped; the remaining ticks are matched in order to the printed labels in
    the spec. A label printed at the axis corner is put at the other axis line ("at_axis");
  * a straight line is fitted through these positions; the largest misfit (px) is reported and
    added to every interval.

Curves: a colour mask of the curve ink inside the plot box (text and legends named in the spec
blanked). Connected components are split by size: `part: solid` keeps the components wider than
`min_solid` px (whole lines), `part: dashed` the smaller ones (dashes), `part: all` everything.
At the column of a requested x the runs of the mask are listed and one is chosen by `rank`
(k-th from the bottom, or from the top when negative), optionally only between two rows
(`band`, given as values, which only says which curve is meant). Where the chosen line has a gap
in that column (between dashes, or behind a label), its centre is interpolated by a quadratic fit
to the centres of the same-rank runs within +-`fit_px` columns, and the fit residual widens the
interval. A run longer than the line's vertical thickness plus 4 px is fused with another line;
its interval is the whole run.

Intervals (95%): centre +- (2 px + y misfit) for a clean run; the run's extent +- the same for a
fused run; +- (3 px + 2 x fit residual + y misfit) for an interpolated centre; to each is added
|slope| (x misfit + 1 px), the shift in y of an error in x where the curve is steep.

Markers: connected components of a colour mask, closed and hole-filled, with an area within the
spec's range; the value is the centroid, the interval +- (misfit + 2 px).
"""

import math

import numpy as np
from scipy import ndimage


def rgb(image):
    return np.asarray(image)[..., :3].astype(int)


def mask_of(image, ink):
    if isinstance(ink, list) and ink and isinstance(ink[0], str):  # several inks together
        m = mask_of(image, ink[0])
        for k in ink[1:]:
            m = m | mask_of(image, k)
        return m
    a = rgb(image)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    chroma = a.max(axis=2) - a.min(axis=2)
    if ink == "black":
        return (r + g + b < 330) & (chroma < 45)
    if ink == "blue":
        return (b - r > 50) & (b - g > 40)
    if ink == "red":
        return (r - g > 80) & (r - b > 80)
    if ink == "green":
        return (g - r > 40) & (g - b > 30)
    if ink == "magenta":
        return (r - g > 60) & (b - g > 60)
    if ink == "cyan":
        return (g - r > 60) & (b - r > 60) & (abs(g - b) < 70)
    if ink == "olive":
        return (r - b > 60) & (g - b > 60) & (abs(r - g) < 60)
    col = np.array(ink[:3])
    tol = ink[3] if len(ink) > 3 else 60
    return np.sqrt(((a - col) ** 2).sum(axis=2)) < tol


def runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    return max((b - a for a, b in runs(v)), default=0)


class Axis:
    def __init__(self, pix, vals, log=False):
        self.log = log
        p = np.array(pix, float)
        v = np.log10(vals) if log else np.array(vals, float)
        self.b, self.a = np.polyfit(p, v, 1)
        self.misfit = float(np.max(np.abs((v - self.a) / self.b - p))) if len(p) > 2 else 0.0
        self.pix, self.vals = [float(x) for x in p], list(vals)

    def val(self, px):
        u = self.a + self.b * px
        return 10 ** u if self.log else u

    def px(self, val):
        u = math.log10(val) if self.log else val
        return (u - self.a) / self.b


def _line(mask, axis, region):
    """Centre of the axis line: rows (axis 0) or columns (axis 1) with the longest run."""
    r0, r1 = region
    sub = mask[r0:r1] if axis == 0 else mask[:, r0:r1].T
    lens = np.array([_longest(s) for s in sub])
    best = np.flatnonzero(lens >= 0.97 * lens.max())
    grp = [best[0]]
    for i in best[1:]:
        if i - grp[-1] == 1:
            grp.append(i)
        else:
            break
    lo, hi = grp[0], grp[-1]  # widen to the anti-aliased edges of a thick line
    while lo > 0 and lens[lo - 1] >= 0.5 * lens.max():
        lo -= 1
    while hi < len(lens) - 1 and lens[hi + 1] >= 0.5 * lens.max():
        hi += 1
    return r0 + lo, r0 + hi  # first and last row/column of the line


def _ticks(mask, lo_line, hi_line, span, side, along_rows, min_len, max_len):
    """Ticks standing on a line (rows lo_line..hi_line if along_rows else columns)."""
    out = []
    lengths = []
    for c in range(span[0], span[1]):
        n_in = n_out = 0
        if along_rows:  # x axis: ticks go up ("in") or down ("out") from the line
            k = lo_line - 1
            while k >= 0 and mask[k, c]:
                n_in += 1
                k -= 1
            k = hi_line + 1
            while k < mask.shape[0] and mask[k, c]:
                n_out += 1
                k += 1
        else:  # y axis: ticks go right ("in") or left ("out")
            k = hi_line + 1
            while k < mask.shape[1] and mask[c, k]:
                n_in += 1
                k += 1
            k = lo_line - 1
            while k >= 0 and mask[c, k]:
                n_out += 1
                k -= 1
        n = {"in": n_in, "out": n_out, "both": max(n_in, n_out)}[side]
        lengths.append(n if min_len <= n <= max_len else 0)
    cur = []
    for i, n in enumerate(lengths + [0]):
        if n:
            cur.append(i)
        elif cur:
            if len(cur) <= 30:
                out.append((span[0] + (cur[0] + cur[-1] + 1) / 2.0, max(lengths[j] for j in cur)))
            cur = []
    return out


def calibrate(image, spec):
    fmask = mask_of(image, spec.get("frame", "black"))
    H, W = fmask.shape
    xr = spec.get("x_row_region", [H // 2, H])
    yc = spec.get("y_col_region", [0, W // 2])
    xa = _line(fmask, 0, xr)
    ya = _line(fmask, 1, yc)
    x_row = (xa[0] + xa[1] + 1) / 2
    y_col = (ya[0] + ya[1] + 1) / 2
    sx, sy = spec["x"], spec["y"]
    xt = _ticks(fmask, xa[0], xa[1], (ya[1] + 3, sx.get("span_end", W)), sx.get("side", "in"),
                True, sx.get("min_len", 6), sx.get("max_len", 200))
    yt = _ticks(fmask, ya[0], ya[1], (sy.get("span_start", 0), xa[0] - 3), sy.get("side", "in"),
                False, sy.get("min_len", 6), sy.get("max_len", 200))
    xt = [p for p, n in xt if n >= sx.get("major_len", 0)]
    yt = sorted([p for p, n in yt if n >= sy.get("major_len", 0)], reverse=True)  # bottom first
    for name, found, s in (("x", xt, sx), ("y", yt, sy)):
        if s.get("drop"):
            found[:] = [p for i, p in enumerate(found) if i not in s["drop"]]
        if len(found) != len(s["ticks"]):
            raise ValueError(f"{name}: found {len(found)} ticks at {[round(p) for p in found]}, "
                             f"expected {len(s['ticks'])} for {s['ticks']}")
    xp, xv = list(xt), list(sx["ticks"])
    if sx.get("at_axis") is not None:
        xp.insert(0, y_col)
        xv.insert(0, sx["at_axis"])
    yp, yv = list(yt), list(sy["ticks"])
    if sy.get("at_axis") is not None:
        yp.insert(0, x_row)
        yv.insert(0, sy["at_axis"])
    X = Axis(xp, xv, sx.get("log", False))
    Y = Axis(yp, yv, sy.get("log", False))
    return X, Y, {"x_row": x_row, "y_col": y_col, "x_line": xa, "y_line": ya}


def curve_mask(image, spec, ax):
    m = mask_of(image, spec["ink"])
    out = np.zeros_like(m)
    pad = spec.get("pad", 6)
    top = spec.get("top_row", 0)
    right = spec.get("right_col", m.shape[1])
    out[top:ax["x_line"][0] - pad, ax["y_line"][1] + pad:right] = \
        m[top:ax["x_line"][0] - pad, ax["y_line"][1] + pad:right]
    for x0, y0, x1, y1 in spec.get("blank", []):
        out[y0:y1, x0:x1] = False
    part = spec.get("part", "all")
    if part != "all":
        lab, n = ndimage.label(out, structure=np.ones((3, 3)))
        sl = ndimage.find_objects(lab)
        keep = np.zeros(n + 1, bool)
        for i, s in enumerate(sl, start=1):
            w = s[1].stop - s[1].start
            h = s[0].stop - s[0].start
            big = max(w, h) >= spec.get("min_solid", 400)
            keep[i] = big if part == "solid" else not big
        out = keep[lab]
    return out


def _pick(mask, c, rank, band_rows):
    rr = [(a, b) for a, b in runs(mask[:, c])
          if band_rows is None or (band_rows[0] <= (a + b) / 2 <= band_rows[1])]
    rr.sort(key=lambda ab: -ab[0])  # bottom first
    if rank < 0:
        rank = len(rr) + rank
        if rank < 0:
            return None
    if rank >= len(rr):
        return None
    return rr[rank]


def read_curve(image, at, spec):
    X, Y, ax = calibrate(image, spec)
    mis_x, mis_y = X.misfit, Y.misfit
    mask = curve_mask(image, spec, ax)
    w = spec.get("w", 10)
    rank = spec.get("rank", 0)
    fit_px = spec.get("fit_px", 60)
    out = []
    for x in at:
        c = int(round(X.px(x)))
        band = None
        if spec.get("band"):
            b0, b1 = spec["band"](x) if callable(spec["band"]) else spec["band"]
            band = sorted([Y.px(b0), Y.px(b1)])
        if c < 0 or c >= mask.shape[1]:
            out.append({"x": x, "y": None, "note": "outside the crop"})
            continue
        cols = range(max(c - fit_px, 0), min(c + fit_px + 1, mask.shape[1]))
        slope = 0.0
        th = w
        for _ in range(2):  # the line's vertical thickness grows with its slope
            pts = []
            for cc in cols:
                r = _pick(mask, cc, rank, band)
                if r and r[1] - r[0] <= th + 4:
                    pts.append((cc, (r[0] + r[1] - 1) / 2))
            if len(pts) >= 5:
                pc = np.array(pts, float)
                deg = 2 if len(pts) >= 10 else 1
                coef = np.polyfit(pc[:, 0] - c, pc[:, 1], deg)
                slope = float(coef[-2])
                resid = float(np.max(np.abs(np.polyval(coef, pc[:, 0] - c) - pc[:, 1])))
            th = w * math.sqrt(1 + slope * slope)
        r = _pick(mask, c, rank, band)
        kind = None
        if r and r[1] - r[0] <= th + 4:
            ctr = (r[0] + r[1] - 1) / 2
            top_row, bot_row = ctr - 2 - mis_y, ctr + 2 + mis_y
            kind = "clean run"
        elif r and r[1] - r[0] <= spec.get("max_fused", 60):
            ctr = (r[0] + r[1] - 1) / 2
            top_row, bot_row = r[0] - 2 - mis_y, r[1] - 1 + 2 + mis_y
            kind = f"run of {r[1] - r[0]} px, fused with another line"
        elif len(pts) >= 10 and resid < spec.get("max_resid", 10):
            ctr = float(coef[-1])
            pad = 3 + 2 * resid + mis_y
            top_row, bot_row = ctr - pad, ctr + pad
            kind = f"gap in the line; centre from a quadratic fit to {len(pts)} columns (residual {resid:.1f} px)"
        else:
            out.append({"x": x, "y": None, "px": [c, None],
                        "note": "the chosen line is not found in this column"})
            continue
        ext = abs(slope) * (mis_x + 1)
        top_row -= ext
        bot_row += ext
        y, y1, y2 = Y.val(ctr), Y.val(top_row), Y.val(bot_row)
        out.append({"x": x, "y": float(y), "lo": float(min(y1, y2)), "hi": float(max(y1, y2)),
                    "px": [c, float(ctr)], "px_lo": float(top_row), "px_hi": float(bot_row),
                    "note": f"{kind}; calibration misfit x {mis_x:.1f} px, y {mis_y:.1f} px"})
    return out


def read_markers(image, spec):
    X, Y, ax = calibrate(image, spec)
    mis = max(X.misfit, Y.misfit)
    m = curve_mask(image, dict(spec, part="all"), ax)
    m = ndimage.binary_closing(m, iterations=2)
    holes = ndimage.binary_fill_holes(m) & ~m  # fill only small holes (hollow markers), not
    hl, hn = ndimage.label(holes)              # regions closed off between two curves
    if hn:
        sizes = ndimage.sum(holes, hl, range(1, hn + 1))
        small = np.concatenate([[False], sizes <= spec.get("hole_max", 3000)])
        m = m | small[hl]
    if spec.get("open"):
        m = ndimage.binary_opening(m, iterations=spec["open"])
    if spec.get("core"):
        # keep only the cores of round markers: pixels farther than `core` px from any background
        # pixel; lines, text strokes and arrowheads are thinner than 2 * core and drop out
        m = ndimage.distance_transform_edt(m) >= spec["core"]
    lab, n = ndimage.label(m)
    amin, amax = spec["area"]
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if not (amin <= len(ys) <= amax):
            continue
        h = ys.max() - ys.min() + 1
        wd = xs.max() - xs.min() + 1
        if max(h, wd) > spec.get("max_aspect", 1.6) * min(h, wd):
            continue
        cx, cy = xs.mean() + 0.5, ys.mean() + 0.5
        pad = mis + spec.get("pad_px", 2)
        out.append({"x": float(X.val(cx)), "y": float(Y.val(cy)),
                    "lo": float(min(Y.val(cy + pad), Y.val(cy - pad))),
                    "hi": float(max(Y.val(cy + pad), Y.val(cy - pad))),
                    "px": [float(cx), float(cy)], "px_lo": float(cy - pad), "px_hi": float(cy + pad),
                    "note": f"marker centroid, area {len(ys)} px, x read {X.val(cx):.4g} "
                            f"(+- {abs(X.val(cx + pad) - X.val(cx)):.2g}); calibration misfit {mis:.1f} px"})
    out.sort(key=lambda d: d["x"])
    # a core much smaller or larger than the typical one belongs to a marker partly hidden by, or
    # merged with, other ink: its centroid may be off by up to a marker radius, so widen its interval
    areas = [int(d["note"].split("area ")[1].split(" ")[0]) for d in out]
    if areas:
        med = float(np.median(areas))
        extra = spec.get("partial_px", 12)
        for d, a in zip(out, areas):
            if abs(a - med) > 0.4 * med:
                cy = d["px"][1]
                pad = mis + spec.get("pad_px", 2) + extra
                d.update(lo=float(min(Y.val(cy + pad), Y.val(cy - pad))),
                         hi=float(max(Y.val(cy + pad), Y.val(cy - pad))),
                         px_lo=float(cy - pad), px_hi=float(cy + pad),
                         note=d["note"] + f"; core area far from the typical {med:.0f} px (marker partly "
                                          f"hidden or merged), interval widened by {extra} px")
    if spec.get("pick"):
        # two series in one colour: group points by x (within `x_tol` px) and keep the upper or
        # lower point of each group; at the x values in `pick_flip_x` the other one
        tol = spec.get("x_tol", 25)
        groups = []
        for d in out:
            if groups and abs(d["px"][0] - groups[-1][-1]["px"][0]) <= tol:
                groups[-1].append(d)
            else:
                groups.append([d])
        kept = []
        for grp in groups:
            upper = spec["pick"] == "upper"
            if any(abs(grp[0]["x"] - f) < 0.03 for f in spec.get("pick_flip_x", [])):
                upper = not upper
            d = max(grp, key=lambda e: e["y"]) if upper else min(grp, key=lambda e: e["y"])
            if len(grp) == 1:
                d = dict(d, note=d["note"] + "; the only point at this g, kept in both series")
            kept.append(d)
        out = kept
    return out


def read_vline(image, at, spec):
    """A vertical dashed line (a threshold marked on the g axis), read as its g for each requested
    y position (the reading's x is the y-axis quantity, its y the x-axis value of the line).

    Columns inside the plot box whose count of line ink is at least `min_frac` of the box height
    and whose ink is split into at least `min_dashes` runs with a median length of at least
    `min_dash_len` px (a dashed line; rotated text gives short runs) are grouped; groups wider
    than `max_width` px are dropped (text). The `index`-th group from the left is the line; its
    centre is the ink-weighted mean column, +- (1 px + x misfit + half the group's width beyond the
    line's own width)."""
    X, Y, ax = calibrate(image, spec)
    m = mask_of(image, spec.get("ink", "black"))
    pad = spec.get("pad", 14)
    top = spec.get("top_row", pad)
    r0, r1 = top, ax["x_line"][0] - pad
    c0, c1 = ax["y_line"][1] + pad, spec.get("right_col", m.shape[1] - pad)
    box = np.zeros_like(m)
    box[r0:r1, c0:c1] = m[r0:r1, c0:c1]
    for x0, y0, x1, y1 in spec.get("blank", []):
        box[y0:y1, x0:x1] = False
    H = r1 - r0
    cnt = box.sum(axis=0)
    def dashed(c):
        rr = runs(box[:, c])
        return (len(rr) >= spec.get("min_dashes", 4)
                and np.median([b - a for a, b in rr]) >= spec.get("min_dash_len", 30))

    ok = [c for c in range(c0, c1) if cnt[c] >= spec.get("min_frac", 0.15) * H and dashed(c)]
    groups, cur = [], []
    for c in ok:
        if cur and c != cur[-1] + 1:
            groups.append(cur)
            cur = []
        cur.append(c)
    if cur:
        groups.append(cur)
    groups = [g for g in groups if len(g) <= spec.get("max_width", 20)]
    k = spec.get("index", 0)
    if k >= len(groups):
        return [{"x": a, "y": None, "note": f"found {len(groups)} dashed vertical lines, wanted number {k}"} for a in at]
    cols = np.array(groups[k], float)
    wts = cnt[groups[k]].astype(float)
    ctr = float((cols * wts).sum() / wts.sum()) + 0.5
    rows = np.flatnonzero(box[:, groups[k]].any(axis=1))
    half = 1 + X.misfit + max(0, (len(cols) - spec.get("w", 6)) / 2)
    g, g1, g2 = X.val(ctr), X.val(ctr - half), X.val(ctr + half)
    out = []
    for a in at:
        ra = Y.px(a)
        if not (rows.min() - 30 <= ra <= rows.max() + 30):
            out.append({"x": a, "y": None, "note": "the line does not reach this height"})
            continue
        out.append({"x": a, "y": float(g), "lo": float(min(g1, g2)), "hi": float(max(g1, g2)),
                    "px": [ctr, float(ra)],
                    "note": f"dashed vertical line {len(cols)} px wide at column {ctr:.1f}, "
                            f"rows {rows.min()}-{rows.max()}; calibration misfit x {X.misfit:.1f} px"})
    return out


def load(path):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("tallinen2015_tal", Path(path).with_name("_tal.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
