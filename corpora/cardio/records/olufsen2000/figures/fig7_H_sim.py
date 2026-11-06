"""Fig. 7, Iliac (H): the solid line 'sim'. Code in _fig7.py.
y labels matched: frame (top, bottom) (None, -20.0); interior ticks [60.0, 40.0, 20.0, 0.0]."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_sim(image, at, (None, -20.0), [60.0, 40.0, 20.0, 0.0])
