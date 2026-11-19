"""Fig. 7(b) (PDF p. 7): the two black branches of the (k, kappa) bifurcation diagram,
kappa/(G R) against kR. The reading's `what` says which branch: `read` returns the upper one
(labelled lambda > lambda*), `read_lower` (used by fig7b_lower.py) the lower one (lambda < lambda*).

Calibration by _colour_curves.py: labelled y ticks 3, 2, 1 from the top (the 0 tick is on the x
axis); x labels 0, 5, 10, ... under every second tick (2.5 per tick).
The curves are the black pixels inside the plot box (axes and ticks cut off 8 axis-line widths
in from the axes). Where a column holds two runs, the upper run is the lambda > lambda* branch and
the lower one the lambda < lambda* branch. Right of the last column holding two runs (the upper
branch has left the crop at its top), a single run is the lower branch. Columns with three or more
runs (the S-shaped fold) and columns with one run left of that are not read.
"""
import importlib.util
from pathlib import Path

import numpy as np


def _h():
    spec = importlib.util.spec_from_file_location("haas2015_fig7", Path(__file__).with_name("_fig7.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _setup(image):
    h = _h()
    cal = h.cc().calibrate(image, [3.0, 2.0, 1.0], 2.5)
    blk = np.asarray(image).astype(int).max(axis=2) < 60
    box = blk.copy()
    m = 8 * cal["lw"]
    box[:, : cal["c_axis"] + m] = False
    box[cal["r_axis"] - m:, :] = False
    two = [c for c in range(box.shape[1]) if len(h.runs(box, c)) == 2]
    last_two = max(two) if two else box.shape[1]
    return h, cal, box, last_two


def read(image, at):
    h, cal, box, last_two = _setup(image)
    return h.read_runs(cal, box, at, lambda rs, col: rs[0] if len(rs) == 2 else None,
                       "upper black branch (lambda > lambda*) of Fig. 7(b)")


def read_lower(image, at):
    h, cal, box, last_two = _setup(image)

    def pick(rs, col):
        if len(rs) == 2:
            return rs[1]
        if len(rs) == 1 and col > last_two:
            return rs[0]
        return None
    return h.read_runs(cal, box, at, pick, "lower black branch (lambda < lambda*) of Fig. 7(b)")
