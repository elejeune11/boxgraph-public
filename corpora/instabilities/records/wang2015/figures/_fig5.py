"""Shared reading code for Fig. 5 (p. 7) of wang2015: axis calibration from the
tick marks, the black theory curve, and coloured markers with error bars.

Calibration: the frame of each panel carries inward tick marks on all four sides.
They are found as short dark runs next to the frame, grouped, and matched in order
to the printed labels (Fig. 5A: x 0.4 ... 1 and y 0.4 ... 1; Fig. 5B: x 0.6 ... 1 and
y 0 ... 0.2). The two frame edges that carry no label are dropped. The axis maps are
straight-line fits; the misfit (largest residual, in pixels) widens every interval.

Markers: every point is a marker with an error bar (stem with a cap at each end) in the
series' colour. Markers crowd and overlap, so each reading file gives one seed per marker
(a pixel position placed by eye near it); everything else is measured around the seed:
the stem column (median centre of the narrow coloured stroke above and below the marker),
the bar ends (followed up and down the stem, bridging gaps of up to 30 px where the theory
line or another marker covers it, to the cap, whose centre row is the end), and the marker
centre (the middle of the rows near the seed where the coloured stroke is clearly wider
than the stem). The interval is a quarter of the marker's height (at least 6 px) plus the
calibration misfit; a seed flagged as overlapping or hidden gets the marker's whole
half-height (at least 25 px). Where no marker can be measured, the seed row is used with a
25 px interval, and the note says so.
"""
import numpy as np
from scipy import ndimage as ndi


