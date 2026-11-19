"""Fig. 7(c) (PDF p. 7): the orange critical branch (lambda = lambda*), kR against d/R.

Calibration by _colour_curves.py: labelled y ticks 20, 10 from the top; x labels 0, 0.3, 0.6, ...
under every third tick (0.1 per tick). The orange (255, 89, 0) pixels are the branch, the
critical-point dot on it, the leader line from the label to the dot and the label's letters.
A disc of 2.5 dot radii around the dot (the deepest orange pixel) is removed; of what is left,
the connected parts spanning at least 0.3 in d/R are the branch (the leader line and the letters
span less). A column is read only where it holds exactly one run of the branch.
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
    cal = h.cc().calibrate(image, [20.0, 10.0], 0.1)
    mask, edt, r, c, rad = h.dot(cal, (255, 89, 0))
    mask = h.plot_box(cal, mask)
    yy, xx = np.ogrid[: mask.shape[0], : mask.shape[1]]
    mask &= (yy - r) ** 2 + (xx - c) ** 2 > (2.5 * rad) ** 2
    lab, n = ndi.label(mask)
    keep = np.zeros_like(mask)
    for i in range(1, n + 1):
        cols = np.where((lab == i).any(axis=0))[0]
        if (cols.max() - cols.min()) / cal["cpu"] >= 0.3:
            keep |= lab == i
    return h.read_runs(cal, keep, at, lambda rs, col: rs[0] if len(rs) == 1 else None,
                       "orange critical branch of Fig. 7(c)")
