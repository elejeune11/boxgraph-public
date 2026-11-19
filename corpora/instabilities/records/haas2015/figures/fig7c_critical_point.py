"""Fig. 7(c) (PDF p. 7): the orange dot labelled "critical point (lambda*, k*)". Returns one point:
x = d/R, y = k*R.

Calibration by _colour_curves.py: labelled y ticks 20, 10 from the top; 0.1 in d/R per x tick.
The dot is the deepest pixel of the orange (255, 89, 0) mask; its centre is the centroid of its
pixels deeper than half its radius, located to about 2 px; the interval adds the calibration
misfits.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi


def _h():
    spec = importlib.util.spec_from_file_location("haas2015_fig7", Path(__file__).with_name("_fig7.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    h = _h()
    m = h.cc()
    cal = m.calibrate(image, [20.0, 10.0], 0.1)
    mask, edt, r, c, rad = h.dot(cal, (255, 89, 0))
    lab, _ = ndi.label(mask)
    core = (edt > 0.5 * rad) & (lab == lab[r, c])
    core_lab, _ = ndi.label(core)
    rows, cols = np.where(core_lab == core_lab[r, c])
    row, col = float(rows.mean()), float(cols.mean())
    x = (col - cal["c0"]) / cal["cpu"]
    y = cal["a"] + cal["b"] * row
    dy = abs(cal["b"]) * 2.0 + cal["ymis"]
    return [{"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy), "px": [col, row],
             "px_lo": row - 2.0, "px_hi": row + 2.0,
             "note": m.note(cal, f"orange dot, radius {rad:.0f} px; d/R = {x:.4f} +- {2.0 / cal['cpu'] + cal['xmis']:.4f}")}]
