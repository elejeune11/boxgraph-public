"""Supp. Fig. 1f, the line Viscoelastic (green): force in a simulated tensile test against time. The y axis is labelled 'Force (0.1 pN)'; values are returned in pN (tick label x 0.1). The panel is an embedded bitmap; ticks point inwards.
Line colours sampled from the crop; the seed is a pixel on the chosen line, from which it is
traced both ways. Axis calibration: x from its tick marks, valued [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]; y from its tick marks, valued [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

PALETTE = {'black': (28, 20, 20), 'red': (228, 52, 44), 'green': (132, 196, 60)}
X = {'mode': 'ticks', 'values': [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8], 'side': 'above', 'min_len': 15, 'max_len': 80}
Y = {'mode': 'ticks', 'values': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], 'side': 'right', 'min_len': 15, 'max_len': 80}
SEED = (1995, 1596)


def read(image, at):
    return K.curve_panel(image, PALETTE, 'green', X, Y, at, SEED, tol=70, ink_thr=70, extra_px=4.0)