def _groups(idx):
    out, cur = [], []
    for i in list(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            out.append((cur[0] + cur[-1]) / 2.0)
            cur = []
        if i is not None:
            cur.append(int(i))
    return out


def dark_mask(img):
    img = img.astype(int)
    gray = img.mean(2)
    sat = img.max(2) - img.min(2)
    return (gray < 110) & (sat < 60)


def frame(img):
    """The plot frame: the longest dark rows and columns."""
    d = dark_mask(img)
    H, W = d.shape
    rows = np.nonzero(d.sum(1) > 0.6 * W)[0]
    cols = np.nonzero(d.sum(0) > 0.5 * H)[0]
    top, bot = _groups(rows)[0], _groups(rows)[-1]
    left, right = _groups(cols)[0], _groups(cols)[-1]
    return left, top, right, bot


def ticks(img):
    """Tick positions (centres) along the bottom (x) and left (y) edges, frame edges included."""
    d = dark_mask(img)
    c0, r0, c1, r1 = [int(round(v)) for v in frame(img)]
    cnt = d[r1 - 30:r1 - 2, c0 - 5:c1 + 6].sum(0)
    xs = [c + c0 - 5 for c in _groups(np.nonzero(cnt >= 12)[0])]
    cnt = d[r0 - 5:r1 + 6, c0 + 3:c0 + 31].sum(1)
    ys = [r + r0 - 5 for r in _groups(np.nonzero(cnt >= 12)[0])]
    return xs, ys


class Lin:
    def __init__(self, px, vals):
        px, vals = np.asarray(px, float), np.asarray(vals, float)
        self.b, self.a = np.polyfit(px, vals, 1)
        self.misfit = float(np.max(np.abs(px - (vals - self.a) / self.b)))
        self.misfit = max(self.misfit, 0.5)

    def val(self, p):
        return self.a + self.b * p

    def px(self, v):
        return (v - self.a) / self.b


def calibrate(img, x_labels, y_labels, x_drop, y_drop):
    """x_labels left to right, y_labels top to bottom; x_drop / y_drop: indexes of
    unlabelled ticks (frame edges) to leave out, counted in the found order."""
    xs, ys = ticks(img)
    xs = [x for i, x in enumerate(xs) if i not in x_drop]
    ys = [y for i, y in enumerate(ys) if i not in y_drop]
    if len(xs) != len(x_labels) or len(ys) != len(y_labels):
        raise ValueError(f"ticks found {xs} {ys} do not match the labels")
    return Lin(xs, x_labels), Lin(ys, y_labels)


# ---------------------------------------------------------------- colours
def colour_mask(img, name):
    img = img.astype(int)
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    mag = (R > G + 60) & (B > G + 60) & (np.abs(R - B) < 90)
    if name == "blue":
        return (B > R + 60) & (B > G + 60)
    if name == "magenta":
        return mag
    if name == "red":
        return (R > G + 70) & (R > B + 70) & ~mag
    if name == "green":
        return (G > R + 40) & (G > B + 40)
    if name == "yellow":
        return (R > B + 70) & (G > B + 70) & (np.abs(R - G) < 70)
    if name == "brown":
        return (R > G + 50) & (R > B + 60) & (G > B - 10) & (np.abs(R - G) >= 50) & (R < 235)
    raise ValueError(name)


def calibrate_5a(img):
    """Fig. 5A: x ticks 0.4 ... 1 (the right frame edge, unlabelled, dropped); y ticks
    1 ... 0.4 from the top (the top frame edge and the unlabelled 0.3 tick on the bottom
    frame dropped)."""
    return calibrate(img, [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4],
                     x_drop={7}, y_drop={0, 8})


def calibrate_5b(img):
    """Fig. 5B: x ticks 0.6 ... 1 (both frame edges are labelled); y ticks 0.2 ... 0 from the top."""
    return calibrate(img, [0.6, 0.7, 0.8, 0.9, 1.0], [0.2, 0.15, 0.1, 0.05, 0.0], x_drop=set(), y_drop=set())


def _follow(mask, col, r, step, half=5, gap=30, limit=400):
    """Last row of the stem reached from row r going in direction step (+1 down, -1 up)."""
    c = int(round(col))
    last, miss, rr = r, 0, r
    H = mask.shape[0]
    for _ in range(limit):
        rr += step
        if not (0 <= rr < H):
            break
        if mask[rr, c - half:c + half + 1].any():
            last, miss = rr, 0
        else:
            miss += 1
            if miss > gap:
                break
    return last


def _width(mask, row, col, reach):
    c = int(round(col))
    on = np.nonzero(mask[int(row), c - reach:c + reach + 1])[0]
    if len(on) == 0:
        return 0
    # only the run containing (or nearest) the stem
    centre = reach
    runs, start = [], on[0]
    for a, b in zip(on[:-1], on[1:]):
        if b - a > 3:
            runs.append((start, a))
            start = b
    runs.append((start, on[-1]))
    s, e = min(runs, key=lambda t: 0 if t[0] <= centre <= t[1] else min(abs(t[0] - centre), abs(t[1] - centre)))
    return e - s + 1


def read_seeded(img, xa, ya, colour, seeds, box, marker_reach=45, cap_reach=30, stem_half=5):
    """One reading per seed (column, row) placed near a marker: the stem column, the two
    error-bar caps and the marker centre are all measured from the image around the seed.
    A seed given as (column, row, "note") carries a remark (e.g. overlapping markers)
    that widens the interval to the whole marker."""
    mask = colour_mask(img, colour)
    c0, r0, c1, r1 = [int(round(v)) for v in box]
    inner = np.zeros_like(mask)
    inner[r0 + 4:r1 - 3, c0 + 4:c1 - 3] = mask[r0 + 4:r1 - 3, c0 + 4:c1 - 3]
    mask = inner
    out = []
    for seed in seeds:
        c, r = seed[0], seed[1]
        remark = seed[2] if len(seed) > 2 else ""
        # stem column: centroid of coloured pixels in a narrow window, away from the marker
        cols = []
        for rr in list(range(int(r) - 140, int(r) - 40)) + list(range(int(r) + 40, int(r) + 140)):
            if 0 <= rr < mask.shape[0]:
                on = np.nonzero(mask[rr, int(c) - 10:int(c) + 11])[0]
                if 0 < len(on) <= 2 * stem_half + 8:
                    cols.append(on.mean() + int(c) - 10)
        sc = float(np.median(cols)) if len(cols) >= 10 else float(c)
        top = _follow(mask, sc, int(r), -1, half=stem_half)
        bot = _follow(mask, sc, int(r), +1, half=stem_half)
        sw = 2 * stem_half + 3

        def cap(end, step):
            rows = [rr for rr in range(end, end + step * 22, step) if _width(mask, rr, sc, cap_reach) >= sw + 8]
            return (float(np.mean(rows)), (max(rows) - min(rows) + 1) / 2.0) if rows else (end + step * 5.0, 6.0)

        top_c, top_h = cap(top, +1)
        bot_c, bot_h = cap(bot, -1)
        wide = [rr for rr in range(int(r) - marker_reach, int(r) + marker_reach + 1)
                if top_c + top_h + 3 < rr < bot_c - bot_h - 3 and _width(mask, rr, sc, marker_reach) >= sw + 6]
        if len(wide) >= 6:
            row = (wide[0] + wide[-1]) / 2.0
            half = (wide[-1] - wide[0]) / 2.0
            err_px = max(6.0, half / 2.0)
            how = f"marker centre (marker {wide[-1] - wide[0] + 1} px tall)"
        else:
            row, half = float(r), 25.0
            err_px = 25.0
            how = "marker not found: seed row, interval the marker's size"
        if remark:
            err_px = max(err_px, half, 25.0)  # anywhere within a marker's half-height
            how += f"; {remark}"
        err_px += ya.misfit
        y = float(ya.val(row))
        lo, hi = sorted((float(ya.val(row + err_px)), float(ya.val(row - err_px))))
        e_top, e_bot = top_h + ya.misfit, bot_h + ya.misfit
        out.append({"x": float(xa.val(sc)), "y": y, "lo": lo, "hi": hi, "px": [sc, row],
                    "px_lo": row - err_px, "px_hi": row + err_px,
                    "bar_hi": float(ya.val(top_c)), "bar_lo": float(ya.val(bot_c)),
                    "bar_hi_outer": float(ya.val(top_c - e_top)), "bar_lo_outer": float(ya.val(bot_c + e_bot)),
                    "note": f"{how}; stem at column {sc:.0f} (x misfit {xa.misfit:.1f} px); "
                            f"caps at rows {top_c:.0f} and {bot_c:.0f}"})
    out.sort(key=lambda d: d["x"])
    return out


def read_black_curve(img, xa, ya, at, box, exclude=None):
    """The black theory curve at the given x: middle of the dark run nearest the curve's trend."""
    d = dark_mask(img)
    c0, r0, c1, r1 = [int(round(v)) for v in box]
    m = np.zeros_like(d)
    m[r0 + 8:r1 - 8, c0 + 8:c1 - 8] = d[r0 + 8:r1 - 8, c0 + 8:c1 - 8]
    if exclude is not None:  # legend area: (c0, r0, c1, r1)
        a, b, c, e = exclude
        m[b:e, a:c] = False
    m = ndi.binary_opening(m, structure=np.ones((3, 3)))
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    # the curve is cut into pieces where markers lie on it: keep every large piece
    keep = [i + 1 for i, s in enumerate(sizes) if s >= 0.05 * sizes.max()]
    curve = np.isin(lab, keep)
    out = []
    for x in at:
        p = xa.px(x)
        c = int(round(p))
        rows = np.nonzero(curve[:, c - 1:c + 2].any(1))[0]
        if len(rows) == 0:
            out.append({"x": x, "y": None, "note": "curve not found at this x"})
            continue
        rmin, rmax = rows.min(), rows.max()
        if rmax - rmin > 60:
            out.append({"x": x, "y": None, "note": "curve run too tall here"})
            continue
        row = (rmin + rmax) / 2.0
        half = (rmax - rmin + 1) / 2.0
        err = half + ya.misfit
        y = float(ya.val(row))
        lo, hi = sorted((float(ya.val(row + err)), float(ya.val(row - err))))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [p, row], "px_lo": row - err, "px_hi": row + err,
                    "note": f"line {rmax - rmin + 1} px thick; calibration misfit {ya.misfit:.1f} px"})
    return out
