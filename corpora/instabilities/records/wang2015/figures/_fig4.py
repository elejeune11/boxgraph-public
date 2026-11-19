"""Shared reading code for Fig. 4 (p. 6) of wang2015: six sections of the phase diagram at
Gamma/(mu_s H_f) = 0.13, 0.28, 0.46, 0.81, 3.99, 66.63, each with eM on the horizontal axis
(linear, 0 ... 0.6) and mu_f/mu_s on the vertical axis (logarithmic, 10^-1 ... 10^5). The
red curve is the computed (finite element) boundary of the delaminated-buckle region.

Calibration: the plot frame is the black box (the longest dark rows and columns). Its edges
carry the end labels (left 0, right 0.6, bottom 10^-1, top 10^5). The inward major tick marks
along the bottom edge (0.1 ... 0.5) and the right edge (10^0 ... 10^4) are found as the
longest short dark runs next to the frame, matched to the nearest predicted label position
(within 1.5% of the axis), and fitted together with the edges; the misfit is the largest
residual. The right edge is used for the vertical ticks because the curves crowd the left.

The red curve: pixels clearly red (R high, G and B low), the largest connected piece (the
photographs' red arrows are separate pieces). At each eM its rows in the column (and the two
neighbours) give the value (their middle) and the interval (their extent, plus the misfit).
"""
import math

import numpy as np
from scipy import ndimage as ndi


def _ink(img, vertical):
    """Thin dark lines by local contrast (the raster is blurred and the frame is not black):
    pixels at least 45 grey levels darker than the grey closing across the line's direction."""
    gray = img.astype(float).mean(2)
    size = (1, 21) if vertical else (21, 1)
    return ndi.grey_closing(gray, size=size) - gray > 45


def _longest(v):
    best, start, bs = 0, None, 0
    for i, x in enumerate(list(v) + [False]):
        if x and start is None:
            start = i
        elif not x and start is not None:
            if i - start > best:
                best, bs = i - start, start
            start = None
    return best, bs


