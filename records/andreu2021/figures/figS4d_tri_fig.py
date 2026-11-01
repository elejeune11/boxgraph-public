"""Supplementary Fig. 4d (PDF p. 17): bead stiffness at 0 s, the black points of the triangular signals 0.125-4 Hz with their error bars

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
CONFIG = {'ylabels': [0.0, 0.1, 0.2, 0.3],
 'xlabels': [0.125, 0.25, 0.5, 1, 2, 4, 'Sq'],
 'xscale': 'log10',
 'color': [0, 0, 0],
 'error_bars': True,
 'legend': False,
 'read': [0.125, 0.25, 0.5, 1, 2, 4]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("andreu2021_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_markers_at(image, at, CONFIG)
