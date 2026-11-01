"""Supplementary Fig. 4e (PDF p. 17): force loading rate vs time, the 0.125 Hz series (n=19 beads) at 32-160 s with its error bars. The y axis is calibrated on its 100, 1000 and 10000 ticks (the lower ticks are covered by the markers at 0 s, which sit on the axis and are not read); the 0 s x tick is hidden the same way

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
CONFIG = {'ylabels': [100, 1000, 10000],
 'yscale': 'log10',
 'yprobe': [12, 18],
 'xlabels': [32, 64, 96, 128, 160],
 'error_bars': True,
 'read': [32, 64, 96, 128, 160],
 'legend': False,
 'tol': 40,
 'color': [140, 125, 53]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("andreu2021_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_markers_at(image, at, CONFIG)
