"""Fig. 2F (p. 3): partial implicit volume point-enclosure time (blue line). See _fig2f.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2f", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2f.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "piv")
