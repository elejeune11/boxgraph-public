"""Fig. 5 (PDF p. 6): the orange dot marking the critical point (maximum of the spinodal curve on
the critical branch), for lambda_max = 1.1R and r_p = R. Returns one point: x = d/R, y = k*R.

Calibration by _colour_curves.py (see its docstring): labelled y ticks 30, 20, 10 from the top;
0.1 in d/R per x tick. The dot is the deepest pixel of the orange (255, 89, 0) mask (the largest
distance to a non-orange pixel); its centre is located to about 2 px, and the interval adds the
calibration misfits.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_colour_curves", Path(__file__).with_name("_colour_curves.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    cal = m.calibrate(image, [30.0, 20.0, 10.0], 0.1)
    mask, lab, order, sizes = m.colour_parts(cal, (255, 89, 0))
    edt = ndi.distance_transform_edt(mask)
    r, c = np.unravel_index(int(np.argmax(edt)), edt.shape)
    # centre of the dot: centroid of its pixels deeper than half its radius
    rad = float(edt[r, c])
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
