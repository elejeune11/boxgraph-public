"""Fig. 1d (stress relaxing minus elastic), the line for 100 lig um^-2 (grey levels darkest to lightest: 400, 225, 100, 56, 6). The y axis is labelled in nm^2 x 10^4; values are returned in nm^2. Calibrated on the labels '0' and '3.0'; the bottom label '-4.0' is not used (it does not fit a linear axis through the other two).
Line colours sampled from the crop; the seed is a pixel on the chosen line, from which it is
traced both ways. Axis calibration: x from the centres of its printed labels [0.01, 0.1, 1, 10] (log10); y from the centres of its printed labels [0, 30000]. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

PALETTE = {'l400': (35, 34, 33), 'l225': (76, 76, 78), 'l100': (108, 110, 112), 'l56': (146, 147, 146), 'l6': (189, 186, 185)}
X = {'mode': 'labels', 'values': [0.01, 0.1, 1, 10], 'log': True, 'band': 200, 'gap': 40, 'rows': [1820, 2010]}
Y = {'mode': 'labels', 'values': [0, 30000], 'band': 300, 'gap': 40, 'skip': [0], 'rows': [0, 1820]}
SEED = (504, 572)


def read(image, at):
    return K.curve_panel(image, PALETTE, 'l100', X, Y, at, SEED, tol=22)
