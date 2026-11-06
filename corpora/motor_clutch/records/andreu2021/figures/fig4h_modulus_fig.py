"""Fig. 4h (PDF p. 7): apparent Young's modulus vs retraction speed, the red points with their error bars: fibronectin-coated beads attaching to cells (n=21 curves)

Read by `read_markers_free` in the shared code _kit.py (method and intervals in its docstring).
CONFIG holds only what the code cannot find by itself: the printed tick labels, matched in
order to the tick marks found, the series colour, and which labels are read. x of a
categorical label is its condition index (`xvalue`). The hash pins _kit.py: if it changes,
re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "fc7a7175e74f5275b3208aa387d6fe97a88df7c29519176d7af05157d23070d5"
CONFIG = {'ylabels': [0, 5, 10, 15, 20],
 'xlabels': [2, 4, 6, 8],
 'color': [250, 5, 5],
 'error_bars': True,
 'snap': 1,
 'legend': False}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("andreu2021_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_markers_free(image, at, CONFIG)
