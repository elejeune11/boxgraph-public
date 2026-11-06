"""Fig. S5A-C (PDF p. 48): the left insets (large negative steps), one reading per panel.

Reads with the shared code in _matlab_bars.py (pinned by its hash). Labels
matched on the page: x ticks -0.9, -0.6, -0.3 (the box edges carry no label);
y box edges 0 and 0.01, inner tick 0.005. Bins are spaced as in the bars found
(or from the bar width when no two bars are neighbours); a bin with no bar
above the axis line reads 0.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_matlab_bars.py")
SHARED_SHA256 = "d6216f0ee9bea86d663b0c973809fcbb164dad4e3d8272760312b4a98d90102a"
X_TICKS, X_EDGES = [-0.9, -0.6, -0.3], None
Y_TICKS, Y_EDGES = [0.005], [0.0, 0.01]


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_matlab_bars.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("matlab_bars", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bx = mod.box(image)
    cal = mod.calibrate(image, bx, X_TICKS, Y_TICKS, X_EDGES, Y_EDGES)
    return mod.read_bars(image, bx, cal)
