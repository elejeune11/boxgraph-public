"""Fig. 7, Aortic Arc (B): the solid line 'sim'. Code in _fig7.py.
y labels matched: frame (top, bottom) (350.0, None); interior ticks [300.0, 250.0, 200.0, 150.0, 100.0, 50.0, 0.0, -50.0]."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_sim(image, at, (350.0, None), [300.0, 250.0, 200.0, 150.0, 100.0, 50.0, 0.0, -50.0])
