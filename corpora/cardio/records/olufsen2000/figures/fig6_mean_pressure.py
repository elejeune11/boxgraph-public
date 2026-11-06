"""Fig. 6 (PDF p. 12): mean pressure along the aorta, solid line. Code in _common.py.
Labels matched: x left frame 0, ticks 10, 20, 30, 40 cm; y top frame 104.5, bottom frame 102.0,
ticks 104.0, 103.5, 103.0, 102.5 mmHg."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    cal = _c.calibrate(image, (0.0, None), [10.0, 20.0, 30.0, 40.0], (104.5, 102.0), [104.0, 103.5, 103.0, 102.5])
    return _c.read_solid(cal, at)
