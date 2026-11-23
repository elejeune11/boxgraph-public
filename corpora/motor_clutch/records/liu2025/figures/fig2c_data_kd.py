"""Fig. 2(c) (PDF p. 5): measured cell traction of MEF Talin 1 KO, Talin 2 shRNA cells (green
triangles) against E.

Same calibration as fig2c_data_wt (shared code in _hd.py). Symbols: light-green fill (distinct
from the darker green model curve), upward-triangle outline matched to the dark pixels.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "region": (250, 1450)},
    "y": {"marks": [(0, 0), (1, 60), (2, 120), (3, 180)]},
}
FILL = (119, 255, 119)
LEGEND = [(0, 0, 900, 500), (1150, 500, 2133, 1150)]


def read(image, at):
    cal = H.calibrate(image, SPEC)
    sp = cal["sp"]
    box = (sp["c1"] + 2, sp["y_from"], sp["x_to"], sp["r0"] - 1)
    return H.clean(H.symbols(image, FILL, 45, "up", cal["x"], cal["y"], box, exclude=LEGEND, min_fill=0.1))
