"""Shared reading code for Fig. 3 (p. 5): relative apparent viscosity against discharge hematocrit,
eight data sets in seven panels (3.3 and 4.4 um share the upper-left panel: filled and open
circles), each with its Eq. 3 line (Table 2 B and C).

Calibration, per panel, from the image (crop straightened by the tilt of its frame lines):
- the panel is the frame found inside a search box around it (long dark rows and columns);
- x: the eleven ticks hanging below the bottom frame line, 0 to 1 in steps of 0.1 (the end ones
  are the frame corners; only the bottom row of panels is labelled, 0, 0.2, ..., 1, and all panels
  carry the same ticks);
- y: the ticks left of the left frame line and right of the right frame line; the top one is the
  top frame line, and the rest are evenly spaced, valued from the labels printed beside them
  (upper-left panel: 3.5 at the frame, then 3, 2.5, 2, 1.5, 1; 5.6 and 6 um panels: 2 at the
  frame, then 1.5, 1; the four lower panels: 7 at the frame, then 6, ..., 1). Each tick's value
  is its rank from the top frame by the median spacing (a tick hidden under a marker is skipped).
  The two sides disagree by up to ~8 px (the print is slightly sheared), so y is interpolated
  between the left and right fits by column.

Markers: filled circles are what survives an opening with a disk of radius 10 px; open circles
are the small round holes (white interiors) of the ink. Both are masked (with a 4 px rim) before
lines are read. A line is then the top or bottom run in a column among those whose value lies
in a band; the bands keep out the panel labels and are given per reading.
"""

import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _p92 as P  # noqa: E402

# search boxes (rows r0..r1, columns c0..c1 of the straightened crop) and the y value of the top frame and the step
PANELS = {
    "3.3/4.4": ((60, 1420, 450, 2350), 3.5, 0.5),
    "5.6": ((60, 700, 2500, 4400), 2.0, 0.5),
    "6": ((700, 1420, 2500, 4400), 2.0, 0.5),
    "9": ((1450, 2920, 450, 2350), 7.0, 1.0),
    "12": ((1450, 2920, 2500, 4400), 7.0, 1.0),
    "20": ((2950, 4430, 450, 2350), 7.0, 1.0),
    "40": ((2950, 4430, 2500, 4400), 7.0, 1.0),
}

_CACHE = {}


def _ticks_valued(ticks, top_row, top_val, step):
    rows = [r for r, n in ticks if n >= 20]
    rows = sorted(rows)
    gaps = np.diff(rows)
    sp = float(np.median(gaps[gaps > 0.6 * np.median(gaps)]))
    vals = [top_val - step * round((r - top_row) / sp) for r in rows]
    return rows, vals


class Panel:
    def __init__(self, image, key):
        self.st = st = P.Straight(image)
        d = st.d
        (r0, r1, c0, c1), top_val, step = PANELS[key]
        rows = P.long_rows(d, 0.5, r0, r1, c0, c1)
        cols = P.long_cols(d, 0.5, r0, r1, c0, c1)
        self.top, self.bottom = rows[0], rows[-1]
        self.left, self.right = cols[0], cols[-1]
        xt = P.ticks_off_hline(d, self.bottom, self.left[0] - 5, self.right[1] + 6, +1, min_len=15)
        if len(xt) != 11:
            raise ValueError(f"panel {key}: {len(xt)} x ticks")
        self.xa = P.Axis([c for c, _ in xt], [k / 10 for k in range(11)])
        top_row = (self.top[0] + self.top[1]) / 2.0
        yl = P.ticks_off_vline(d, self.left, self.top[0] - 5, self.bottom[1] + 6, -1, min_len=10)
        yr = P.ticks_off_vline(d, self.right, self.top[0] - 5, self.bottom[1] + 6, +1, min_len=10)
        self.yl = P.Axis(*_ticks_valued(yl, top_row, top_val, step))
        self.yr = P.Axis(*_ticks_valued(yr, top_row, top_val, step))
        self.lcol = (self.left[0] + self.left[1]) / 2.0
        self.rcol = (self.right[0] + self.right[1]) / 2.0
        self.box = (self.top[1], self.bottom[0], self.left[1], self.right[0])
        sub = (slice(self.top[1] + 1, self.bottom[0]), slice(self.left[1] + 1, self.right[0]))
        inner = np.zeros_like(d)
        inner[sub] = d[sub]
        self.inner = inner
        self.filled = P.dots_mask(inner, 10)
        holes = ndi.binary_fill_holes(inner) & ~inner
        lab, n = ndi.label(holes)
        keep = np.zeros_like(holes)
        if n:
            sizes = ndi.sum(holes, lab, range(1, n + 1))
            for k, sl in enumerate(ndi.find_objects(lab), start=1):
                h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
                if 150 <= sizes[k - 1] <= 1500 and 0.6 <= h / max(w, 1) <= 1.6 and sizes[k - 1] >= 0.55 * h * w:
                    # a gap enclosed by filled markers is not an open circle: its rim is mostly filled ink
                    big = (slice(max(sl[0].start - 10, 0), sl[0].stop + 10), slice(max(sl[1].start - 10, 0), sl[1].stop + 10))
                    one = lab[big] == k
                    rim = ndi.binary_dilation(one, iterations=8) & ~one
                    if (rim & self.filled[big]).sum() < 0.3 * rim.sum():
                        keep[sl] |= lab[sl] == k
        self.holes = keep
        rings = ndi.binary_dilation(keep, iterations=9) & inner
        self.lines = inner & ~ndi.binary_dilation(self.filled, iterations=4) & ~ndi.binary_dilation(rings, iterations=2)

    def ya_at(self, col):
        w = (col - self.lcol) / (self.rcol - self.lcol)
        a = self.yl.a + (self.yr.a - self.yl.a) * w
        b = self.yl.b + (self.yr.b - self.yl.b) * w
        ax = P.Axis([0, 1, 2], [a, a + b, a + 2 * b])
        ax.misfit = max(self.yl.misfit, self.yr.misfit) + 1.0
        return ax

    def note(self):
        return (f"x misfit {self.xa.misfit:.1f} px; y misfit left {self.yl.misfit:.1f}, "
                f"right {self.yr.misfit:.1f} px")


