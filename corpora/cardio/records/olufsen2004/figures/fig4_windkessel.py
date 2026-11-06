"""Fig. 4 (PDF p. 14): the dashed curve (windkessel), the lower black curve after t = 0. See _fig4.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_curve(image, at, "lower", dashed=True)
