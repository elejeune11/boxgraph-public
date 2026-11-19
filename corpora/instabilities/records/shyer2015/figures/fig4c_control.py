"""Fig. 4C (PDF p. 6), first panel (Control): percent EdU-positive cells in fold sub-regions 1-6 (bars 1-6
from the left), with their error bars. Read by the shared bar-chart code in _xlbars.py (see its docstring).
Ticks: this panel prints 80, 60, 40, 20; the top tick (unlabelled) is 100 and the x axis 0 by the even spacing,
which the fit's misfit checks."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_xlbars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_xlbars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [100, 80, 60, 40, 20, 0]
ORDER = {float(i): i for i in range(1, 7)}   # region number (x label) -> bar number from the left


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=6)
