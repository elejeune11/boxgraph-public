"""Fig. 3b, grey bars (elastic): cell-spreading area at initial moduli 1.4, 3.4, 9 kPa (indices 1-3).
Fill colour sampled from the crop; y tick values listed bottom to top (labelled or not).
See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILL, TOL = (60, 60, 68), 14
TICKS = [0, 500, 1000, 1500, 2000]


def read(image, at):
    out, _ = K.bar_series(image, FILL, TOL, TICKS, ink_thr=47)
    return out
