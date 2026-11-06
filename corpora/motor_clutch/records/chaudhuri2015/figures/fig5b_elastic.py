"""Fig. 5b, the line Elastic (the grey horizontal line): average lead node spacing against substrate stiffness.
Line colours sampled from the crop; the seed is a pixel on the chosen line, from which it is
traced both ways. Axis calibration: x from the centres of its printed labels [0.01, 0.1, 1, 10] (log10); y from the centres of its printed labels [0, 5, 10, 15, 20]. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

PALETTE = {'text': (12, 12, 12), 'elastic': (100, 100, 100), 'e12': (132, 164, 204), 'e5_13': (92, 140, 188), 'e13': (36, 60, 92)}
X = {'mode': 'labels', 'values': [0.01, 0.1, 1, 10], 'log': True, 'band': 200, 'gap': 40, 'skip': [0]}
Y = {'mode': 'labels', 'values': [0, 5, 10, 15, 20], 'band': 200, 'gap': 30}
SEED = (910, None)


def read(image, at):
    return K.curve_panel(image, PALETTE, 'elastic', X, Y, at, SEED, tol=40)
