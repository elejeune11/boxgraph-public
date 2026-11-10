"""Fig. 1G(i) (p. 2): lattice (blue) moving average of <C_tissue>/C_inlet, convex cube. See _fig1g.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig1g", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig1g.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "lat_i")
