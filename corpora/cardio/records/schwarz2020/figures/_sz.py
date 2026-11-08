"""Shared reading code for the box plots and histograms of schwarz2020 (Figs. 2, 3, 4 and 6).
Vector art rendered at 600-800 dpi.

Inks, from the image:
  ink  : the axes, ticks, box outlines, medians, whiskers and caps: grey level < 160 and colourless
         (max - min channel < 50).  The grey dashed grid lines (about 204) and the blue fills are not ink.
  fill : the box or bar fill, given per figure as its colour(s) read off the crop (within 14 of it).

Axes: an axis line is the longest straight run of ink along a row (x axis) or column (y axis).
Ticks point outward (down from an x axis, left from a y axis).  The depth of ink beyond the axis
line is measured at every position along it; ticks are the runs of positions deeper than 10 px, and
long ticks the runs deeper than 0.8 of the deepest.  Each figure says which ticks carry which printed
values (the long ones, or all of them in order).  The value axis is a least-squares line through the
matched ticks; the misfit is the largest distance in pixels of a matched tick from it.

Box plots ('along' = the value axis direction, 'across' = the other).  The image is turned so that
the value axis runs along the rows.  A box is a group of fill components that overlap across (the
median line cuts a box's fill in two); components less than 30 px across are not boxes (grid dashes).
In the box's centre line (across):
  box edges (25th and 75th percentiles): the outline just outside the fill: fill edge -+ (w + 1)/2,
    w the outline width (measured on the median line, else 4 px);
  median: the ink run inside the fill extent;
  whisker ends: from each box edge, ink is followed outward along the centre line (gaps of up to 2 px
    bridged) to its end; the cap's centre is that end -+ w/2.  Where the whisker runs into an axis line
    the end is not separable from the axis: the interval reaches across the axis line, and the note says so.
Intervals (95%): the centre +-(w/2 + 1 px + misfit).

Histograms: in the column at a bin centre, the longest run of the bar's fill that reaches down to the
x axis line; the bar's top outline is the ink run just above it, and its centre is the value.  A bin
with no fill above the axis is not read (empty, or too low to draw).  Interval: the outline run
+-(1 px + misfit).
"""
import numpy as np


