"""Fig. 7, Brachialis (J): the solid line 'sim'. Code in _fig7.py.
y labels matched: frame (top, bottom) (7.0, -1.0); interior ticks [6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0]."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_sim(image, at, (7.0, -1.0), [6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0])
