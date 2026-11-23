"""Fig. 2(d) (PDF p. 5): measured retrograde actin flow of MEF Talin 1 KO, Talin 2 shRNA cells
(green triangles) against E.

Calibration as fig2d_data_wt (shared code in _hd.py). Symbols: light-green fill (distinct from the
darker green model curve), upward-triangle outline matched to the dark pixels.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "region": (340, 1560)},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)]},
}
LEGEND = [(418, 1045, 990, 1430), (1353, 572, 2200, 1100)]


def read(image, at):
    return H.read_symbols(image, SPEC, (119, 255, 119), 45, "up", exclude=LEGEND, min_fill=0.1)
