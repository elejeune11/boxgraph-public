"""Supplementary Fig. 2a (PDF p. 14): measured gel strain vs applied voltage, the black points with their error bars (n=3 membranes); the orange line and the dotted guide lines are not read

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
CONFIG = {'ylabels': [2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25],
 'ydrop_bottom': 1,
 'xlabels': [0.0, 0.25, 0.5, 1.0, 1.5, 2.0],
 'xprobe': [17, 21],
 'x_breaks': False,
 'color': [0, 0, 0],
 'error_bars': True,
 'snap': 0.1,
 'legend': False,
 'radius_median': True}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("andreu2021_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_markers_free(image, at, CONFIG)
