"""Fig. 4(f) (PDF p. 10): traction peak location against F with b = 0, the black dots with grey error bars.

Read by the shared code in _kit.py (see its docstring for the method and the intervals). Only the
printed tick labels matched to the ticks found are given here.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_kit", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)

XLABELS = [0, 2, 4, 6, 8, 10]
YLABELS = [4, 3, 2, 1, 0]


def read(image, at):
    return _kit.read_dots(image, at, XLABELS, YLABELS, bars='grey')
