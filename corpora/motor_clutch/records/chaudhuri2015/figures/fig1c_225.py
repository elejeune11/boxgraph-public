"""Fig. 1c (stress-relaxing substrates), the line labelled 225 lig um^-2. The y axis is labelled in nm^2 x 10^4; values are returned in nm^2 (label value x 10^4). The five y labels are not evenly spaced; the straight-line fit through all of them carries its misfit.
Line colours sampled from the crop; the seed is a pixel on the chosen line, from which it is
traced both ways. Axis calibration: x from the centres of its printed labels [0.01, 0.1, 1, 10] (log10); y from the centres of its printed labels [0, 5000, 15000, 20000, 35000]. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

PALETTE = {'text': (36, 28, 28), 'axis': (76, 76, 76), 'l400': (28, 60, 36), 'l225': (36, 108, 52), 'l100': (52, 140, 60), 'l56': (68, 180, 84), 'l6': (116, 204, 100)}
X = {'mode': 'labels', 'values': [0.01, 0.1, 1, 10], 'log': True, 'band': 190, 'gap': 40}
Y = {'mode': 'labels', 'values': [0, 5000, 15000, 20000, 35000], 'band': 240, 'gap': 40}
SEED = (756, None)


def read(image, at):
    return K.curve_panel(image, PALETTE, 'l225', X, Y, at, SEED, tol=45)
