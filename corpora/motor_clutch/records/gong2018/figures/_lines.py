"""Shared code for solid model curves of gong2018 read at chosen x positions.

For one curve of one colour:
  1. mask the colour inside the plot box (minus excluded boxes, e.g. the legend);
  2. an opening by a disk of radius `open_r` keeps the thick solid line and drops
     thinner strokes of the same colour (marker outlines, text);
  3. at each x of `at` (the reader's choice of positions, in the axis unit), in a
     window of +/-`half` columns around the calibrated column, the line is the run
     of masked rows; the value is the middle of the run;
  4. a position is not read (left out of the result, with no value) when there is
     no run (the curve is hidden under another curve drawn on top of it), when
     there are several runs, when the run is longer than `max_run` rows (a
     steep or vertical stretch, where the value is not defined by the column),
     or shorter than `min_run` rows (thinner than the line: partly hidden under
     another curve, so its middle is not the line's).

With `scatter`, a band of scattered dots is read instead: the median row of the
colour's pixels in the window, with the 10th-90th percentile spread as the run.

Axes: tick marks matched to the printed labels (_axes.py).
Interval (95%): half the run's length (the line's thickness, with the slope
across the window), one source pixel of the upsampled image (`src_px`), the
calibration misfit and half a pixel.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi


def _load(name):
    spec = importlib.util.spec_from_file_location(f"gong2018{name}", Path(__file__).with_name(f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mask(image, color, tol):
    f = image.astype(float)
    return np.sqrt(((f - np.asarray(color, float)) ** 2).sum(axis=2)) <= tol


def read_curve(image, at, axes, s, exclude=(), calib=None):
    xa, ya, box = calib or _load("_axes").calibrate(image, axes)
    c0, r0, c1, r1 = (int(v) for v in box)
    m = mask(image, s["color"], s["tol"])
    keep = np.zeros_like(m)
    mg = s.get("margin", 4)
    keep[r0 + mg:r1 - mg, c0 + mg:c1 - mg] = True
    for ea, eb, ec, ed in exclude:
        keep[eb:ed, ea:ec] = False
    m &= keep
    r = s["open_r"]
    if r:
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        m = ndi.binary_opening(m, structure=np.hypot(yy, xx) <= r)
    half = s.get("half", 2)
    out = []
    for x in at:
        col = xa.to_pixel(x)
        a = int(round(col)) - half
        if a < c0 + mg or a + 2 * half + 1 > c1 - mg:
            continue
        prof = m[:, a:a + 2 * half + 1].any(axis=1)
        if s.get("scatter"):
            # a band of scattered dots: its middle is the median row of the colour's
            # pixels in the window; its spread (10th to 90th percentile) is the run
            rr, _ = np.nonzero(m[:, a:a + 2 * half + 1])
            if len(rr) < s.get("min_px", 50):
                continue
            p10, p50, p90 = np.percentile(rr, [10, 50, 90])
            row, run = p50 + 0.5, max(p90 - p10, 1.0)
            e = run / 2 + s.get("src_px", 8) + 0.5 + max(ya.residual_px, 0.5)
            lo, hi = sorted((ya.to_value(row + e), ya.to_value(row - e)))
            out.append({"x": x, "y": ya.to_value(row), "lo": lo, "hi": hi, "px": [col, row],
                        "px_lo": row - e, "px_hi": row + e,
                        "note": f"median of the dot band, rows {p10:.0f}-{p90:.0f} (10-90%) at column {col:.0f}"})
            continue
        lab, n = ndi.label(prof)
        if n != 1:
            continue
        rows = np.nonzero(prof)[0]
        run = rows.max() + 1 - rows.min()
        if run > s["max_run"] or run < s.get("min_run", 0):
            continue  # steep, or partly hidden under another curve (thinner than the line)
        row = (rows.min() + rows.max() + 1) / 2
        e = run / 2 + s.get("src_px", 8) + 0.5 + max(ya.residual_px, 0.5)
        lo, hi = sorted((ya.to_value(row + e), ya.to_value(row - e)))
        out.append({"x": x, "y": ya.to_value(row), "lo": lo, "hi": hi, "px": [col, row],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": f"line centre, rows {rows.min()}-{rows.max()} at column {col:.0f}"})
    return out
