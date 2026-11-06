"""Fig. 2(b) (PDF p. 5): the load-extension loop of the first cycle: loading (solid) and unloading (dashed) together, as one band.

Reading by the shared code in _fig2.py (see its docstring for the calibration, how the curves or
markers are told apart and the intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("alastruey2011_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, {"curve": "loop", "x": [0, 0.2, 0.4, 0.6, 0.8, 1], "y": [1, 0.8, 0.6, 0.4, 0.2, 0]})
