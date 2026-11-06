"""Fig. 2c, red bars (stress relaxation, ionically crosslinked): initial elastic modulus at Low,
Mid, High crosslinking (indices 1, 2, 3). y ticks every 2 kPa from 0 to 14 (labels 0, 4, 8, 12).
Bar fill colour sampled from the crop. See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILL, TOL = (204, 36, 44), 40
TICKS = [0, 2, 4, 6, 8, 10, 12, 14]


def read(image, at):
    out, _ = K.bar_series(image, FILL, TOL, TICKS, ink_thr=45)
    return out
