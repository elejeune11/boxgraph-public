"""Fig. 2(a) (PDF p. 5): the load F/Fmax (thin solid line), during the holds at zero and full extension.

Reading by the shared code in _fig2.py (see its docstring for the calibration, how the curves or
markers are told apart and the intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("alastruey2011_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, {"curve": "load", "x": [20, 40, 60, 80, 100], "y": [1, 0.8, 0.6, 0.4, 0.2, 0]})
