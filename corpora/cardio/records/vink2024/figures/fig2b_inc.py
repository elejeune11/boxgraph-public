"""Fig. 2B (PDF p. 5): the bars of the CFT entity 'Inconclusive ICFT (n=9), dotted pink' at Baseline, Insulin and Stress (bars 3, 7, 11 of 12 from the left), with their SD error bars.
Read by the shared bar-chart code in _bars.py (calibration, bar tops, error bars: see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_bars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [0.8, 0.6, 0.4, 0.2, 0.0]   # y tick labels, top to bottom, as printed
ORDER = {1: 3, 2: 7, 3: 11}   # study state index -> bar number from the left of the panel


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=12)
