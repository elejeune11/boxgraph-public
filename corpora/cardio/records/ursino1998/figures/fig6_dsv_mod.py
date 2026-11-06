"""Fig. 6, bottom: model normalized dSV/dHR, filled diamonds (see _fig6.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig6", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig6.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

LEGEND = (2950, 1700, 4375, 2300)  # crop pixels of the bottom panel's legend (mod., exp.)


def read(image, at):
    return _f.read_diamonds(image, "d", LEGEND)
