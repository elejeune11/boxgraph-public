"""Fig. 2B (PDF p. 4): mean spreading speed vs viscosity, kl = 0.1 pN/nm, brown down
triangles (ka = 0.5).  Read by the shared code in _common.py (see its docstring): axes
from the interior inward ticks; the triangles touch their neighbours, so their x
positions are those of the green squares (same grid, found in this image), and at each
the brown blob left after eroding away the connecting line is the marker.  Below
eta = 1.5 the triangles lie under the green squares and are not read.
"""
import importlib.util
from pathlib import Path

SPEC = {
    "x": {"labels": [0.1, 1, 10], "scale": "log10"},
    "y": {"labels": [110, 100, 90, 80, 70]},
    "color": [150, 45, 10], "tol": 80, "erode": 5, "window_px": 80, "min_area": 150,
    "center_px": 15, "pad": 40, "src_px": 8, "x_min": 1.5,
    "grid_from": {"color": [10, 125, 10], "tol": 80, "square": [28, 19], "score": 0.7, "pad": 40},
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
