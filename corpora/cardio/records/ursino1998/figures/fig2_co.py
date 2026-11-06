"""Fig. 2, bottom: cardiac output (flow out of the left ventricle) in a basal cycle (see _fig2.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_curve(image, at, "bot")