class _View:
    def __init__(self, panel):
        self.d = panel.lines
        self.back = panel.st.back


def read_line(image, at, key, band, label):
    """band(x) -> (lo, hi, 'top'|'bottom') or None (not read at x)."""
    p = Panel(image, key)
    view = _View(p)
    out = []
    for a in at:
        x = float(a)
        b = band(x)
        if b is None:
            out.append({"x": x, "y": None, "note": "markers, the other line or the panel label too close: not read"})
            continue
        lo, hi, pick = b

        def choose(runs, c, lo=lo, hi=hi, pick=pick):
            ya = p.ya_at(c)
            cand = [r for r in runs if lo <= ya.value((r[0] + r[1]) / 2.0) <= hi and r[1] - r[0] < 120]
            if not cand:
                return None
            return cand[0] if pick == "top" else cand[-1]

        ya = p.ya_at(p.xa.pixel(x))
        # at least 12 columns in the 41-column window must show the line between the markers, and
        # the chosen runs must follow one smooth trend (sd at most 5 px), else line and markers mix
        r = P.read_line(view, p.xa, ya, p.box, [x], choose, window=20, min_cols=12, max_sd=5.0)[0]
        if r.get("y") is not None:
            r["note"] += f"; {label}; {p.note()}"
        out.append(r)
    return out


def _disks(mask, R, merged_area):
    """Greedy disks in a mask of markers: (row, col, merged?)."""
    lab, n = ndi.label(mask)
    out = []
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        sub = np.pad(lab[sl] == k, 2)
        merged = float(sub.sum()) > merged_area
        rem = sub
        while True:
            dt = ndi.distance_transform_edt(rem)
            m = float(dt.max())
            if m < 0.5 * R:
                break
            rr, cc = np.unravel_index(int(np.argmax(dt)), dt.shape)
            pr, pc = np.nonzero(dt >= m - 0.75)
            near = (pr - rr) ** 2 + (pc - cc) ** 2 <= (0.5 * R) ** 2
            rr, cc = float(pr[near].mean()), float(pc[near].mean())
            out.append((sl[0].start + rr - 2, sl[1].start + cc - 2, merged))
            ri, ci = np.ogrid[0:rem.shape[0], 0:rem.shape[1]]
            rem = rem & ((ri - rr) ** 2 + (ci - cc) ** 2 > (0.7 * R) ** 2)
    return out


def _point(p, row, col, err_px, note):
    ya = p.ya_at(col)
    err = err_px + ya.misfit
    lo, hi = sorted([ya.value(row + err), ya.value(row - err)])
    pc, pr = p.st.back(col, row)
    _, plo = p.st.back(col, row - err)
    _, phi = p.st.back(col, row + err)
    xerr = err_px + p.xa.misfit
    return {"x": p.xa.value(col), "y": ya.value(row), "lo": lo, "hi": hi, "px": [pc, pr],
            "px_lo": plo, "px_hi": phi,
            "note": note + f"; x within {p.xa.value(col - xerr):.3f}..{p.xa.value(col + xerr):.3f}"}


def read_filled(image, key, exclude=None):
    """Filled circles of a panel, split greedily into disks (as in _fig5). exclude(x, y) -> True
    drops a point (a region where the panel label stands)."""
    p = Panel(image, key)
    # marker radius: the median over blobs of the largest inscribed disk (a merged blob still holds
    # a whole marker), so it does not depend on how many blobs are single
    lab, n = ndi.label(p.filled)
    radii = [float(ndi.distance_transform_edt(np.pad(lab[sl] == k, 1)).max())
             for k, sl in enumerate(ndi.find_objects(lab), start=1)]
    R = float(np.median(radii))
    single = float(np.pi * R * R)
    out = []
    # a printed marker is not a perfect disk: a blob counts as merged above 1.6 inscribed-disk areas
    for row, col, merged in _disks(p.filled, R, 1.6 * single):
        o = _point(p, row, col, 0.5 * R if merged else 2.0,
                   ("split from a blob of merged markers" if merged else "single marker") + f"; marker radius {R:.1f} px")
        if exclude and exclude(o["x"], o["y"]):
            continue
        out.append(o)
    out.sort(key=lambda o: (o["x"], o["y"]))
    return out


def read_open(image, key, exclude=None):
    """Open circles: each round hole of the ink is one marker, at the hole's centroid; the
    interval is the hole's radius (a hole cut by an overlapping ring is off-centre by at most
    that)."""
    p = Panel(image, key)
    lab, n = ndi.label(p.holes)
    out = []
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        sub = lab[sl] == k
        rr, cc = np.nonzero(sub)
        row, col = sl[0].start + rr.mean(), sl[1].start + cc.mean()
        r_h = float(np.sqrt(sub.sum() / np.pi))
        o = _point(p, row, col, r_h, f"open circle (hole radius {r_h:.1f} px)")
        if exclude and exclude(o["x"], o["y"]):
            continue
        out.append(o)
    out.sort(key=lambda o: (o["x"], o["y"]))
    return out
