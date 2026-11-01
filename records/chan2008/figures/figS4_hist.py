"""Fig. S4 (PDF pp. 36-47): one bead's histogram of single time-increment step sizes
(third column), one reading per bead; all 67 share this file.

Reads with the shared code in _matlab_bars.py (pinned by its hash). Labels
matched on the pages: x box edges -1 and 1, inner ticks -0.5, 0, 0.5; y box
edges 0 and 120, inner ticks 20 ... 100. Every panel was checked to carry these
same labels; a panel whose tick strokes do not fit them stops the reading
(misfit over 4 px) rather than reading it on the wrong scale. Bins are spaced
as the bars found; a bin with no bar above the axis line reads 0.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_matlab_bars.py")
SHARED_SHA256 = "d6216f0ee9bea86d663b0c973809fcbb164dad4e3d8272760312b4a98d90102a"
X_TICKS, X_EDGES = [-0.5, 0.0, 0.5], [-1.0, 1.0]
Y_TICKS, Y_EDGES = [20.0, 40.0, 60.0, 80.0, 100.0], [0.0, 120.0]


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_matlab_bars.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("matlab_bars", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bx = mod.box(image)
    cal = mod.calibrate(image, bx, X_TICKS, Y_TICKS, X_EDGES, Y_EDGES)
    if cal["misfit_y"] > 4.0 or cal["misfit_x"] > 4.0:
        raise ValueError(f"tick strokes do not fit the expected labels (misfit x {cal['misfit_x']:.1f}, "
                         f"y {cal['misfit_y']:.1f} px): this panel's axes differ")
    return mod.read_bars(image, bx, cal)
