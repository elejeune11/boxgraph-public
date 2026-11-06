"""Shared reading code for the figures of Pries, Neuhaus & Gaehtgens 1992 (black line plots on
scanned pages, log diameter axis or linear hematocrit axis).

Everything is taken from the image:
- the scan's tilt is the tilt of the longest straight dark line (an axis); the crop is rotated
  straight and every pixel position returned is mapped back to the crop as rendered;
- the frame is the long dark rows and columns of the straightened crop;
- ticks are short dark runs that stick out of a frame line (outwards); a tick's printed label is
  matched by order (the labelled ticks are the longer ones);
- a curve is a run of ink crossing a column, chosen among the runs in that column by a rule
  stated in each reading (rank from the top or bottom, thickness).
"""

import math

import numpy as np
from PIL import Image

from boxgraph import digitize as dg


# ---------------------------------------------------------------- straightening
class Straight:
    """The crop rotated straight, with the map from straightened pixels back to the crop."""

    def __init__(self, image, angle=None):
        self.orig = image
        self.angle = dg.find_skew(image) if angle is None else angle
        h, w = image.shape[:2]
        self.cx, self.cy = w / 2.0, h / 2.0
        if abs(self.angle) < 0.02:
            self.img = image
            self.angle = 0.0
        else:
            im = Image.fromarray(image).rotate(-self.angle, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
            self.img = np.asarray(im).copy()
        g = self.img.astype(float).mean(axis=2)
        paper = float(np.percentile(g, 60))
        ink = float(np.percentile(g, 0.3))
        self.d = g < (paper + ink) / 2

    def back(self, col, row):
        """Straightened (col, row) -> (col, row) in the crop as rendered."""
        # PIL rotates the picture by -angle (counter-clockwise positive) about its centre; invert it
        t = math.radians(-self.angle)
        dx, dy = col - self.cx, row - self.cy
        x = self.cx + math.cos(t) * dx - math.sin(t) * dy
        y = self.cy + math.sin(t) * dx + math.cos(t) * dy
        return x, y


# ---------------------------------------------------------------- frame and ticks
def groups(idx, gap=1):
    out = []
    for i in idx:
        if out and i <= out[-1][1] + gap:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(g) for g in out]


def longest_run(v):
    best = cur = 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def long_rows(d, frac, r0=0, r1=None, c0=0, c1=None):
    sub = d[r0:r1, c0:c1]
    n = sub.shape[1]
    return groups([r0 + r for r in range(sub.shape[0]) if longest_run(sub[r]) >= frac * n])


def long_cols(d, frac, r0=0, r1=None, c0=0, c1=None):
    sub = d[r0:r1, c0:c1]
    n = sub.shape[0]
    return groups([c0 + c for c in range(sub.shape[1]) if longest_run(sub[:, c]) >= frac * n])


def ticks_off_hline(d, line, c0, c1, direction, min_len=8, max_width=30):
    """Ticks sticking out of horizontal line `line` = (first row, last row), direction +1 = down,
    -1 = up, over columns c0..c1. Returns [(centre column, length)]."""
    edge = line[1] if direction > 0 else line[0]
    lengths = {}
    for c in range(c0, c1):
        r, n = edge + direction, 0
        while 0 <= r < d.shape[0] and d[r, c]:
            n += 1
            r += direction
        lengths[c] = n
    keep = [c for c, n in sorted(lengths.items()) if n >= min_len]
    return [((a + b) / 2.0, max(lengths[q] for q in range(a, b + 1))) for a, b in groups(keep)
            if b - a + 1 <= max_width]


def ticks_off_vline(d, line, r0, r1, direction, min_len=8, max_width=30):
    """Ticks sticking out of vertical line `line` = (first col, last col), direction -1 = left,
    +1 = right, over rows r0..r1. Returns [(centre row, length)]."""
    edge = line[0] if direction < 0 else line[1]
    lengths = {}
    for r in range(r0, r1):
        c, n = edge + direction, 0
        while 0 <= c < d.shape[1] and d[r, c]:
            n += 1
            c += direction
        lengths[r] = n
    keep = [r for r, n in sorted(lengths.items()) if n >= min_len]
    return [((a + b) / 2.0, max(lengths[q] for q in range(a, b + 1))) for a, b in groups(keep)
            if b - a + 1 <= max_width]


def fit(pos, vals):
    """value = a + b * pixel, least squares; misfit in pixels (largest residual)."""
    pos, vals = np.asarray(pos, float), np.asarray(vals, float)
    A = np.vstack([np.ones_like(pos), pos]).T
    coef, *_ = np.linalg.lstsq(A, vals, rcond=None)
    res = vals - A @ coef
    mis = float(np.max(np.abs(res / coef[1]))) if len(pos) > 2 else 0.0
    return (float(coef[0]), float(coef[1])), mis


class Axis:
    def __init__(self, pos, vals, log=False):
        self.log = log
        self.pos = list(pos)
        self.vals = list(vals)
        (self.a, self.b), self.misfit = fit(pos, np.log10(vals) if log else vals)

    def value(self, px):
        v = self.a + self.b * px
        return 10 ** v if self.log else v

    def pixel(self, value):
        v = math.log10(value) if self.log else value
        return (v - self.a) / self.b


