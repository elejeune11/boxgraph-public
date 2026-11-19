"""Fig. 4a (PDF p. 3): sigma_y, the upper curve, with its minimum at the step.

Reading by the shared code in _fig4a.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("bowden1998_fig4a", Path(__file__).with_name("_fig4a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curves(image, at, 0)
