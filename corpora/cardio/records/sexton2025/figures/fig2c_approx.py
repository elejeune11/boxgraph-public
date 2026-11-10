"""Fig. 2C (p. 3): median alignment of the prior approximation (red line). See _fig2c.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2c", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2c.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "approx")
