"""Fig. 11, bottom (wavelength) (PDF p. 17): the stars (numerical solution with interface shear), H/h = 100; symbols merged with others are not read.

Reading by the shared code in _common.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path

PARAMS = {'xlabels': [0, 5, 10, 15, 20], 'ylabels': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50], 'xscale': 'linear', 'yscale': 'linear', 'color': 'black', 'open_px': 5, 'min_area': 150, 'box': (15, 26, 15, 21), 'ratio': (0.5, 1.01)}


def _common():
    spec = importlib.util.spec_from_file_location("huang2005_figures_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    return _common().read_markers_p(image, PARAMS)
