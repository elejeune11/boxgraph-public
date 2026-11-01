"""Fig. S5A, S5B, S5C (PDF p. 48): aggregate step-size histograms, main axes.

The three panels share their layout, so the three readings share this file. Reads with the shared code in _matlab_bars.py (pinned by its hash). Labels
matched on the page: x box edges -1 and 1, inner ticks -0.5, 0, 0.5; y box edges
0 and 0.6, inner ticks 0.1 ... 0.5. Bins are spaced as the bars found; a bin with
no bar above the axis line reads 0 (the insets read the small bars).
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_matlab_bars.py")
SHARED_SHA256 = "d6216f0ee9bea86d663b0c973809fcbb164dad4e3d8272760312b4a98d90102a"
X_TICKS, X_EDGES = [-0.5, 0.0, 0.5], [-1.0, 1.0]
Y_TICKS, Y_EDGES = [0.1, 0.2, 0.3, 0.4, 0.5], [0.0, 0.6]


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_matlab_bars.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("matlab_bars", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bx = mod.box(image)
    cal = mod.calibrate(image, bx, X_TICKS, Y_TICKS, X_EDGES, Y_EDGES)
    return mod.read_bars(image, bx, cal)
