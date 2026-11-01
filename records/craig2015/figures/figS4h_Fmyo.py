"""Supplemental figure 4(h) (PDF p. 23): the blue curve, myosin force (caption), b = 40.

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
YLABELS = [0.16, 0.12, 0.08, 0.04]


def read(image, at):
    return _kit.read_curve(image, at, XLABELS, YLABELS, color=(0, 0, 255), inner=True, legend_text=True)
