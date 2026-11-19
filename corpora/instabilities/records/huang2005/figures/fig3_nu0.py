"""Fig. 3 (PDF p. 6): the green curve, labelled 0 (nu_s = 0).

Reading by the shared code in _common.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path

PARAMS = {'xlabels': [0.01, 0.1, 1, 10], 'ylabels': [1, 10, 100, 1000], 'xscale': 'log10', 'yscale': 'log10', 'color': 'green', 'seed_x': 0.02}


def _common():
    spec = importlib.util.spec_from_file_location("huang2005_figures_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    return _common().read_curve_p(image, at, PARAMS)
