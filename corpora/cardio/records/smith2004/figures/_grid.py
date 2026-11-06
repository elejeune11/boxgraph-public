# Shared helpers for the figure readings of smith2004. Every plot in this paper is a
# MATLAB axes box: a solid frame and dotted gridlines at every labelled tick. Calibration
# comes from the image: the frame and the gridlines are found, their spacing gives the
# step in pixels, and one labelled line (an anchor: a frame edge or the lowest gridline,
# whose printed label the reading file names) plus the printed label step give each
# line's value. Lines are fitted by least squares; the misfit is the largest residual.
import numpy as np
from scipy import ndimage


def runs(v):
    """(start, end_exclusive) of each run of True in a 1-D boolean array."""
    v = np.asarray(v, dtype=bool)
    if not v.any():
        return []
    d = np.diff(np.concatenate([[0], v.astype(np.int8), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def longest_runs(mask, axis):
    """Longest run of True along `axis` (0: down each column, 1: along each row)."""
    m = mask if axis == 0 else mask.T
    best = np.zeros(m.shape[1], dtype=int)
    cur = np.zeros(m.shape[1], dtype=int)
    for row in m:
        cur = np.where(row, cur + 1, 0)
        best = np.maximum(best, cur)
    return best


def groups(idx):
    idx = np.asarray(idx)
    if idx.size == 0:
        return []
    return np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)


def ink_mask(image, thr=None):
    """Dark pixels: below the midpoint between the paper and the darkest ink."""
    g = image[:, :, :3].astype(float).mean(axis=2)
    if thr is None:
        thr = 0.5 * (np.percentile(g, 90) + np.percentile(g, 0.2))
    return g < thr


def thick(mask, size, disk=False):
    """Pixels of lines at least `size` pixels thick (drops dotted gridlines and hairlines).
    With `disk`, the probe is a disk of that diameter, which fits a line of that width at
    any angle (a square does not fit a diagonal line)."""
    if size <= 1:
        return mask.copy()
    if disk:
        yy, xx = np.mgrid[:size, :size]
        st = (yy - (size - 1) / 2) ** 2 + (xx - (size - 1) / 2) ** 2 <= ((size - 1) / 2) ** 2
    else:
        st = np.ones((size, size), bool)
    return ndimage.binary_opening(mask, structure=st)


def frame(ink, frac=0.6, mode="run"):
    """Candidate frame lines: the columns and rows whose longest continuous run of ink
    (mode 'run') or whose share of ink (mode 'frac': a solid line that a raster image has
    broken into pieces) is at least `frac` of the largest. Returns (columns, rows) as pixel
    centres; the caller picks the outermost."""
    if mode == "frac":
        cr, rr = ink.mean(axis=0), ink.mean(axis=1)
    else:
        cr, rr = longest_runs(ink, 0), longest_runs(ink, 1)
    cols = [float(gp.mean()) for gp in groups(np.flatnonzero(cr >= frac * cr.max()))]
    rows = [float(gp.mean()) for gp in groups(np.flatnonzero(rr >= frac * rr.max()))]
    return cols, rows


def gridlines(ink, lo, hi, a0, a1, axis, min_runs=6, max_run_frac=0.25, min_frac=0.03, rel_runs=0.4):
    """Dotted gridlines between pixels a0..a1 across the box, sampled over lo..hi along it.
    axis 0: vertical lines (columns); axis 1: horizontal lines (rows). A dotted line has
    many short runs of ink (at least rel_runs of the most dotted line); a curve, text or
    the frame crosses a line in few runs or one long one."""
    cand = []
    for p in range(int(a0), int(a1)):
        line = ink[int(lo):int(hi), p] if axis == 0 else ink[p, int(lo):int(hi)]
        rs = runs(line)
        if not rs:
            continue
        n = len(line)
        longest = max(e - s for s, e in rs)
        if len(rs) >= min_runs and longest < max_run_frac * n and line.mean() >= min_frac:
            cand.append((p, len(rs)))
    if not cand:
        return []
    top = max(k for _, k in cand)
    out = [p for p, k in cand if k >= rel_runs * top]
    return [float(gp.mean()) for gp in groups(np.array(out, dtype=int))]


class Axis:
    """Value <-> pixel for one axis, fitted to the lattice of labelled lines."""

    def __init__(self, grid, edges, anchor_px, anchor_val, step_val, increasing_px=True, tol=0.1):
        g = sorted(grid)
        if len(g) < 2 and anchor_px is not None and all(abs(anchor_px - x) > 5 for x in g):
            g = sorted(g + [anchor_px])  # few gridlines: the anchor line gives the step too
        if len(g) < 2:
            raise ValueError("fewer than two gridlines")
        d = np.diff(g)
        base = d.min()
        k = np.round(d / base)
        step_px = float(d.sum() / k.sum())
        sign = 1.0 if increasing_px else -1.0
        marks = []
        for p in sorted(set([round(x, 2) for x in g + [e for e in edges if e is not None]])):
            kk = sign * (p - anchor_px) / step_px
            if abs(kk - round(kk)) <= tol:
                marks.append((p, anchor_val + round(kk) * step_val))
        ps = np.array([m[0] for m in marks])
        vs = np.array([m[1] for m in marks])
        self.b, self.a = np.polyfit(ps, vs, 1)
        self.misfit = float(np.max(np.abs(self.a + self.b * ps - vs)))
        self.marks = marks
        self.step_px = step_px

    def val(self, p):
        return float(self.a + self.b * p)

    def px(self, v):
        return float((v - self.a) / self.b)

    def describe(self, name):
        lo, hi = self.marks[0][1], self.marks[-1][1]
        return f"{name}: {len(self.marks)} lines {lo:g}..{hi:g}, misfit {self.misfit:.3g}"


def column_runs(mask, col, r0, r1):
    """Runs of the mask in a column between rows r0..r1, as (top, bottom) inclusive rows."""
    return [(s + int(r0), e - 1 + int(r0)) for s, e in runs(mask[int(r0):int(r1), int(col)])]


def vertical_edges(mask, c0, c1, r0, r1, min_len_frac=0.15):
    """Vertical line segments inside the box: groups of columns whose longest run of the
    mask is at least min_len_frac of the box height. Returns (centre col, left col, right col,
    mid row of the longest run) for each, left to right."""
    sub = mask[int(r0):int(r1), int(c0):int(c1)]
    lr = longest_runs(sub, 0)
    out = []
    for gp in groups(np.flatnonzero(lr >= min_len_frac * sub.shape[0])):
        # weight the centre by run length, so the steep start of a curve beside a line counts less
        w = lr[gp].astype(float)
        c = float((gp * w).sum() / w.sum()) + c0
        best = int(gp[np.argmax(lr[gp])])
        rs = runs(sub[:, best])
        s, e = max(rs, key=lambda x: x[1] - x[0])
        out.append((c, float(gp[0] + c0), float(gp[-1] + c0), 0.5 * (s + e) + r0))
    return out


def arc_peaks(mask, c0, c1, r0, r1, reach_frac=0.04, rise_px=1.0, step=6):
    """Tops of arcs: points on the upper edge of the mask that are higher than the upper edge
    of the same line at every column within +-reach on both sides, and the line continues
    (an upper-edge pixel within `step` rows) across that reach. Text and arrowheads are too
    short to continue that far. Returns (col, top row) for each peak, left to right."""
    sub = mask[int(r0):int(r1), int(c0):int(c1)]
    H, W = sub.shape
    top = sub & ~np.vstack([np.zeros((1, W), bool), sub[:-1]])
    reach = max(3, int(reach_frac * W))
    tops = [np.flatnonzero(top[:, c]) for c in range(W)]
    peaks = []
    for c in range(reach, W - reach):
        for r in tops[c]:
            ok = True
            lower_somewhere = [False, False]
            for side, rng in ((0, range(c - 1, c - reach - 1, -1)), (1, range(c + 1, c + reach + 1))):
                prev = r
                for cc in rng:
                    cand = tops[cc][np.abs(tops[cc] - prev) <= step]
                    if cand.size == 0:
                        ok = False
                        break
                    nxt = int(cand[np.argmin(np.abs(cand - prev))])
                    if nxt < r:          # higher than the candidate: not a peak
                        ok = False
                        break
                    if nxt - r >= rise_px:
                        lower_somewhere[side] = True
                    prev = nxt
                if not ok:
                    break
            if ok and all(lower_somewhere):
                peaks.append((c, int(r)))
    # merge neighbours on the same flat top
    out = []
    for c, r in sorted(peaks):
        if out and c - out[-1][-1][0] <= 2 and abs(r - out[-1][-1][1]) <= 1:
            out[-1].append((c, r))
        else:
            out.append([(c, r)])
    res = []
    for gp in out:
        r = min(p[1] for p in gp)
        cs = [p[0] for p in gp if p[1] == r]
        res.append((float(np.mean(cs)) + c0, float(r) + r0, float(min(p[0] for p in gp)) + c0, float(max(p[0] for p in gp)) + c0))
    return res


def line_width(mask, c0, c1, r0, r1):
    """Commonest vertical run length of the mask inside the box: the line thickness of
    flat-ish curves."""
    sub = mask[int(r0):int(r1), int(c0):int(c1)]
    lens = []
    for c in range(0, sub.shape[1], 3):
        lens += [e - s for s, e in runs(sub[:, c])]
    if not lens:
        return 1
    v, n = np.unique(lens, return_counts=True)
    return int(v[np.argmax(n)])
