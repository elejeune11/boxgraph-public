"""Fig. B5 (PDF p. 18): aortic pressure 8 cm after the aortic valve over 8 s, solid line. Code in _common.py.
Labels matched: x left frame 0, right frame 8, ticks 2, 4, 6 s; y top frame 130, bottom frame 50,
ticks 120, 110, 100, 90, 80, 70, 60 mmHg."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    cal = _c.calibrate(image, (0.0, 8.0), [2.0, 4.0, 6.0], (130.0, 50.0),
                       [120.0, 110.0, 100.0, 90.0, 80.0, 70.0, 60.0])
    return _c.read_solid(cal, at, half_frac=0.003)
