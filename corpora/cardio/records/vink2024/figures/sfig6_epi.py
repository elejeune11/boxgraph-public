"""Supplemental Fig. 6 (PDF p. 17): the bar of the CFT entity 'Epicardial spasm, light peach' (bar 1 of 4), with its error bar; placed at state 2 (the clamp).
Read by the shared bar-chart code in _bars.py (calibration, bar tops, error bars: see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_bars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [100.0, 80.0, 60.0, 40.0, 20.0, 0.0]   # y tick labels, top to bottom, as printed
ORDER = {2: 1}   # study state index -> bar number from the left of the panel


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=4)
