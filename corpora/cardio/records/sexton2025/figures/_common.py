"""Shared reading code for the figures of sexton2025. Everything is found in the rendered crop.

Calibration. A y axis is a long vertical line of dark ink (the plot frame's left side); an x axis a long
horizontal one (the frame's bottom). Tick marks are short dark runs that leave the axis line, inwards or
outwards. Their centres are matched in order to the printed tick labels the caller passes (the only
values typed in from the page), a straight line (or a line in log10) is fitted, and the largest misfit
in pixels widens every interval.
"""

import math

import numpy as np


def gray(image):
    return image[..., :3].astype(float).mean(axis=2)


def runs(v):
    """[start, end) of the runs of True in a 1D boolean array."""
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def merge(pos, gap=2):
    """Group sorted integer positions into runs, bridging gaps up to `gap`; centres."""
    out, cur = [], []
    for p in sorted(pos):
        if cur and p - cur[-1] > gap:
            out.append(cur)
            cur = []
        cur.append(p)
    if cur:
        out.append(cur)
    return [((g[0] + g[-1]) / 2.0 + 0.5, g[0], g[-1]) for g in out]


class Axis:
    def __init__(self, pix, vals, scale="linear"):
        self.scale = scale
        p = np.asarray(pix, float)
        v = np.asarray(vals, float)
        u = np.log10(v) if scale == "log10" else v
        self.b, self.a = np.polyfit(p, u, 1)
        self.misfit = max(float(np.max(np.abs(p - (u - self.a) / self.b))), 0.5)
        self.marks = list(zip(p.tolist(), v.tolist()))

    def val(self, p):
        u = self.a + self.b * p
        return 10.0 ** u if self.scale == "log10" else u

    def pix(self, v):
        u = math.log10(v) if self.scale == "log10" else v
        return (u - self.a) / self.b

    def interval(self, p, half):
        a, b = self.val(p - half - self.misfit), self.val(p + half + self.misfit)
        return min(a, b), max(a, b)


def frame(image, dark=110, frac=0.5, region=None):
    """Rows of long horizontal ink lines and columns of long vertical ones, within region
    (r0, r1, c0, c1). Returns (rows, cols) as lists of run centres."""
    g = gray(image)
    ink = g < dark
    r0, r1, c0, c1 = region if region else (0, ink.shape[0], 0, ink.shape[1])
    sub = ink[r0:r1, c0:c1]
    H, W = sub.shape
    rows = [r + r0 for r in range(H) if max((e - s for s, e in runs(sub[r])), default=0) >= frac * W]
    cols = [c + c0 for c in range(W) if max((e - s for s, e in runs(sub[:, c])), default=0) >= frac * H]
    return merge(rows), merge(cols)


def ticks_on_vertical(image, col_lo, col_hi, side, length, r0, r1, dark=110, minlen=None):
    """Rows of tick marks on a vertical axis line occupying columns [col_lo, col_hi]. side 'in' looks
    right of it, 'out' left. A tick: a row where the `length` px next to the line are mostly ink."""
    ink = gray(image) < dark
    if side == "in":
        band = ink[r0:r1, col_hi + 1: col_hi + 1 + length]
    else:
        band = ink[r0:r1, max(col_lo - length, 0): col_lo]
    need = minlen if minlen is not None else 0.8 * length
    rows = [r + r0 for r in range(band.shape[0]) if band[r].sum() >= need]
    return [m for m in merge(rows) if m[2] - m[1] < 25]


def ticks_on_horizontal(image, row_lo, row_hi, side, length, c0, c1, dark=110, minlen=None):
    """Columns of tick marks on a horizontal axis line occupying rows [row_lo, row_hi]; side 'in' looks
    above it, 'out' below."""
    ink = gray(image) < dark
    if side == "in":
        band = ink[max(row_lo - length, 0): row_lo, c0:c1]
    else:
        band = ink[row_hi + 1: row_hi + 1 + length, c0:c1]
    need = minlen if minlen is not None else 0.8 * length
    cols = [c + c0 for c in range(band.shape[1]) if band[:, c].sum() >= need]
    return [m for m in merge(cols) if m[2] - m[1] < 25]


def hue_mask(image, rgb, tol):
    """Pixels within `tol` (Euclidean, 0-255) of a colour."""
    d = image[..., :3].astype(float) - np.asarray(rgb, float)
    return np.sqrt((d * d).sum(axis=2)) < tol


def column_runs(mask, col, r0=0, r1=None):
    r1 = mask.shape[0] if r1 is None else r1
    return [(s + r0, e + r0) for s, e in runs(mask[r0:r1, col])]


def curve_at(mask, col, near=None, search=3, r0=0, r1=None):
    """Centre and half-height of the mask run in column col (or a neighbour), the one nearest `near`."""
    for dc in sorted(range(-search, search + 1), key=abs):
        c = int(col) + dc
        if not (0 <= c < mask.shape[1]):
            continue
        rs = column_runs(mask, c, r0, r1)
        if rs:
            if near is None:
                s, e = rs[0]
            else:
                s, e = min(rs, key=lambda t: abs((t[0] + t[1]) / 2 - near))
            return (s + e - 1) / 2.0 + 0.5, (e - s) / 2.0, c
    return None
