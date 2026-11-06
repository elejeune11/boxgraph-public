"""Fig. 7, Aortic Des (F): the dashed line 'meas'. Code in _fig7.py.
y labels matched: frame (top, bottom) (300.0, -50.0); interior ticks [250.0, 200.0, 150.0, 100.0, 50.0, 0.0]."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_meas(image, at, (300.0, -50.0), [250.0, 200.0, 150.0, 100.0, 50.0, 0.0])
