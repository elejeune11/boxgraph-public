"""Fig. 5 (PDF p. 10): the blue diamond markers (Huang et al. 1996, larger radii), with their error
bars where a cap shows outside the marker. Code in _fig5.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.markers(image, "blue")
