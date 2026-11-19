"""Fig. 7 (PDF p. 12): the black line, 'Stripes pattern (Analytical solution)'.

Reading by the shared code in _common.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path

PARAMS = {'xlabels': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'ylabels': [0, 0.5, 1, 1.5, 2, 2.5, 3], 'xscale': 'linear', 'yscale': 'linear', 'color': 'black', 'seed_x': 6}


def _common():
    spec = importlib.util.spec_from_file_location("huang2005_figures_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    return _common().read_curve_p(image, at, PARAMS)
