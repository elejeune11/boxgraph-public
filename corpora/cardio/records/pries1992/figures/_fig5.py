"""Shared reading code for Fig. 5 (p. 6): relative apparent viscosity against tube diameter.

Calibration from the image (crop straightened by the tilt of its frame):
- x: the ticks hanging below the bottom frame line and those standing above the top frame line,
  each taken in order from the left frame (the long ticks are the labelled decades 1, 10, 100,
  1000; between them 2..9 times a decade; then 2000, 3000), log scale. The printed page is
  slightly sheared (the top ticks sit up to ~12 px right of the bottom ones), so the tick
  position used at a given row is interpolated between the two rows of ticks.
- y: the ten ticks left of the left frame line, every 0.5 from 5.5 (top, unlabelled) down to 1
  (labelled 5, 4, 3, 2, 1). Their spacing is uneven by up to ~10 px (reproduction), so y is
  interpolated between neighbouring ticks.

Lines: the filled data markers are removed first (an opening with a disk of radius 14 px keeps
only them; they and a 4 px rim are masked out), then in each column the line is chosen among the
remaining runs by a value band (calibrated y) and a rank (top or bottom of the runs in the band).
The bands were chosen by looking at the figure, to keep out the data letters, the thin lines
joining them, the legend and the curve labels; they are listed in each reading's code.
"""

import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _p92 as P  # noqa: E402

Y_LABELS = [5.5, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0]


def decade_values(n):
    vals, dec = [], 1.0
    while len(vals) < n:
        for k in range(1, 10):
            vals.append(k * dec)
            if len(vals) == n:
                break
        dec *= 10
    return vals


class Cal:
    def __init__(self, image, y_labels=None):
        self.y_labels = Y_LABELS if y_labels is None else y_labels
        self.st = st = P.Straight(image)
        d = st.d
        rows = P.long_rows(d, 0.6)
        cols = P.long_cols(d, 0.6)
        self.top, self.bottom = rows[0], rows[-1]
        self.left = cols[0]
        bt = P.ticks_off_hline(d, self.bottom, self.left[0] - 5, d.shape[1], +1, min_len=15)
        tt = P.ticks_off_hline(d, self.top, self.left[0] - 5, d.shape[1], -1, min_len=15)
        if len(bt) != len(tt):
            raise ValueError(f"{len(bt)} bottom ticks but {len(tt)} top ticks")
        self.bt = np.array([c for c, _ in bt])
        self.tt = np.array([c for c, _ in tt])
        self.xvals = decade_values(len(bt))
        self.right = (int(self.bt[-1]) - 2, int(self.bt[-1]) + 2)
        yt = P.ticks_off_vline(d, self.left, self.top[0] - 20, self.bottom[1] + 20, -1, min_len=15)
        rcol = P.long_cols(d, 0.6, c0=int(self.bt[-1]) - 15, c1=int(self.bt[-1]) + 15)[0]
        yr = P.ticks_off_vline(d, rcol, self.top[0] - 20, self.bottom[1] + 20, +1, min_len=15)
        if len(yt) != len(self.y_labels) or len(yr) != len(self.y_labels):
            raise ValueError(f"found {len(yt)} left and {len(yr)} right y ticks")
        self.yl = np.array([r for r, _ in yt])
        self.yr = np.array([r for r, _ in yr])
        self.lcol, self.rcol = (self.left[0] + self.left[1]) / 2.0, (rcol[0] + rcol[1]) / 2.0
        self.ya = self.ya_at((self.lcol + self.rcol) / 2.0)
        self.box = (self.top[1], self.bottom[0], self.left[1], int(self.bt[-1]) - 3)
        dots = P.dots_mask(d, 14)
        self.dots = dots
        self.lines = d & ~ndi.binary_dilation(dots, iterations=4)

    def xa_at(self, row):
        w = (self.bottom[0] - row) / float(self.bottom[0] - self.top[1])
        pos = self.bt + (self.tt - self.bt) * w
        return P.PiecewiseAxis(pos, self.xvals, log=True, misfit=2.0)

    def ya_at(self, col):
        w = (col - self.lcol) / (self.rcol - self.lcol)
        return P.PiecewiseAxis(self.yl + (self.yr - self.yl) * w, self.y_labels, misfit=2.0)

    def x_misfit_note(self):
        return (f"x ticks top-bottom offset up to {np.max(np.abs(self.tt - self.bt)):.0f} px, "
                f"y ticks left-right up to {np.max(np.abs(self.yr - self.yl)):.0f} px")