def _groups(idx):
    out, cur = [], []
    for i in list(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            out.append((cur[0] + cur[-1]) / 2.0)
            cur = []
        if i is not None:
            cur.append(int(i))
    return out


def frame(img):
    # widened by a pixel either way: the blurred, slightly tilted lines wander by a pixel
    dv = ndi.binary_dilation(_ink(img, True), structure=np.ones((1, 3)))
    dh = ndi.binary_dilation(_ink(img, False), structure=np.ones((3, 1)))
    H, W = dv.shape
    # frame lines: ink over most of the crop's width or height (the plot fills ~80% of the crop;
    # the dashed section lines and the boundary curves fill far less of any one row or column)
    rows = [r for r in range(H) if dh[r].mean() > 0.5]  # Fig. 4F: an inset photo covers part of the top edge
    cols = [c for c in range(W) if dv[:, c].mean() > 0.6]
    gr, gc = _groups(rows), _groups(cols)
    return gc[0], gr[0], gc[-1], gr[-1]  # left, top, right, bottom (line centres)


def _fit(px, vals):
    px, vals = np.asarray(px, float), np.asarray(vals, float)
    b, a = np.polyfit(px, vals, 1)
    mis = float(np.max(np.abs(px - (vals - a) / b)))
    return a, b, max(mis, 0.5)


class Cal:
    def __init__(self, img):
        dv, dh = _ink(img, True), _ink(img, False)
        left, top, right, bottom = frame(img)
        self.box = (left, top, right, bottom)
        L, T, R_, B = [int(round(v)) for v in self.box]
        def run(line):
            """Length of the ink run that starts within 10 px of the frame (index 0 = frame side)."""
            k = 0
            while k < 10 and not line[k]:
                k += 1
            n = 0
            while k + n < len(line) and line[k + n] and n < 60:
                n += 1
            return n

        def ticks(lens, preds, span):
            """Per predicted position: the positions within 1.5% of the axis whose run is a tick
            (8-45 px; longer runs are boundary lines) and at least 85% of the longest such run
            there (major, not minor, ticks); their mean."""
            out = []
            for k, pred in preds:
                win = {p: n for p, n in lens.items() if abs(p - pred) <= 0.015 * span and 8 <= n <= 45}
                if win:
                    top_n = max(win.values())
                    out.append((k, float(np.mean([p for p, n in win.items() if n >= 0.85 * top_n]))))
            return out

        # bottom edge: vertical tick marks upward from the frame line (which is skipped)
        lens = {c: run(dv[B - 4::-1, c]) for c in range(L + 8, R_ - 7)}
        found = ticks(lens, [(k, left + (right - left) * k / 6.0) for k in range(1, 6)], right - left)
        xs = [float(left), float(right)] + [p for _, p in found]
        xv = [0.0, 0.6] + [0.1 * k for k, _ in found]
        self.ax, self.bx, self.mx = _fit(xs, xv)
        # right edge: horizontal tick marks leftward from the frame line
        lens = {r: run(dh[r, R_ - 4::-1]) for r in range(T + 8, B - 7)}
        found_y = ticks(lens, [(k, bottom - (bottom - top) * k / 6.0) for k in range(1, 6)], bottom - top)
        ys = [float(bottom), float(top)] + [p for _, p in found_y]
        yv = [-1.0, 5.0] + [-1.0 + k for k, _ in found_y]
        self.ay, self.by, self.my = _fit(ys, yv)
        self.n_ticks = (len(xs) - 2, len(ys) - 2)
        self.ticks_x, self.ticks_y = list(zip(xs, xv)), list(zip(ys, yv))

    def col(self, eM):
        return (eM - self.ax) / self.bx

    def ratio(self, row):
        return 10.0 ** (self.ay + self.by * row)


def red_curve(img, at, gamma_label):
    cal = Cal(img)
    a = img.astype(int)
    red = (a[..., 0] > 170) & (a[..., 1] < 90) & (a[..., 2] < 90)
    L, T, R_, B = [int(round(v)) for v in cal.box]
    m = np.zeros_like(red)
    m[T + 3:B - 2, L + 3:R_ - 2] = red[T + 3:B - 2, L + 3:R_ - 2]
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n == 0:
        return [{"x": x, "y": None, "note": "no red curve"} for x in at]
    # keep the pieces of the curve (it is cut where black lines, dashed lines and markers cross
    # it); drop red pieces lying in a photograph (arrows, scale bars): their surroundings are grey
    a_sat = a.max(2) - a.min(2)
    a_gray = a.mean(2)
    photo_like = (a_sat < 40) & (a_gray > 60) & (a_gray < 235)
    curve = np.zeros_like(m)
    for i, sl in enumerate(ndi.find_objects(lab)):
        piece = lab[sl] == i + 1
        if piece.sum() < 40:
            continue
        r0, r1 = max(sl[0].start - 8, 0), sl[0].stop + 8
        c0, c1 = max(sl[1].start - 8, 0), sl[1].stop + 8
        big = np.zeros((r1 - r0, c1 - c0), bool)
        big[sl[0].start - r0:sl[0].stop - r0, sl[1].start - c0:sl[1].stop - c0] = piece
        ring = ndi.binary_dilation(big, iterations=8) & ~ndi.binary_dilation(big, iterations=3)
        if photo_like[r0:r1, c0:c1][ring].mean() > 0.5:
            continue
        curve[sl] |= piece
    out = []
    for x in at:
        c = int(round(cal.col(x)))
        rows = np.nonzero(curve[:, c - 1:c + 2].any(1))[0]
        if len(rows) == 0:
            out.append({"x": x, "y": None, "note": "red curve not in this column"})
            continue
        runs = []
        for r in rows:
            if runs and r - runs[-1][1] <= 6:
                runs[-1][1] = r
            else:
                runs.append([r, r])
        if len(runs) > 1:
            out.append({"x": x, "y": None, "note": f"red in several places in this column: {runs}"})
            continue
        s, e = int(runs[0][0]), int(runs[0][1])
        row = (s + e) / 2.0
        # a column cuts a steep curve over many rows; the interval is that whole cut
        err = (e - s + 1) / 2.0 + cal.my
        out.append({"x": x, "y": cal.ratio(row), "lo": cal.ratio(row + err), "hi": cal.ratio(row - err),
                    "px": [float(c), row], "px_lo": row - err, "px_hi": row + err,
                    "note": f"Gamma/(mu_s H_f) = {gamma_label}; red rows {s}-{e}; "
                            f"ticks matched x {cal.n_ticks[0]}, y {cal.n_ticks[1]}; misfit x {cal.mx:.1f}, y {cal.my:.1f} px"})
    return out
