"""Shared reading code for the figures of Ursino 1998 (all scanned, black ink on white).

Everything is found in the image: the axis lines or plot frame, the tick marks or the dotted
grid lines (matched to the printed labels by the reading files), the curves, markers and bars.
Pixel coordinates are continuous: pixel (row i, column j) has its centre at (j + 0.5, i + 0.5).
"""

import math

import numpy as np
from scipy import ndimage


# ----------------------------------------------------------------------------------------------
# ink and runs


def ink(image, level=0.5):
    """Dark pixels: below `level` of the way from the paper to the darkest ink."""
    g = image[..., :3].astype(float).mean(axis=2)
    paper, dark = np.percentile(g, 99), np.percentile(g, 0.2)
    return g < paper - level * (paper - dark)


def runs(v):
    """(start, stop) of each run of True in a 1-D array."""
    d = np.diff(np.concatenate([[0], np.asarray(v, dtype=np.int8), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def longest_run(v, gap=2):
    """(length, start, stop) of the longest run of True, bridging gaps of up to `gap`."""
    rs = runs(v)
    best, cur = (0, 0, 0), None
    for a, b in rs:
        if cur is not None and a - cur[1] <= gap:
            cur = (cur[0], b)
        else:
            cur = (a, b)
        if cur[1] - cur[0] > best[0]:
            best = (cur[1] - cur[0], cur[0], cur[1])
    return best


def straighten(image, min_deg=0.05):
    """The scans are tilted by a few tenths of a degree. Rotate the crop so that its longest
    straight line (an axis) is level, and return the rotated image, the angle, and a function
    mapping a (column, row) of the rotated image back to the crop as rendered."""
    from PIL import Image

    from boxgraph.digitize import find_skew

    angle = find_skew(image)
    if abs(angle) < min_deg:
        return image, 0.0, (lambda c, r: (c, r))
    th = math.radians(-angle)  # PIL rotates counter-clockwise by -angle
    H, W = image.shape[:2]
    cx, cy = W / 2.0, H / 2.0
    im = Image.fromarray(image).rotate(-angle, resample=Image.BICUBIC, fillcolor=(255, 255, 255))

    def back(c, r):
        dx, dy = c - cx, r - cy
        return (cx + dx * math.cos(th) - dy * math.sin(th), cy + dx * math.sin(th) + dy * math.cos(th))

    return np.asarray(im).copy(), angle, back


def unrotate(out, back):
    """Map the pixel positions of readings made on a straightened image back to the crop."""
    for d in out:
        if "px" in d and d["px"] is not None and d.get("y") is not None:
            c, r = d["px"]
            d["px"] = list(back(c, r))
            for k in ("px_lo", "px_hi"):
                if k in d:
                    d[k] = back(c, d[k])[1]
        elif "px" in d and d["px"] is not None:
            d["px"] = [back(d["px"][0], d["px"][1])[0], d["px"][1]]
    return out


# ----------------------------------------------------------------------------------------------
# lines and axes


def long_lines(m, axis, min_len, gap=2):
    """Groups of adjacent rows (axis=0) or columns (axis=1) holding a run of ink at least
    `min_len` long: [(first, last + 1, run start, run stop)], in order."""
    a = m if axis == 0 else m.T
    hits = []
    for i in range(a.shape[0]):
        n, s, e = longest_run(a[i], gap)
        if n >= min_len:
            hits.append((i, s, e))
    groups = []
    for i, s, e in hits:
        if groups and i - groups[-1][1] <= 5:  # a scanned line can have a lighter streak in it
            g = groups[-1]
            groups[-1] = (g[0], i + 1, min(g[2], s), max(g[3], e))
        else:
            groups.append((i, i + 1, s, e))
    return groups


def tick_marks(m, line, axis, side, length=(6, 60), maxw=30, span=None):
    """Short marks standing perpendicular on an axis line.
    line: (first, stop) rows of a horizontal axis (axis=0) or columns of a vertical one (axis=1).
    side: -1 above / left of the line, +1 below / right of it. Returns mark centres (along the line)
    and their lengths."""
    a = m if axis == 0 else m.T
    lo, hi = line
    lmin, lmax = length
    if side < 0:
        probe = a[max(0, lo - lmin): lo, :].all(axis=0)
    else:
        probe = a[hi: hi + lmin, :].all(axis=0)
    out = []
    for s, e in runs(probe):
        if e - s > maxw:
            continue
        if span is not None and not (span[0] <= s and e <= span[1]):
            continue
        c = (s + e) / 2.0
        # its length: how far the ink goes on from the line
        cc = slice(s, e)
        n = 0
        while n < lmax + 2:
            r = lo - 1 - n if side < 0 else hi + n
            if r < 0 or r >= a.shape[0] or not a[r, cc].any():
                break
            n += 1
        if n <= lmax:
            out.append((c, n))
    return out


def evenly(cands, n, tol=0.02):
    """The n candidates (in order) that are most evenly spaced; raises if none is within tol."""
    import itertools

    c = sorted(cands)
    if len(c) < n:
        raise ValueError(f"only {len(c)} tick candidates, need {n}: {c}")
    best = None
    for sub in itertools.combinations(c, n):
        d = np.diff(sub)
        score = float(np.ptp(d) / np.mean(d))
        if best is None or score < best[0]:
            best = (score, list(sub))
    if best[0] > tol * n:
        raise ValueError(f"no evenly spaced set of {n} ticks among {c} (best spread {best[0]:.3f})")
    return best[1]


def dots(m, amax=400, dmax=30):
    """Small isolated blobs (the dots of dotted grid lines or dotted curves): (col, row, area)."""
    lab, n = ndimage.label(m)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h > dmax or w > dmax:
            continue
        rr, cc = np.nonzero(lab[sl] == i)
        if len(rr) > amax:
            continue
        out.append((cc.mean() + sl[1].start + 0.5, rr.mean() + sl[0].start + 0.5, len(rr)))
    return out


def grid_lines(pts, axis, min_count=8, tol=4.0):
    """Positions of dotted grid lines: rows (axis=0, horizontal lines) or columns (axis=1) where
    at least `min_count` dots line up within `tol` px."""
    v = sorted(p[1] if axis == 0 else p[0] for p in pts)
    groups, cur = [], []
    for x in v:
        if cur and x - cur[-1] > tol:
            groups.append(cur)
            cur = []
        cur.append(x)
    if cur:
        groups.append(cur)
    return [float(np.mean(g)) for g in groups if len(g) >= min_count]


# ----------------------------------------------------------------------------------------------
# calibration


class Cal:
    """value = a + b * pixel (in log10 of the value for a log axis), from (pixel, value) marks."""

    def __init__(self, marks, log=False):
        self.marks = [(float(p), float(v)) for p, v in marks]
        self.log = log
        p = np.array([m[0] for m in self.marks])
        u = np.array([math.log10(m[1]) if log else m[1] for m in self.marks])
        self.b, self.a = np.polyfit(p, u, 1)
        self.misfit = float(np.max(np.abs((u - self.a) / self.b - p))) if len(p) > 2 else 0.0
        self.err = max(self.misfit, 0.5)

    def val(self, px):
        u = self.a + self.b * px
        return 10.0 ** u if self.log else u

    def px(self, v):
        u = math.log10(v) if self.log else v
        return (u - self.a) / self.b


def axis_frame(m, min_frac=0.5):
    """The longest vertical line on the left (y axis) and the lowest long horizontal line
    (x axis), as (first, stop) pixel bands, with their extents."""
    H, W = m.shape
    v = long_lines(m, 1, int(min_frac * H))
    h = long_lines(m, 0, int(min_frac * W))
    if not v or not h:
        raise ValueError("axis lines not found")
    return dict(v=v, h=h)


# ----------------------------------------------------------------------------------------------
# reading


def column_runs(m, col):
    """(centre row, half height) of each run of ink in one column."""
    if not 0 <= col < m.shape[1]:
        return []
    return [((a + b) / 2.0, (b - a) / 2.0) for a, b in runs(m[:, col])]


def continuing(m, col, rs, reach=(8, 40), tol=None):
    """Of several runs in a column, the one the line continues through: nearest to where the
    single-run columns on either side (8 to 40 px away) put it, if it is within the run's height.
    None if that is not decided."""
    if len(rs) == 1:
        return rs[0]
    if not rs:
        return None
    left, right = [], []
    for k in range(reach[0], reach[1]):
        for side, c in ((left, col - k), (right, col + k)):
            q = column_runs(m, c)
            if len(q) == 1:
                side.append((c, q[0][0]))
    if not left or not right:
        return None
    (cl, yl), (cr, yr) = left[0], right[0]
    pred = yl + (yr - yl) * (col - cl) / float(cr - cl)
    best = min(rs, key=lambda q: abs(q[0] - pred))
    lim = tol if tol is not None else best[1] + 4
    return best if abs(best[0] - pred) <= lim else None


def read_line(m, xcal, ycal, at, pick=None, band=1, note_fn=None):
    """Read a curve drawn as the only (or chosen) ink run in each column of mask m.
    pick(col, runs) -> run or None chooses among several runs. The interval is the line's half
    height in the column, the calibration misfit, and the slope across the x calibration misfit."""
    out = []
    for x in at:
        pc = xcal.px(x)
        col = int(math.floor(pc))
        rs = column_runs(m, col)
        r = pick(col, rs) if pick else continuing(m, col, rs)
        if r is None:
            out.append({"x": x, "y": None, "px": [pc, 0.0],
                        "note": f"{len(rs)} runs of ink in this column; the curve cannot be told apart here"})
            continue
        centre, half = r
        nb = []
        for k in (-3, 3):
            rk = column_runs(m, col + k)
            if rk:
                nb.append(min(rk, key=lambda q: abs(q[0] - centre))[0])
        slope = (nb[1] - nb[0]) / 6.0 if len(nb) == 2 else 0.0
        e = half + 0.5 + abs(slope) * (xcal.err + abs(pc - col - 0.5)) + ycal.err
        y = ycal.val(centre)
        a, b = ycal.val(centre - e), ycal.val(centre + e)
        d = {"x": x, "y": y, "lo": min(a, b), "hi": max(a, b), "px": [pc, centre],
             "px_lo": centre - e, "px_hi": centre + e}
        if note_fn:
            d["note"] = note_fn(col, rs)
        out.append(d)
    return out


def point(xcal, ycal, col, row, err_px, note="", bar=None):
    """A reading of a plotted point at (col, row) with err_px of uncertainty in its centre; bar is
    (row of upper end, row of lower end, err_px of the ends) for an error bar."""
    y = ycal.val(row)
    a, b = ycal.val(row - err_px), ycal.val(row + err_px)
    d = {"x": xcal.val(col), "y": y, "lo": min(a, b), "hi": max(a, b), "px": [col, row],
         "px_lo": row - err_px, "px_hi": row + err_px}
    if note:
        d["note"] = note
    if bar is not None:
        top, bot, e = bar
        v1, v2 = ycal.val(top), ycal.val(bot)
        o1, o2 = ycal.val(top - e), ycal.val(bot + e)
        d["bar_lo"], d["bar_hi"] = min(v1, v2), max(v1, v2)
        d["bar_lo_outer"], d["bar_hi_outer"] = min(o1, o2), max(o1, o2)
    return d


def blobs(m, min_area=1):
    """Connected blobs: dicts with area, bbox (r0, r1, c0, c1), centroid, bbox centre and fill."""
    lab, n = ndimage.label(m)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        sub = lab[sl] == i
        rr, cc = np.nonzero(sub)
        if len(rr) < min_area:
            continue
        r0, r1, c0, c1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        out.append(dict(area=len(rr), r0=r0, r1=r1, c0=c0, c1=c1, h=r1 - r0, w=c1 - c0,
                        row=rr.mean() + r0 + 0.5, col=cc.mean() + c0 + 0.5,
                        brow=(r0 + r1) / 2.0, bcol=(c0 + c1) / 2.0,
                        fill=len(rr) / float((r1 - r0) * (c1 - c0)), mask=sub, label=i))
    return out


def opened(m, k):
    """Ink that survives an opening with a k x k square: solid shapes, without thin lines."""
    return ndimage.binary_opening(m, structure=np.ones((k, k), bool))


def holes(m, amin, amax):
    """Enclosed holes of the ink (inside open markers): blobs of the filled-in background."""
    filled = ndimage.binary_fill_holes(m)
    return [b for b in blobs(filled & ~m) if amin <= b["area"] <= amax]
