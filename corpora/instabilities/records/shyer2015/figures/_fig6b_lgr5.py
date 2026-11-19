"""Fig. 6B (PDF p. 9), the Lgr5 panels (Control, Inside-out): Lgr5 FISH molecules per unit area at the fold
base and tip (bars 1 and 2; x = 1 base, 2 tip), with their error bars. Each panel prints 0.08, 0.06, 0.04,
0.02; the top tick (unlabelled) is 0.10 and the x axis 0 by the even spacing, which the fit's misfit checks.
Read by the shared bar-chart code in _xlbars.py (see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_xlbars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_xlbars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [0.10, 0.08, 0.06, 0.04, 0.02, 0.0]
ORDER = {1.0: 1, 2.0: 2}


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=2)
