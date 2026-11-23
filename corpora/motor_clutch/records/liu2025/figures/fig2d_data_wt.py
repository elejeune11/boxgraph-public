"""Fig. 2(d) (PDF p. 5): measured retrograde actin flow of MEF WT cells (pink circles) against E.

Shared code in _hd.py. x: log axis, decade ticks 10^2, 10^4, 10^6 (with 10^3, 10^5 between them)
left of the axis break; the point right of the break sits on the last tick, labelled 10^11.
y: ticks 0, 40, 80, 120. Symbols: pink fill, circle outline matched to the dark pixels.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "region": (340, 1560)},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)]},
    "break": (0.72, 1e11),
    "box": lambda s: (s["c1"] + 2, s["y_from"], 10 ** 6, s["r0"] - 1),  # both sides of the break
}
LEGEND = [(418, 1045, 990, 1430), (1353, 572, 2200, 1100)]


def read(image, at):
    return H.read_symbols(image, SPEC, (248, 152, 152), 60, "circle", exclude=LEGEND)
