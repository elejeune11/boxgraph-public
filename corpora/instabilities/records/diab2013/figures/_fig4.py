"""Fig. 4 (PDF p. 10): finite-element evolution of the Fourier coefficients A1 (solid) and A2 (dashed)
against eps in panels (a) kbar = 0.628, (b) 1.30, (c) 2.51 (log10 axes), and the growth rate dA1/deps
of the three cases (i), (ii), (iii) in panel (d).

Calibration by `_diab.calibrate`: the printed tick labels of each panel (x: 0.10 ... 0.20; 0.20 ... 0.28;
0.30 ... 0.36; 0 ... 0.4; y: 1.0 x 10^-8 ... 1.0 x 10^0 in (a)-(c), 5.0 x 10^-4, 5.0 x 10^-1, 5.0 x 10^2
in (d)), found as tick marks outside the axes; the y axes are logarithmic.
The ink is opened with an 11 px square (the lines are about 24 px), which removes the thin dotted
vertical lines at eps_w and eps_c, and pieces smaller than 2.5 x 11^2 px are dropped (most dots of the
dotted and chained lines). Each curve is followed (`_diab.read_tracked`) from the first stroke, from
a start eps outwards, whose centre lies in a band of y values chosen to hold that curve alone there;
the follower bridges dashes' gaps and keeps to the curve where others cross it.
"""
import importlib.util
from pathlib import Path

DECADES = [1e-8, 1e-6, 1e-4, 1e-2, 1.0]
PANELS = {
    "a": ([0.10, 0.12, 0.14, 0.16, 0.18, 0.20], DECADES),
    "b": ([0.20, 0.22, 0.24, 0.26, 0.28], DECADES),
    "c": ([0.30, 0.32, 0.34, 0.36], DECADES),
    "d": ([0, 0.1, 0.2, 0.3, 0.4], [5e-4, 5e-1, 5e2]),
}
# panel, start eps, y band at the start, x range followed
CURVES = {
    "a_A1": ("a", 0.12, (1e-3, 1e-2), (0.10, 0.186)),
    "a_A2": ("a", 0.175, (1e-2, 1e-1), (0.157, 0.186)),
    "b_A1": ("b", 0.23, (1e-3, 1e-2), (0.20, 0.2715)),
    "b_A2": ("b", 0.26, (1e-5, 1e-3), (0.248, 0.2715)),
    "c_A1": ("c", 0.32, (1e-3, 1e-1), (0.30, 0.3515)),
    "c_A2": ("c", 0.32, (3e-6, 3e-4), (0.30, 0.3515)),
    "d_i": ("d", 0.12, (1e-2, 1e-1), (0.003, 0.156)),
    "d_ii": ("d", 0.22, (1e-2, 1e-1), (0.003, 0.27)),
    "d_iii": ("d", 0.28, (1e-2, 1e-1), (0.003, 0.35)),
}


def read_curve(image, at, which):
    spec = importlib.util.spec_from_file_location("diab2013_d", Path(__file__).with_name("_diab.py"))
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    panel, x0, band, xr = CURVES[which]
    xl, yl = PANELS[panel]
    out, *_ = d.read_tracked(image, at, xl, yl, x0, pick=band, x_range=xr, y_scale="log10", open_px=11)
    return out
