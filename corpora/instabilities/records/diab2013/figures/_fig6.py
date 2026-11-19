"""Fig. 6 (PDF p. 12): local compressive strain eps_l near the nucleation point of creasing against the
applied nominal compressive strain eps, finite-element results for six kbar.

Calibration by `_diab.calibrate`: x ticks labelled 0, 0.1, ..., 0.8 and y ticks labelled 0, 0.1, ...,
0.5 (the lowest is the x axis's stub), found as tick marks outside the axes.
Line styles, matched to the legend by their dash pattern and by where each ends (the curve of
kbar = 2.510 rises vertically at about 0.355, the curve of 0.204 at about 0.31):
- kbar = 1.300 (solid): followed (`_diab.read_tracked`, ink opened with an 11 px square) from the
  first stroke, from eps = 0.2 outwards, with its centre between eps_l = 0.17 and 0.21;
- kbar = 0.204 (short dashes): followed from the first stroke, from eps = 0.25, between eps_l = 0.28
  and 0.34 (above the solid line, which is the only other line there);
- kbar = 2.510 (chain: dashes and single dots): followed from the first stroke, from eps = 0.31,
  between eps_l = 0.26 and 0.32; its dots are dropped as small pieces and its dashes followed;
- kbar = 0.100 (coarse dots): the dots, as pieces of the ink opened with a 7 px square that are 12-45
  px in both directions, lie between eps = 0.09 and 0.585 (left of the legend box), above eps_l = 0.04
  and more than 0.01 below the 45-degree line eps_l = eps (where every other curve lies on or above
  it); the thin dots of the eps_M and eps_B guide lines are smaller than 12 px. Their centres are read
  by local line fits with the dot size as the line width.
"""
import importlib.util
from pathlib import Path

X_LABELS = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
Y_LABELS = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
TRACKED = {"k1300": (0.2, (0.17, 0.21), (0.005, 0.268)),
           "k0204": (0.25, (0.28, 0.34), (0.2, 0.305)),
           "k2510": (0.31, (0.26, 0.32), (0.275, 0.352))}


def _d():
    spec = importlib.util.spec_from_file_location("diab2013_d", Path(__file__).with_name("_diab.py"))
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    return d


def read_curve(image, at, which):
    d = _d()
    if which in TRACKED:
        x0, band, xr = TRACKED[which]
        out, *_ = d.read_tracked(image, at, X_LABELS, Y_LABELS, x0, pick=band, x_range=xr, open_px=11)
        return out
    dk = d.dark(image)
    cal = d.calibrate(dk, X_LABELS, Y_LABELS)
    X, Y = cal["x"], cal["y"]
    m = d.open_mask(dk, 7)
    sizes = []

    def keep(rs, cs):
        h, w = rs.max() - rs.min() + 1, cs.max() - cs.min() + 1
        if not (12 <= h <= 45 and 12 <= w <= 45):
            return False
        e, el = X.val(cs.mean()), Y.val(rs.mean())
        ok = 0.09 <= e <= 0.585 and el > 0.04 and el < e - 0.01
        if ok:
            sizes.append((h + w) / 2)
        return ok

    pts = d.piece_points(m, keep)
    lw = float(sorted(sizes)[len(sizes) // 2]) if sizes else 20.0
    return d.read_at(cal, pts, at, lw, win=120, extra_note=f"; {len(sizes)} dots")
