"""Fig. 5, middle left (nu_s = 0.4) (PDF p. 9): the curve labelled 10^4 (red).

Reading by the shared code in _common.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path

PARAMS = {'xlabels': [0.1, 1, 10, 100, 1000], 'ylabels': [10, 100], 'xscale': 'log10', 'yscale': 'log10', 'color': 'red', 'seed_x': 300, 'seed_rank': 0, 'open_px': 2}


def _common():
    spec = importlib.util.spec_from_file_location("huang2005_figures_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    return _common().read_curve_p(image, at, PARAMS)
