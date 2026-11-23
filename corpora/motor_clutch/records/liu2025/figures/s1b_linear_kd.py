"""Fig. S1(b) (PDF p. 49): the green curve, linear KD model, mean tension of an engaged (non-talin)
molecular clutch against E.

Shared code in _hd.py. x: log axis, the long decade ticks 10^2 ... 10^6 (labelled 10^2, 10^4,
10^6); y: log axis, the long ticks 0.1, 1, 10, 100. The curve: pixels of the pure green, the only
green line in the panel; the legend is left out.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "major": 0.8},
    "y": {"scale": "log10", "marks": [(0, 0.1), (1, 1), (2, 10), (3, 100)], "major": 0.8},
}
LEGEND = [(735, 100, 1440, 400)]


def read(image, at):
    cal = H.calibrate(image, SPEC)
    sp = cal["sp"]
    box = (sp["c1"] + 2, 0, sp["x_to"] + 3, sp["r0"] - 1)
    return H.curve(image, (0, 220, 0), 90, cal["x"], cal["y"], at, box, pick="top", exclude=LEGEND)
