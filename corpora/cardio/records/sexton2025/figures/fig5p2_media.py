"""Fig. 5P(ii) (p. 6): radial profile of average viable cell count, media control (panel 2). See _fig5p2.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5p2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5p2.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, 2)
