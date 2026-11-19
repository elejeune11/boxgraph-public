"""Fig. 6B and 6D (PDF p. 9), the EdU panels (Control, Inside-out, Grid): percent EdU-positive cells in fold
sub-regions 1-6 (bars 1-6 from the left), quantified as in Fig. 4, with their error bars. Each panel prints
80, 60, 40, 20; the top tick (unlabelled) is 100 and the x axis 0 by the even spacing, which the fit's
misfit checks. Read by the shared bar-chart code in _xlbars.py (see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_xlbars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_xlbars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [100, 80, 60, 40, 20, 0]
ORDER = {float(i): i for i in range(1, 7)}


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=6)
