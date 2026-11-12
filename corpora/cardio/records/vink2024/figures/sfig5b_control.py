"""Supplemental Fig. 5B (PDF p. 16): the blue (Controls) bars of fold MBF (axis 'ΔMBF') at Insulin (state 2) and Stress (state 3), bars 2 and 4 of 4, with error bars; the crop starts below the legend, so the top tick (8) is not used.
Read by the shared bar-chart code in _bars.py (calibration, bar tops, error bars: see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_bars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [6.0, 4.0, 2.0, 0.0]   # y tick labels, top to bottom, as printed
ORDER = {2: 2, 3: 4}   # study state index -> bar number from the left of the panel


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=4)
