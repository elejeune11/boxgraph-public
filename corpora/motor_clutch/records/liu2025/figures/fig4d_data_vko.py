"""Fig. 4(d) (PDF p. 10): measured retrograde actin flow of vinculin-KO MEF cells (green
left-pointing triangle, right of the axis break, at the 10^11 tick), data of refs. 13, 21.

Shared code in _hd.py. x: log axis, decade ticks 10^2 ... 10^6 left of the break; the point
right of the break sits at the last tick, labelled 10^11. y: ticks 0, 40, 80, 120. The symbol:
blob of the fill colour, at its centroid; the legends are left out.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "major": 0.8, "region": (400, 1620)},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)], "major": 0.8, "region": (100, 1650)},
    "break": (0.68, 1e11),
    "box": lambda s: (s["c1"] + 2, s["y_from"], 10 ** 6, s["r0"] - 1),
}
EXCLUDE = [(0, 0, 2500, 190), (1437, 525, 2250, 900)]


def read(image, at):
    return H.read_symbols(image, SPEC, (70, 215, 70), 60, "left", exclude=EXCLUDE, mode="fill", min_area=40)
