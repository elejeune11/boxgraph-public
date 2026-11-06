"""Fig. S1A of gong2018 (PDF p. 14): mean spreading speed vs stiffness of an
elastic substrate, KMC (blue open squares) and ODE (red open circles).

Axes by _axes.py from the inward ticks on the top spine (x: 0.1, 1, 10; 0.01 and
100 at the corners) and on the left spine (y: 120, 100, 80, 60; 40 at the bottom
spine; the marker at 0.01 touches this spine and is dropped as not evenly spaced
with the ticks; the right spine is touched by the plateau markers at 120).  Markers by the template code of _common.py
(annulus for the circles, open square for the squares), applied with this
calibration.  Intervals as in _common.py.
"""
import importlib.util
from pathlib import Path

AXES = {
    "tick_px": 16,
    "x": {"labels": [0.01, 0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"], "band": "top"},
    "y": {"labels": [120, 100, 80, 60, 40], "edge_ticks": ["end"], "band": "left", "regular": True},
}
SERIES = {
    # the coloured labels "ODE method" and "KMC method" inside the plot are excluded
    "ode": {"color": [217, 83, 25], "tol": 90, "ring": [20, 32], "score": 0.6, "pad": 30,
            "exclude": [[1100, 1200, 1700, 1310]], "src_px": 8},
    "kmc": {"color": [0, 114, 189], "tol": 90, "square": [30, 12], "score": 0.7, "pad": 30,
            "exclude": [[290, 975, 910, 1085]], "src_px": 8},
}


def _load(name):
    spec = importlib.util.spec_from_file_location(f"gong2018{name}", Path(__file__).with_name(f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _on_grid(pts, snap=12):
    """The squares are evenly spaced in log k: fit the pitch (median spacing) and
    the phase (circular mean of column mod pitch), keep one marker per grid
    position, the nearest, within `snap` px (the template also fires where a
    circle overlaps a square, between two grid positions)."""
    import numpy as np
    cols = np.array([p["px"][0] for p in pts])
    pitch = float(np.median(np.diff(np.sort(cols))))
    ang = 2 * np.pi * cols / pitch
    phase = float(np.angle(np.exp(1j * ang).mean())) * pitch / (2 * np.pi)
    best = {}
    for p, c in zip(pts, cols):
        k = int(round((c - phase) / pitch))
        d = abs(c - phase - k * pitch)
        if d <= snap and (k not in best or d < best[k][0]):
            best[k] = (d, p)
    return [best[k][1] for k in sorted(best)]


def read(image, at, key):
    xa, ya, box = _load("_axes").calibrate(image, AXES)
    pts = _load("_common").markers(image, SERIES[key], xa, ya, box)
    return _on_grid(pts) if key == "kmc" else pts
