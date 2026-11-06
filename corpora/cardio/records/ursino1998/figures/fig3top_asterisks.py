"""Fig. 3, top: the asterisks (Chapleau and Abboud, 30-50 mmHg peak-to-peak pulsation) (see _fig3top.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig3top", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig3top.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_points(image, "stars")
