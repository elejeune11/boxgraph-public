"""Fig. 7, L Carotid (D): the solid line 'sim'. Code in _fig7.py.
y labels matched: frame (top, bottom) (35.0, 0.0); interior ticks [30.0, 25.0, 20.0, 15.0, 10.0, 5.0]."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_sim(image, at, (35.0, 0.0), [30.0, 25.0, 20.0, 15.0, 10.0, 5.0])
