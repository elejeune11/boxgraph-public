"""Fig. 4 (PDF p. 3): the inflow q(t), solid line. Code in _common.py.
Labels matched: x frame 0 and 4 s, ticks 1, 2, 3; y top frame 400, ticks 300, 200, 100, 0 cm^3/s
(the bottom frame carries no label)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    cal = _c.calibrate_linear(image, (0.0, 4.0), [1.0, 2.0, 3.0], (400.0, None), [300.0, 200.0, 100.0, 0.0])
    return _c.read_solid(cal, at, half_frac=0.003)