class PiecewiseAxis:
    """Linear interpolation between neighbouring ticks, for scans whose tick spacing is uneven
    (the reproduction stretched the page unevenly, and the curves with it). `misfit` (pixels) is
    the uncertainty of one tick position; `linear_misfit` says how uneven the ticks are."""

    def __init__(self, pos, vals, log=False, misfit=2.0):
        order = np.argsort(pos)
        self.pos = np.asarray(pos, float)[order]
        v = np.asarray(vals, float)[order]
        self.log = log
        self.v = np.log10(v) if log else v
        self.misfit = misfit
        _, self.linear_misfit = fit(self.pos, self.v)

    def _interp(self, xp, fp, x):
        # linear inside, extended with the end segments outside
        if x <= xp[0]:
            return fp[0] + (x - xp[0]) * (fp[1] - fp[0]) / (xp[1] - xp[0])
        if x >= xp[-1]:
            return fp[-1] + (x - xp[-1]) * (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
        return float(np.interp(x, xp, fp))

    def value(self, px):
        v = self._interp(self.pos, self.v, px)
        return 10 ** v if self.log else v

    def pixel(self, value):
        v = math.log10(value) if self.log else value
        if self.v[0] < self.v[-1]:
            return self._interp(self.v, self.pos, v)
        return self._interp(self.v[::-1], self.pos[::-1], v)


def dots_mask(d, radius):
    """Filled round markers: what survives an opening with a disk of `radius` (thin lines and
    letter strokes do not), grown back to the markers' size."""
    from scipy import ndimage as ndi

    yy, xx = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    disk = xx * xx + yy * yy <= radius * radius
    return ndi.binary_opening(d, structure=disk)


# ---------------------------------------------------------------- curves
def column_runs(d, col, r0, r1):
    v = d[r0:r1, int(col)]
    return [(r0 + a, r0 + b) for a, b in groups(list(np.nonzero(v)[0]))]


def read_line(st, xa, ya, box, at, choose, window=25, min_cols=5, label="", y_round=None, skip=None,
              max_sd=None):
    """Read a curve at each x in `at`. In each column of a window around x, `choose(runs, col)`
    returns the (first, last) row of the curve's run, or None. The row at x is a quadratic trend
    through the chosen run centres (outliers dropped). 95% interval in pixels: half the line's
    extent + 2 sd of the trend residuals + y calibration misfit + |slope| * x calibration misfit
    + 1 px for the straightening."""
    top, bottom, left, right = box
    out = []
    for x in at:
        if skip and skip(x):
            out.append({"x": x, "y": None, "note": skip(x)})
            continue
        c = xa.pixel(x)
        if c < left + 4 or c > right - 4:
            out.append({"x": x, "y": None, "note": "outside the plot box"})
            continue
        cols, cen, half = [], [], []
        for cc in range(int(round(c)) - window, int(round(c)) + window + 1):
            if cc <= left + 3 or cc >= right - 3:
                continue
            runs = column_runs(st.d, cc, top + 4, bottom - 3)
            r = choose(runs, cc)
            if r is None:
                continue
            cols.append(cc)
            cen.append((r[0] + r[1]) / 2.0)
            half.append((r[1] - r[0] + 1) / 2.0)
        if len(cols) < min_cols:
            out.append({"x": x, "y": None, "note": f"only {len(cols)} columns near x={x} show the line"})
            continue
        cols, cen = np.asarray(cols, float), np.asarray(cen, float)
        keep = np.ones(len(cols), bool)
        deg = 2 if len(cols) >= 8 else 1
        for _ in range(4):
            A = np.vstack([(cols - c) ** k for k in range(deg + 1)]).T
            coef, *_ = np.linalg.lstsq(A[keep], cen[keep], rcond=None)
            res = cen - A @ coef
            mad = 1.4826 * float(np.median(np.abs(res[keep])))
            new = np.abs(res) <= max(3.0 * mad, 3.0)
            if new.sum() < min_cols or (new == keep).all():
                break
            keep = new
        if keep.sum() < min_cols:
            out.append({"x": x, "y": None, "note": f"columns near x={x} disagree on the line"})
            continue
        if max_sd is not None and float(np.std(res[keep])) > max_sd:
            out.append({"x": x, "y": None, "note": f"the chosen runs near x={x} scatter by "
                        f"{float(np.std(res[keep])):.0f} px (sd): line and markers mixed"})
            continue
        row = float(coef[0])
        slope = abs(float(coef[1]))
        h = float(np.median(np.asarray(half)[keep]))
        err = h + 2.0 * float(np.std(res[keep])) + ya.misfit + slope * xa.misfit + 1.0
        y = ya.value(row)
        lo, hi = sorted([ya.value(row + err), ya.value(row - err)])
        pc, pr = st.back(c, row)
        _, plo = st.back(c, row - err)
        _, phi = st.back(c, row + err)
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [pc, pr], "px_lo": plo, "px_hi": phi,
                    "note": f"{label}{int(keep.sum())}/{len(cols)} columns; half-width {h:.1f} px; +-{err:.1f} px"})
    return out
