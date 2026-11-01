"""Supplemental figure 4(b) (PDF p. 23): the magenta curve, b = 80 (legend).

Read by the shared code in _kit.py (see its docstring for the method and the intervals). Only the
printed tick labels matched to the ticks found are given here (inner ticks: the corner ticks merge
with the frame).
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_kit", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)

XLABELS = [2, 4, 6]
YLABELS = [0.8, 0.6, 0.4, 0.2]


def read(image, at):
    return _kit.read_curve(image, at, XLABELS, YLABELS, color=(191, 0, 191), inner=True, legend_text=True)