def runs(v):
    v = np.asarray(v, bool)
    d = np.diff(np.concatenate([[0], v.astype(int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def closed_runs(v, gap):
    out = []
    for a, b in runs(v):
        if out and a - out[-1][1] <= gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def ink_of(image):
    a = np.asarray(image, float)[..., :3]
    g = a.mean(axis=2)
    return (g < 160) & ((a.max(axis=2) - a.min(axis=2)) < 50)


def fill_of(image, colors, tol=14):
    a = np.asarray(image, float)[..., :3]
    m = np.zeros(a.shape[:2], bool)
    for c in colors:
        m |= np.sqrt(((a - np.array(c, float)) ** 2).sum(axis=2)) < tol
    return m


def axis_rows(k, min_len):
    """Rows holding horizontal ink runs of at least min_len: list of (row0, row1, col0, col1) per line."""
    H, W = k.shape
    cand = []
    for i in range(H):
        for a, b in closed_runs(k[i], 4):  # an axis line can show pixel gaps where ticks join it
            if b - a >= min_len:
                cand.append((i, a, b))
    lines = []
    for i, a, b in sorted(cand):
        for L in lines:
            ov = min(L[3], b) - max(L[2], a)
            if i - L[1] <= 1 and ov > 0.5 * min(L[3] - L[2], b - a):
                L[1], L[2], L[3] = i, min(L[2], a), max(L[3], b)
                break
        else:
            lines.append([i, i, a, b])
    return [tuple(L) for L in lines]


def axis_cols(k, min_len):
    return [(c0, c1, r0, r1) for c0, c1, r0, r1 in axis_rows(k.T, min_len)]


def depths_down(k, row, c0, c1):
    H = k.shape[0]
    d = np.zeros(k.shape[1], int)
    for j in range(max(c0, 0), min(c1, k.shape[1])):
        n = 0
        while row + 1 + n < H and k[row + 1 + n, j]:
            n += 1
        d[j] = n
    return d


def depths_left(k, col, r0, r1):
    d = np.zeros(k.shape[0], int)
    for i in range(max(r0, 0), min(r1, k.shape[0])):
        n = 0
        while col - 1 - n >= 0 and k[i, col - 1 - n]:
            n += 1
        d[i] = n
    return d


def ticks(dep, long=False):
    if long:
        return [(a + b - 1) / 2 for a, b in runs(dep > 0.8 * dep.max())]
    return [(a + b - 1) / 2 for a, b in runs(dep > 10)]


class Axis:
    def __init__(self, pos, vals, log=False, what=""):
        pos = np.asarray(pos, float)
        v = np.log10(vals) if log else np.asarray(vals, float)
        self.a, self.b = np.polyfit(pos, v, 1)
        self.log = log
        self.mis = max(float(np.max(np.abs((v - self.b) / self.a - pos))), 0.5)
        self.note = f"{what} ticks at {[round(p) for p in pos]} = {list(vals)}, misfit {self.mis:.2f} px"

    def val(self, p):
        v = self.a * p + self.b
        return float(10 ** v) if self.log else float(v)

    def pos(self, v):
        return ((np.log10(v) if self.log else v) - self.b) / self.a


def _walk(k, c, r, step, n, stop=None):
    """Follow ink from row r in direction step along column c (bridging gaps of up to 2 px), not
    into an axis line (rows `stop`, a (first, last) pair): a tick may continue the line beyond it."""
    last, gap = None, 0
    while 0 <= r < n:
        if stop and stop[0] - 1 <= r <= stop[1] + 1:
            return stop[0] - 1 if step > 0 else stop[1] + 1

        if k[r, c]:
            last, gap = r, 0
        else:
            gap += 1
            if gap > 2:
                break
        r += step
    return last


def boxes(image, fill_colors, axis, vertical, stop_rows=(), min_along=4):
    """All boxes, each a dict of the five statistics (value, lo, hi, px, note), sorted across.
    vertical: True when the boxes stand upright (value along image rows)."""
    k = ink_of(image)
    f = fill_of(image, fill_colors)
    if not vertical:
        k, f = k.T, f.T
    from scipy import ndimage
    lab, n = ndimage.label(f)
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        rs, cs = sl
        solid = (lab[sl] == i + 1).mean() > 0.5  # a box's fill is solid; anti-aliased text is not
        # thin slivers of a near-white fill are the anti-aliased edges of lines, not fill (min_along
        # is lowered where the fill colour cannot arise from anti-aliasing and boxes are small)
        if cs.stop - cs.start >= 30 and rs.stop - rs.start >= min_along and solid:
            comps.append([cs.start, cs.stop, rs.start, rs.stop])
    comps.sort()
    groups = []
    for c in comps:
        if groups and c[0] < groups[-1][1] - 5:
            g = groups[-1]
            g[1], g[2], g[3] = max(g[1], c[1]), min(g[2], c[2]), max(g[3], c[3])
        else:
            groups.append(list(c))
    out = []
    n = k.shape[0]
    for c0, c1, r0, r1 in groups:
        c = (c0 + c1 - 1) // 2
        cols = [c - 3, c, c + 3]
        # median: ink inside the fill extent in the centre column, away from the outline
        inner = [(a, b) for a, b in runs(k[r0:r1, c]) if a > 0 and b < r1 - r0]
        w = float(np.median([b - a for a, b in inner])) if inner else 4.0
        med = None
        if inner:
            a, b = max(inner, key=lambda t: t[1] - t[0])
            med = (r0 + (a + b - 1) / 2, "median line")
        e_top = r0 - (w + 1) / 2
        e_bot = (r1 - 1) + (w + 1) / 2
        # whiskers: from each edge outward along the centre line
        ends = {}
        for side, start, step in (("top", r0 - 1, -1), ("bot", r1, 1)):
            last = None
            for cc in cols:
                L = _walk(k, cc, start, step, n, (min(stop_rows), max(stop_rows)) if stop_rows else None)
                if L is not None and (last is None or (L - last) * step > 0):
                    last = L
            note = "whisker cap"
            ext = 0.0
            if last is None:
                last = start
            for sr in stop_rows:
                if abs(last - sr) <= w + 3:
                    note = "whisker end runs into the axis line: the interval reaches across it"
                    ext = w + 3
            ends[side] = (last - step * w / 2, note, ext)
        pad = w / 2 + 1 + axis.mis
        def stat(p, note, ext=0.0):
            v1, v2 = axis.val(p - pad - ext), axis.val(p + pad + ext)
            px = [float(c), float(p)] if vertical else [float(p), float(c)]
            return {"y": axis.val(p), "lo": min(v1, v2), "hi": max(v1, v2), "px": px, "note": note}
        st = {"edge_top": stat(e_top, "box edge"), "edge_bot": stat(e_bot, "box edge"),
              "end_top": stat(ends["top"][0], ends["top"][1], ends["top"][2]),
              "end_bot": stat(ends["bot"][0], ends["bot"][1], ends["bot"][2])}
        st["median"] = stat(med[0], med[1]) if med else {"y": None, "note": "no median line separable from the box edge"}
        out.append({"across": float(c), "c0": c0, "c1": c1, "stats": st, "w": w})
    return out


STAT_NAMES = ("whisker_lo", "q1", "median", "q3", "whisker_hi")


def by_stat(box, axis):
    """Map the geometric features of a box to the statistics (low end ... high end of the value axis)."""
    s = box["stats"]
    top_is_high = axis.a < 0  # value grows as the row number falls
    if top_is_high:
        return {"whisker_lo": s["end_bot"], "q1": s["edge_bot"], "median": s["median"],
                "q3": s["edge_top"], "whisker_hi": s["end_top"]}
    return {"whisker_lo": s["end_top"], "q1": s["edge_top"], "median": s["median"],
            "q3": s["edge_bot"], "whisker_hi": s["end_bot"]}


def emit(at, chosen, stat, axis_note):
    """chosen: x (as printed in `at`) -> box; returns the readings of one statistic."""
    out = []
    chosen = {float(key): v for key, v in chosen.items()}
    for x in at:
        b = chosen.get(float(x))
        if b is None:
            out.append({"x": float(x), "y": None, "note": "no box found for this class"})
            continue
        r = dict(b[stat])
        r["x"] = float(x)
        if r.get("y") is not None:
            r["note"] = f"{r['note']}; {axis_note}"
        out.append(r)
    return out


def bars(image, fill_colors, xaxis, yaxis, axis_row, centers):
    """Histogram bars: the value at each bin centre (x values)."""
    k = ink_of(image)
    f = fill_of(image, fill_colors)
    out = []
    for x in centers:
        cf = xaxis.pos(float(x))
        c = int(round(cf))
        rr = [(a, b) for a, b in runs(f[:axis_row, c]) if b >= axis_row - 12]
        if not rr:
            out.append({"x": float(x), "y": None, "note": "no bar above the axis in this bin (empty or too low to draw)"})
            continue
        t = rr[-1][0]
        top_ink = [(a, b) for a, b in runs(k[:t, c]) if b >= t - 2]
        if not top_ink:
            out.append({"x": float(x), "y": None, "note": "bar outline not found"})
            continue
        a, b = top_ink[-1]
        r = (a + b - 1) / 2
        pad = 1 + yaxis.mis
        v1, v2 = yaxis.val(a - pad), yaxis.val(b - 1 + pad)
        out.append({"x": float(x), "y": yaxis.val(r), "lo": min(v1, v2), "hi": max(v1, v2),
                    "px": [float(cf), float(r)], "px_lo": float(b - 1 + pad), "px_hi": float(a - pad),
                    "note": f"top outline rows {a}-{b - 1}; {yaxis.note}; {xaxis.note}"})
    return out
