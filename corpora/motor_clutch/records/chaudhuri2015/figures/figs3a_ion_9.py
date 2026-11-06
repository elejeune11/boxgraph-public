"""Supp. Fig. 3a, the line Ionic 9 kPa (blue): normalized stress against time. The panel is an embedded bitmap.
Line colours sampled from the crop; the seed is a pixel on the chosen line, from which it is
traced both ways. Axis calibration: x from its tick marks, valued [0.1, 1, 10, 100, 1000] (log10); y from its tick marks, valued [0.2, 0.4, 0.6, 0.8, 1.0]. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

PALETTE = {'black': (28, 28, 20), 'dgrey': (100, 92, 84), 'lgrey': (172, 164, 156), 'green': (44, 140, 60), 'blue': (76, 60, 124), 'red': (228, 52, 44)}
X = {'mode': 'ticks', 'values': [0.1, 1, 10, 100, 1000], 'log': True, 'min_len': 30, 'max_len': 160}
Y = {'mode': 'ticks', 'values': [0.2, 0.4, 0.6, 0.8, 1.0], 'min_len': 30, 'max_len': 160}
SEED = (3080, 1829)


def read(image, at):
    return K.curve_panel(image, PALETTE, 'blue', X, Y, at, SEED, tol=40, ink_thr=60, extra_px=4.0, max_jump=25)
