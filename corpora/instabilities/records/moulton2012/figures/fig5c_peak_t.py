"""Fig. 5(c) (PDF p. 5): time of the n-th maximum of r_s (n-th rib), n = the values in `at`.

Shared reading code in _fig5.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("moulton2012_fig5", Path(__file__).with_name("_fig5.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.peaks(image, at, "time")
