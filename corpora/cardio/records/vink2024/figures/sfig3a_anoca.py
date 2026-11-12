"""Supplemental Fig. 3A (PDF p. 14): the red (ANOCA patients) bars of MBV in the LAD territory at Baseline, Insulin and Stress (bars 1, 3, 5 of 6), with SD error bars.
Read by the shared bar-chart code in _bars.py (calibration, bar tops, error bars: see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_bars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [1.0, 0.5, 0.0]   # y tick labels, top to bottom, as printed
ORDER = {1: 1, 2: 3, 3: 5}   # study state index -> bar number from the left of the panel


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=6)
