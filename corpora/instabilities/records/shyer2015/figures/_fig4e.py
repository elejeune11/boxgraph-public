"""Fig. 4E (PDF p. 6), either panel (Control or Cyclo.): Lgr5 single-molecule FISH molecules per unit area at
the fold base and tip (bars 1 and 2 from the left; x = 1 base, 2 tip), with their SD error bars. Each panel
prints its own labels 0.05 to 0.01; the x axis is 0. The axis and ticks are pale grey (about 190-225; the
axis's antialiased edge column is about 235), so axis ink is g < 230, and the bars
are found 16 px above the x axis (above its blurred edge; every bar here is far taller). Read by the shared bar-chart code in _xlbars.py (see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_xlbars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_xlbars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [0.05, 0.04, 0.03, 0.02, 0.01, 0.0]
ORDER = {1.0: 1, 2.0: 2}


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=2, axis_ink=230, base_up=16)
