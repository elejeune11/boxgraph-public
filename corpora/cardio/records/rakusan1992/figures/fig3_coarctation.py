"""Fig. 3 (PDF p. 5), capillary domain area against heart mass: every open triangle (aortic coarctation) that can be told apart.

Reading by the shared code in _scatter.py (see its docstring and that of the function called for the
calibration, how the markers or the curve are found, and the intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("rakusan1992_scatter", Path(__file__).with_name("_scatter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_markers(image, "coa", mod.FIG3)
