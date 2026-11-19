"""Fig. 5 (PDF p. 11), main panel: the primary ruga phase diagram, kbar against eps.

Calibration by `_diab.calibrate`: x ticks labelled 0, 0.2, ..., 1.0 and y ticks labelled 0, 0.5, ...,
3.0 (the lowest y tick is the x axis's own stub left of the y axis), found as tick marks outside the
axes. The inset has its own axes further right and is not touched by these readings.
The ink is opened with an 11 px square, which removes the thin dash-dot guide lines (kbar = 3.0, 1.30,
0.47), the arrows' shafts, the ellipse around R and the asterisks' strokes, and keeps the plotted curves
(about 24 px); pieces smaller than 2.5 x 11^2 px are dropped.
- C12/C13 (solid, with the FEM dashed line superposed on C13): followed (`_diab.read_tracked`) from the
  lowest stroke at eps = 0.1;
- C2c, lower branch (dashed, from T towards R): followed from the first stroke, from eps = 0.35
  outwards, with its centre between kbar = 0.1 and 0.3;
- C2c, upper branch (steep dashes from T up to M): the dash pieces lying wholly more than 1.5 line
  widths below the followed C12, with columns between eps = 0.175 and 0.27 and rows above kbar = 0.52
  (clear of the T marker), taken as centre lines (`_diab.piece_points`) and read by local line fits.
"""
import importlib.util
from pathlib import Path

import numpy as np

X_LABELS = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
Y_LABELS = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
START = {"C12": (0.1, "lowest", (0.005, 0.365)),
         "C2c_lower": (0.35, (0.1, 0.3), (0.19, 0.59))}


def _d():
    spec = importlib.util.spec_from_file_location("diab2013_d", Path(__file__).with_name("_diab.py"))
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    return d


def read_curve(image, at, which):
    d = _d()
    if which in START:
        x0, pick, xr = START[which]
        out, *_ = d.read_tracked(image, at, X_LABELS, Y_LABELS, x0, pick=pick, x_range=xr, open_px=11)
        return out
    _, cal, c12, lw = d.read_tracked(image, [], X_LABELS, Y_LABELS, 0.1, pick="lowest",
                                     x_range=(0.005, 0.365), open_px=11)
    m = d.drop_small(d.open_mask(d.dark(image), 11), 2.5 * 11 * 11)
    X, Y = cal["x"], cal["y"]
    cc = sorted(c12)
    c_lo, c_hi, r_max = X.pix_of(0.175), X.pix_of(0.27), Y.pix_of(0.52)

    def keep(rs, cs):
        if cs.min() < c_lo or cs.max() > c_hi or rs.max() > r_max:
            return False
        rc = np.interp(cs, cc, [c12[c] for c in cc])
        return bool(np.all(rs > rc + 1.5 * lw))

    pts = d.piece_points(m, keep)
    return d.read_at(cal, pts, at, lw)
