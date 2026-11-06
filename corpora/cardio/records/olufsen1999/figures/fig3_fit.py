"""Fig. 3 (PDF p. 3): the solid 'fit' line of Eq. 6, Eh/r0 against r0. Code in _common.py.
Labels matched: x frame 0 and 0.8 cm, ticks 0.2, 0.4, 0.6; y frame 8 (top) and 0 (bottom) x 10^6,
ticks 6, 4, 2 x 10^6 g/s^2/cm."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    cal = _c.calibrate_linear(image, (0.0, 0.8), [0.2, 0.4, 0.6], (8e6, 0.0), [6e6, 4e6, 2e6])
    return _c.read_solid(cal, at, half_frac=0.012)
