"""Fig. 4 (PDF p. 8): flow harmonic amplitudes at the left renal midpoint, the triangles (visc, visco-elastic 1-D model).

Reading by the shared code in _fig4.py (see its docstring for the calibration, how the curves or
markers are told apart and the intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("alastruey2011_fig4", Path(__file__).with_name("_fig4.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_kind(image, "visc", [5, 10, 15], [0, -1, -2])
