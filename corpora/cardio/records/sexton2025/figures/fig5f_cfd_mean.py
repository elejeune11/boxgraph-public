"""Fig. 5F (p. 6): the averaged CFD flow ratio (grey dashed line), read at each branch column. See _fig5f.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5f", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5f.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_dashed(image, at)
