"""Fig. 2a, the red line (Ionic): normalized stress against time in a stress-relaxation test.
Line colours sampled from the crop; the seed is a pixel on the chosen line, from which it is
traced both ways. Axis calibration: x from its tick marks, valued [0.1, 1, 10, 100, 1000] (log10); y from its tick marks, valued [0.2, 0.4, 0.6, 0.8, 1.0]. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

PALETTE = {'axis': (4, 4, 4), 'covalent': (68, 68, 68), 'ionic': (204, 36, 44)}
X = {'mode': 'ticks', 'values': [0.1, 1, 10, 100, 1000], 'log': True}
Y = {'mode': 'ticks', 'values': [0.2, 0.4, 0.6, 0.8, 1.0]}
SEED = (1200, 500)


def read(image, at):
    return K.curve_panel(image, PALETTE, 'ionic', X, Y, at, SEED, ink_thr=40, tol=80)
