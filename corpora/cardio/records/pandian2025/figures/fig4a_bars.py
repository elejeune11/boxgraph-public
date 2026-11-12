"""Fig. 4a (p. 8): the two bars (x = 1 control, 2 IL-1beta) with their error bars. See _fig4a.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4a", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4a.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_bars(image, at)
