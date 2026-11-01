"""Fig. 4d, yellow bars: YAP in the nucleus (normalized), Elastic (1) and Stress relax (2).
Fill colour sampled from the crop; y tick values listed bottom to top (labelled or not).
See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILL, TOL = (252, 212, 100), 40
TICKS = [0, 1, 2, 3, 4]


def read(image, at):
    out, _ = K.bar_series(image, FILL, TOL, TICKS, ink_thr=60)
    return out
