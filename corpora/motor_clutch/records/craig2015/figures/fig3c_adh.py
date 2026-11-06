"""Fig. 3(c) right (PDF p. 9): predicted adhesion density / maximum (filled black dots), CA-Rho cell.

Read by _fig3dots.py (every dot, x read from the image; see its docstring). Only the printed inner tick
labels are given here (the corner ticks merge with the frame).
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_fig3dots", Path(__file__).with_name("_fig3dots.py"))
_f3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f3)


def read(image, at):
    # the right-hand 0.6 tick is hidden by the dots near x = 8, so the 0.6 tick pair is not found
    return _f3.read(image, at, [2, 4, 6], [0.8, 0.4, 0.2])
