"""Fig. 1b (elastic substrates), the line labelled 56 lig um^-2. The y axis is labelled in nm^2 x 10^4; values are returned in nm^2 (label value x 10^4).
Line colours sampled from the crop; the seed is a pixel on the chosen line, from which it is
traced both ways. Axis calibration: x from the centres of its printed labels [0.01, 0.1, 1, 10] (log10); y from the centres of its printed labels [0, 50000]. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

PALETTE = {'text': (40, 24, 24), 'axis': (72, 72, 72), 'l400': (184, 24, 40), 'l225': (232, 56, 40), 'l56': (248, 120, 72), 'l6': (248, 184, 104)}
X = {'mode': 'labels', 'values': [0.01, 0.1, 1, 10], 'log': True, 'band': 200, 'gap': 40}
Y = {'mode': 'labels', 'values': [0, 50000], 'band': 230, 'gap': 40}
SEED = (1400, None)


def read(image, at):
    return K.curve_panel(image, PALETTE, 'l56', X, Y, at, SEED, tol=70)
