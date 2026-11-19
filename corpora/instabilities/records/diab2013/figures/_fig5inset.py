"""Fig. 5 (PDF p. 11), inset: kbar against eps near the R-point, with the fold-crease curve C4c (dashed)
and the folding curve C24 (dotted).

Calibration by `_diab.calibrate`: x ticks labelled 0.57, 0.62, 0.67, 0.72 and y ticks labelled 0.085,
0.095, 0.105, 0.115, found as tick marks outside the axes (the short mark eps_R standing on the x axis
inside the plot is not one of them).
- C4c: the ink opened with a 15 px square (removes the dash-dot guide lines at the R- and (e)/(f)-levels
  and the asterisks' thin strokes), followed (`_diab.read_tracked`) from the first stroke, from
  eps = 0.66 outwards, with its centre between kbar = 0.093 and 0.099.
- C24: the dots of the dotted line, as pieces of the ink opened with a 7 px square that are between 8
  and 40 px in both directions (dots, not letters), lie between eps = 0.598 and 0.632 and between
  kbar = 0.086 and 0.1025 (below the asterisk (e)); their centres are read by local line fits, with
  the dot size as the line width.
"""
import importlib.util
from pathlib import Path

X_LABELS = [0.57, 0.62, 0.67, 0.72]
Y_LABELS = [0.085, 0.095, 0.105, 0.115]


def _d():
    spec = importlib.util.spec_from_file_location("diab2013_d", Path(__file__).with_name("_diab.py"))
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    return d


def read_curve(image, at, which):
    d = _d()
    if which == "C4c":
        out, *_ = d.read_tracked(image, at, X_LABELS, Y_LABELS, 0.66, pick=(0.093, 0.099),
                                 x_range=(0.583, 0.70), open_px=15)
        return out
    dk = d.dark(image)
    cal = d.calibrate(dk, X_LABELS, Y_LABELS)
    X, Y = cal["x"], cal["y"]
    m = d.open_mask(dk, 7)
    c_lo, c_hi = X.pix_of(0.598), X.pix_of(0.632)
    r_lo, r_hi = Y.pix_of(0.1025), Y.pix_of(0.086)
    sizes = []

    def keep(rs, cs):
        h, w = rs.max() - rs.min() + 1, cs.max() - cs.min() + 1
        ok = (8 <= h <= 40 and 8 <= w <= 40 and c_lo <= cs.mean() <= c_hi and r_lo <= rs.mean() <= r_hi)
        if ok:
            sizes.append((h + w) / 2)
        return ok

    pts = d.piece_points(m, keep)
    lw = float(sorted(sizes)[len(sizes) // 2]) if sizes else 15.0
    return d.read_at(cal, pts, at, lw, win=120, extra_note=f"; {len(sizes)} dots")
