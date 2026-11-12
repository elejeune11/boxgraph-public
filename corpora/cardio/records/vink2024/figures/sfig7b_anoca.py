"""Supplemental Fig. 7B (PDF p. 18): every red dot (ANOCA patients): fold MBF during hyperinsulinemia (axis 'ΔMBFinsulin') against M-value.
Read by the shared scatter code in _scatter.py (calibration, colour masks, fused markers: see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_scatter", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_scatter.py"))
_s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s)

Y = [3.0, 2.0, 1.0, 0.0]   # y tick labels, top to bottom, as printed
X = [0.0, 50.0, 100.0, 150.0]   # x tick labels, left to right, as printed (major ticks)


def read(image, at):
    return _s.read_points(image, Y, X, "red")
