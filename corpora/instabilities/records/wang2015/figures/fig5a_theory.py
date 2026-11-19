"""Fig. 5A: the black "Theory" line (Eqs. 9-12); see _fig5.py. The legend sample
(lower right) is masked out."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    xa, ya = _f.calibrate_5a(image)
    return _f.read_black_curve(image, xa, ya, at, _f.frame(image), exclude=(1450, 850, 2410, 1600))