class _Lines:
    """A view of the straightened image with the markers removed, for P.read_line."""

    def __init__(self, cal):
        self.d = cal.lines
        self.back = cal.st.back


def read_bands(image, at, bands, label, y_labels=None):
    """bands: {x as printed: (lo, hi, 'top'|'bottom')} -- the line is the top or bottom run whose
    centre value lies in [lo, hi]; x not in bands is not read. y_labels: the tick values top to
    bottom, for another figure with the same layout (Fig. 2)."""
    cal = Cal(image, y_labels)
    view = _Lines(cal)
    bands = {float(k): v for k, v in bands.items()}
    out = []
    for a in at:
        x = float(a)
        band = bands.get(x)
        if band is None:
            out.append({"x": x, "y": None, "note": "data letters, thin lines or other curves too close: not read"})
            continue
        lo, hi, pick = band

        def choose(runs, c, lo=lo, hi=hi, pick=pick):
            yc = cal.ya_at(c)
            cand = [r for r in runs if lo <= yc.value((r[0] + r[1]) / 2.0) <= hi and r[1] - r[0] < 250]
            if not cand:
                return None
            return cand[0] if pick == "top" else cand[-1]

        # two passes: the row found with the mid-height x axis fixes the x axis at that row
        xa = cal.xa_at((cal.top[1] + cal.bottom[0]) / 2.0)
        ya = cal.ya_at(xa.pixel(x))
        r = P.read_line(view, xa, ya, cal.box, [x], choose, window=25)[0]
        if r.get("y") is not None:
            row = ya.pixel(r["y"])
            xa = cal.xa_at(row)
            ya = cal.ya_at(xa.pixel(x))
            r = P.read_line(view, xa, ya, cal.box, [x], choose, window=25)[0]
        if r.get("y") is not None:
            r["note"] += f"; {label}; {cal.x_misfit_note()}"
        out.append(r)
    return out


def read_dots(image, radius_hint=None):
    """Filled markers: the opened mask is split into disks greedily (largest inscribed disk first,
    a disk of 0.7 marker radius around it removed, repeated while a disk of at least half the marker radius still fits). The marker
    radius is the median inscribed radius of the blobs that hold one marker only (the commonest
    blob size). x and y at each centre; the 95% interval is 2 px plus the calibration misfit for
    a marker standing alone, and half a marker radius for one split out of a merged blob."""
    cal = Cal(image)
    dots = cal.dots
    lab, n = ndi.label(dots)
    sizes = ndi.sum(dots, lab, range(1, n + 1))
    single = float(np.median(sizes[sizes < np.percentile(sizes, 50) * 1.3]))
    R = float(np.sqrt(single / np.pi))
    out = []
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        sub = lab[sl] == k
        area = float(sub.sum())
        merged = area > 1.3 * single
        r0, c0 = sl[0].start, sl[1].start
        rem = np.pad(sub, 2)
        while True:
            dt = ndi.distance_transform_edt(rem)
            m = float(dt.max())
            if m < 0.5 * R:
                break
            rr, cc = np.unravel_index(int(np.argmax(dt)), dt.shape)
            # the centre of the plateau of near-maximal distance
            pr, pc = np.nonzero(dt >= m - 0.75)
            near = (pr - rr) ** 2 + (pc - cc) ** 2 <= (0.5 * R) ** 2
            rr, cc = float(pr[near].mean()), float(pc[near].mean())
            row, col = r0 + rr - 2, c0 + cc - 2
            ri, ci = np.ogrid[0:rem.shape[0], 0:rem.shape[1]]
            rem = rem & ((ri - rr) ** 2 + (ci - cc) ** 2 > (0.7 * R) ** 2)
            xa = cal.xa_at(row)
            ya = cal.ya_at(col)
            err = (0.5 * R if merged else 2.0) + ya.misfit
            xerr = (0.5 * R if merged else 2.0) + xa.misfit
            x = xa.value(col)
            y = ya.value(row)
            lo, hi = sorted([ya.value(row + err), ya.value(row - err)])
            pc_, pr_ = cal.st.back(col, row)
            _, plo = cal.st.back(col, row - err)
            _, phi = cal.st.back(col, row + err)
            out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [pc_, pr_], "px_lo": plo, "px_hi": phi,
                        "note": ("split from a blob of merged markers" if merged else "single marker")
                        + f"; marker radius {R:.1f} px; x within {xa.value(col - xerr):.4g}..{xa.value(col + xerr):.4g}"})
    out.sort(key=lambda o: (o["x"], o["y"]))
    return out
