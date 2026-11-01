"""Fig. 4b, green bars: cell spread area on stress-relaxing gels, Control, b1-blocking ab, Blebbistatin, ML-7, Y27632, Cytochalasin (indices 1-6).
Fill colour sampled from the crop; y tick values listed bottom to top (labelled or not).
See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILL, TOL = (124, 212, 148), 40
TICKS = [0, 200, 400, 600, 800, 1000, 1200, 1400]


def read(image, at):
    out, _ = K.bar_series(image, FILL, TOL, TICKS, ink_thr=60)
    return out
