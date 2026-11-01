"""Fig. S8B and S8C, right panels, of gong2018 (PDF p. 19): relaxation spectra H(tau)
of the PA (B) and HA (C) gels, with the timescales chosen for the
multiple-timescale simulations marked by green crosses.  The crosses are read
(the spectrum line itself is a narrow-peaked curve whose values between peaks
are zero).

Axes by _axes.py: x is log10 tau, ticks on the top spine matched to the labels
10^-2, 10^0, 10^2 (the only labels printed; the box ends are not labelled); y from
0 (bottom spine) to 0.5 (top spine) with ticks on the right spine.  The
spectrum line lies on the bottom spine and hides it: the box's bottom is where
the left spine ends, less the spine's thickness (`spine_px`); the strip of the
neighbouring panel at the left edge is ignored (`min_col`).
Crosses by _points.py: the green mask opened by a disk narrower than the cross's
strokes; the legend's cross is excluded.
"""
import importlib.util
from pathlib import Path

AXES = {"tick_px": 16, "bottom_from_left": True, "spine_px": 14, "min_col": 400,
        "x": {"labels": [0.01, 1, 100], "scale": "log10", "band": "top"},
        "y": {"labels": [0.5, 0.4, 0.3, 0.2, 0.1, 0], "edge_ticks": ["start", "end"], "band": "right"}}
CROSS = {"color": [110, 180, 60], "tol": 70, "open_r": 3, "min_area": 150, "src_px": 8, "margin": 4}
LEGEND = {"b": [[1450, 230, 1700, 400]], "c": [[1480, 330, 1700, 540]]}


def read(image, panel):
    spec = importlib.util.spec_from_file_location("gong2018_points", Path(__file__).with_name("_points.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_points(image, AXES, CROSS, LEGEND[panel])
