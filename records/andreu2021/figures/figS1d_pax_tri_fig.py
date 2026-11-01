"""Supplementary Fig. 1d (PDF p. 13): paxillin adhesion length (red, right axis): the points of triangular stretch at 0.125-2 Hz, with their error bars; the point at 0.5 Hz is (almost) entirely behind another marker and is not read

Read by `read_markers_at` in the shared code _kit.py (method and intervals in its docstring).
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
CONFIG = {'ylabels': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
 'xlabels': ['Ns', 0.125, 0.25, 0.5, 1, 2, 'Sq'],
 'xscale': 'log10',
 'error_bars': True,
 'color': [231, 49, 51],
 'axis': 'right',
 'y2labels': [0, 1, 2, 3],
 'read': [0.125, 0.25, 1, 2]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("andreu2021_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_markers_at(image, at, CONFIG)
