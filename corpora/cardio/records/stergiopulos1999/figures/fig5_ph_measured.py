"""Fig. 5 (p. 6), bottom: the measured phase of dog 71 (filled squares); see _fig5.py for the method and intervals.
The square on the y axis (0 Hz) is the mean term, whose phase is 0 by definition; it is not read."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return [r for r in _f.read_markers(image, at, "ph") if r["x"] > 0.25]
