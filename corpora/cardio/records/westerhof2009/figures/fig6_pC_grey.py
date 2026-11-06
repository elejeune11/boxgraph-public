"""Fig. 6, type C pressure: the grey line (taken as the pressure derived from measured flow with the three-element windkessel; see figures.md) (see _fig6.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig6", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig6.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_pressure(image, at, "C", "grey")
