"""Fig. 3A (PDF p. 5): the red (ANOCA patients) bars of MVR at Insulin (state 2) and Stress (state 3), bars 1 and 3 of 4, with SD error bars.
Read by the shared bar-chart code in _bars.py (calibration, bar tops, error bars: see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_bars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [3.0, 2.0, 1.0, 0.0]   # y tick labels, top to bottom, as printed
ORDER = {2: 1, 3: 3}   # study state index -> bar number from the left of the panel


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=4)
