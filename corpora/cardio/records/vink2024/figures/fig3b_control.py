"""Fig. 3B (PDF p. 5): the blue (Controls) bar of M-value (bar 2 of 2), with its SD error bar; placed at state 2 (the clamp).
Read by the shared bar-chart code in _bars.py (calibration, bar tops, error bars: see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_bars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [100.0, 50.0, 0.0]   # y tick labels, top to bottom, as printed
ORDER = {2: 2}   # study state index -> bar number from the left of the panel


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=2)
