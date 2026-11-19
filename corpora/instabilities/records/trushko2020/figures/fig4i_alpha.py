"""Fig. 4I (PDF p. 9): the green curve, alpha against P_B R^3 for the fitted K = 0.5 uN um.

Shared code in _fig4.py. The green legend line lies at the top right, above the curve, so the
lowest green run in a column is taken.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("trushko2020_fig4", Path(__file__).with_name("_fig4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    return m.read_curve(image, at, m.GREEN, 50.0, 10.0, pick="bottom")
