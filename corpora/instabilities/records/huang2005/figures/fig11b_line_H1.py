"""Fig. 11, bottom (wavelength) (PDF p. 17): the solid line (analytical solution) labelled H/h = 1, line 3 from the top, read between the symbols.

Reading by the shared code in _common.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path

PARAMS = {'xlabels': [0, 5, 10, 15, 20], 'ylabels': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50], 'xscale': 'linear', 'yscale': 'linear', 'color': 'black', 'seed_x': 17.5, 'seed_rank': 2, 'remove_markers': 5}


def _common():
    spec = importlib.util.spec_from_file_location("huang2005_figures_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    return _common().read_curve_p(image, at, PARAMS)
