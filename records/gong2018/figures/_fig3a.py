"""Shared code for Fig. 3A of gong2018 (PDF p. 5): three series on one grid.

The three series are plotted at the same evenly spaced values of log10 tau_s/tau_b.
The grid is found in the image from the blue markers (kl = 10^-2), which are the
cleanest at low tau_s/tau_b: their columns are fitted by col = a + b k with integer
k (one marker per step) and the grid is extended over the plot box.

  blue    filled-square template (_common.py), as found.
  red     annulus template (_common.py); the dashed line through a ring can make a
          second, weaker peak half a marker away, so each found ring is assigned to
          the nearest grid column and only the nearest one per column is kept.
  yellow  the squares nearly touch, so a template also fires between them; at each
          grid column, the rows where the yellow mask fills a quarter of a square's
          width (eroded by a disk wider than the dashed line, the hole bridged) give
          the square, at the middle of their extent.  Where that extent is shorter
          than a whole square (another series' marker covers part of it) the
          position is not read.

Axes: inward tick marks matched to the printed labels (shared code, _common.py).
Intervals: one source pixel of the upsampled image (`src_px`), the calibration
misfit and half a pixel, as in _common.py.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

AXES = {
    "tick_px": 16,
    "x": {"labels": [0.01, 0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"]},
    "y": {"labels": [90, 85, 80, 75, 70, 65, 60, 55], "edge_ticks": ["end"], "sides": "either"},
}
# the legend at the top left of the plot, in the series colours
LEGEND = [[300, 170, 1150, 760]]
BLUE = {**AXES, "color": [0, 114, 189], "tol": 90, "square": [17, 0], "score": 0.75, "pad": 30,
        "exclude": LEGEND, "src_px": 8}
RED = {**AXES, "color": [217, 83, 25], "tol": 90, "ring": [15, 27], "score": 0.6, "pad": 30,
       "exclude": LEGEND, "src_px": 8}
YELLOW = {"color": [237, 177, 32], "tol": 80, "erode": 4, "half_width": 18, "bridge": 6, "src_px": 14,
          "min_rows": 34}  # a whole square spans about 40-45 rows after erosion
SNAP_PX = 14  # a found ring further than this from every grid column is not a marker


def _common():
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def grid(image, c, box):
    blue = sorted(p["px"][0] for p in c.read_spec(image, [], BLUE))
    steps = np.diff(blue)
    pitch = float(np.median(steps))
    k = np.concatenate([[0], np.cumsum(np.round(steps / pitch))])
    b, a = np.polyfit(k, blue, 1)
    c0, _, c1, _ = box
    return [a + b * j for j in range(int(np.ceil((c0 - a) / b)), int(np.floor((c1 - a) / b)) + 1)], b


def read_blue(image, at):
    return _common().read_spec(image, at, BLUE)


def read_red(image, at):
    c = _common()
    _, _, box = c.calibrate(image, RED)
    cols, pitch = grid(image, c, box)
    best = {}
    for p in c.read_spec(image, at, RED):
        j = int(np.argmin([abs(p["px"][0] - g) for g in cols]))
        d = abs(p["px"][0] - cols[j])
        if d <= SNAP_PX and (j not in best or d < best[j][0]):
            best[j] = (d, p)
    out = []
    for j in sorted(best):
        p = best[j][1]
        p["note"] += f"; nearest grid column ({best[j][0]:.0f} px away, pitch {pitch:.1f} px)"
        out.append(p)
    return out


def read_yellow(image, at):
    c = _common()
    xa, ya, box = c.calibrate(image, BLUE)
    cols, pitch = grid(image, c, box)
    y = YELLOW
    m = c._mask(image, y["color"], y["tol"])
    c0, r0, c1, r1 = box
    keep = np.zeros_like(m)
    keep[int(r0):int(r1), int(c0) + 3:int(c1)] = True
    for ea, eb, ec, ed in LEGEND:
        keep[eb:ed, ea:ec] = False
    m &= keep
    r = y["erode"]
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    me = ndi.binary_erosion(m, structure=np.hypot(yy, xx) <= r)
    w = y["half_width"]
    ey = y["src_px"] + 0.5 + max(ya.residual_px, 0.5)
    out = []
    for col in cols:
        x = xa.to_value(col)
        win = me[:, int(round(col)) - w:int(round(col)) + w + 1]
        full = win.sum(axis=1) >= 0.25 * (2 * w + 1)
        full = ndi.binary_closing(full, structure=np.ones(2 * y["bridge"] + 1))
        lab, n = ndi.label(full)
        if n == 0:
            out.append({"x": x, "y": None, "note": "no yellow square at this grid position"})
            continue
        sizes = ndi.sum(full, lab, range(1, n + 1))
        rr = np.nonzero(lab == int(np.argmax(sizes)) + 1)[0]
        if rr.max() + 1 - rr.min() < y["min_rows"]:
            continue  # part of the square is covered by another series' marker: not read
        row = (rr.min() + rr.max() + 1) / 2  # the erosion trims both ends equally
        lo, hi = sorted((ya.to_value(row + ey), ya.to_value(row - ey)))
        out.append({"x": x, "y": ya.to_value(row), "lo": lo, "hi": hi, "px": [col, row],
                    "px_lo": row - ey, "px_hi": row + ey,
                    "note": f"grid column (pitch {pitch:.1f} px); square rows {rr.min()}-{rr.max()}"})
    return out
