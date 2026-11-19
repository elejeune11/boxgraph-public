"""Fig. 3 (PDF p. 3): the solid curve, labelled E1/Ep = 4 (the upper curve).

Reading by the shared code in _fig3.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("bowden1998_fig3", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, 0)
