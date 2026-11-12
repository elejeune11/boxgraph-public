"""Fig. 4a (p. 8): every black dot (one measurement each), control (x = 1.01, 1.02, ...) and IL-1beta
(x = 2.01, ...), ordered top to bottom. See _fig4a.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4a", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4a.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_dots(image)
