"""Fig. 8, row R = 22: the highest point of the flow trace (thin line) in each of the three panels (see _fig8.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig8", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig8.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_row(image, 0, "q_max")
