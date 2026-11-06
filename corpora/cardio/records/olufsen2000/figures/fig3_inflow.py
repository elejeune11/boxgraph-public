"""Fig. 3 (PDF p. 7): measured ascending-aortic inflow q(t), solid line. Code in _common.py.
Labels matched: x ticks 3.4, 3.6, 3.8, 4, 4.2 s; y ticks 400, 300, 200, 100, 0 cm^3/s (frames unlabelled)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    cal = _c.calibrate(image, (None, None), [3.4, 3.6, 3.8, 4.0, 4.2], (None, None), [400.0, 300.0, 200.0, 100.0, 0.0])
    return _c.read_solid(cal, at)
