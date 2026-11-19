"""Fig. 2A (PDF p. 4): the light grey 'Mid' bars at E12, E15 and E19 (bars 2, 5, 8 of 9 from the left), with
their SD error bars. Read by the shared bar-chart code in _xlbars.py (see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_xlbars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_xlbars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]   # y tick labels, top to bottom, as printed
ORDER = {12.0: 2, 15.0: 5, 19.0: 8}          # embryonic day (x label) -> bar number from the left


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=9)
