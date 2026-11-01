"""Fig. S2(a) (PDF p. 21): traction peak location against lambda, black dots with black error bars (the 6 tick merges with the frame; the 0, 2, 4 ticks are used).

Read by the shared code in _kit.py (see its docstring for the method and the intervals). Only the
printed tick labels matched to the ticks found are given here.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_kit", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)

XLABELS = [1, 2, 3, 4]
YLABELS = [4, 2, 0]


def read(image, at):
    return _kit.read_dots(image, at, XLABELS, YLABELS, bars='dark')
