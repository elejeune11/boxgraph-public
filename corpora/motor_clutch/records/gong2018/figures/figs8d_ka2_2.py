"""Fig. S8D (PDF p. 19): spreading speed vs second timescale tau_s2, orange down
triangles (ka,2 = 2).  Read by the shared code in _common.py (see its docstring): axes
from the interior inward ticks (0.1, 1, 10; 110 to 80); triangles as the blobs left
after eroding away the connecting line.  Markers below tau = 0.05 and at 0.1 merge
with the blue circles and are not read; the marker on the right spine is cut.
"""
import importlib.util
from pathlib import Path

SPEC = {
    "tick_px": 14,
    "x": {"labels": [0.1, 1, 10], "scale": "log10"},
    "y": {"labels": [110, 100, 90, 80]},
    "color": [210, 70, 10], "tol": 80, "erode": 5, "min_px": 40, "max_px": 85,
    "center_px": 9, "pad": 40, "src_px": 8, "x_max": 70,
    # the legend at the top left of the plot
    "exclude": [[450, 330, 1120, 670]],
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
