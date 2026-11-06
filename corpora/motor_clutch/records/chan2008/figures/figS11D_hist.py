"""Fig. S11D (PDF p. 54): histogram of normalized radial deviation of reference beads.

Reads with the shared code in _matlab_bars.py (pinned by its hash). Labels
matched on the page: x box edges 0 and 16, inner ticks 2 ... 14; y box edges 0
and 15, inner ticks 5 and 10. Bins (1 nm) are spaced as the bars found; a bin
with no bar above the axis line reads 0.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_matlab_bars.py")
SHARED_SHA256 = "d6216f0ee9bea86d663b0c973809fcbb164dad4e3d8272760312b4a98d90102a"
X_TICKS, X_EDGES = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0], [0.0, 16.0]
Y_TICKS, Y_EDGES = [5.0, 10.0], [0.0, 15.0]


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_matlab_bars.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("matlab_bars", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bx = mod.box(image)
    cal = mod.calibrate(image, bx, X_TICKS, Y_TICKS, X_EDGES, Y_EDGES)
    return mod.read_bars(image, bx, cal)
