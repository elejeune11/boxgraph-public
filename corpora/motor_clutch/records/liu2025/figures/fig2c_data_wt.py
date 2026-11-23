"""Fig. 2(c) (PDF p. 5): measured cell traction of MEF WT cells (pink circles) against E.

Shared code in _hd.py. x: log axis, the decade ticks 10^2, 10^4, 10^6 below the left part of the
broken axis (the ticks right of the break are not used); y: ticks 0, 60, 120, 180.
Symbols: pink fill, circle outline matched to the dark pixels.
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
FILL = (248, 152, 152)
SHAPE = "circle"
LEGEND = [(0, 0, 900, 500), (1150, 500, 2133, 1150)]


def _box(cal):
    sp = cal["sp"]
    return (sp["c1"] + 2, sp["y_from"], sp["x_to"], sp["r0"] - 1)


def read(image, at):
    cal = H.calibrate(image, SPEC)
    return H.clean(H.symbols(image, FILL, 60, SHAPE, cal["x"], cal["y"], _box(cal), exclude=LEGEND,
                                     seed_open=0.25, min_frac=0.03))
