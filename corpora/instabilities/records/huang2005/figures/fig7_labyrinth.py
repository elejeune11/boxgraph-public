"""Fig. 7 (PDF p. 12): the red squares, 'Labyrinths pattern' (simulation), not the legend square.

Reading by the shared code in _common.py (see its docstring for the calibration and intervals).
"""
import importlib.util
from pathlib import Path

PARAMS = {'xlabels': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'ylabels': [0, 0.5, 1, 1.5, 2, 2.5, 3], 'xscale': 'linear', 'yscale': 'linear', 'color': 'red', 'open_px': 8, 'close_px': 5, 'min_area': 600, 'box': (30, 50), 'margin': 2, 'legend': True}


def _common():
    spec = importlib.util.spec_from_file_location("huang2005_figures_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    return _common().read_markers_p(image, PARAMS)
