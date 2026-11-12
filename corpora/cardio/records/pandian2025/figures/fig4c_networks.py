"""Fig. 4c (p. 8): every large black dot (one per network; x = group + 0.1 x the dot's order from the left,
group 1 control, 2 IL-1beta). Log axis. See _fig4bc.py and _cols.read_dots."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4bc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4bc.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_network_dots(image, "4c")
