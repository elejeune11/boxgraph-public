"""Fig. S1(b) (PDF p. 20): total traction force per Y-27632 condition, navy bars with blue error bars; categories 1-4 = WT, 2, 5, 10 uM.

Read by the shared code in _kit.py (see its docstring for the method and the intervals). Only the
printed tick labels matched to the ticks found are given here.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_kit", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)

XLABELS = [1, 2, 3, 4]
YLABELS = [250, 200, 150, 100, 50]


def read(image, at):
    return _kit.read_bars(image, at, XLABELS, YLABELS)
