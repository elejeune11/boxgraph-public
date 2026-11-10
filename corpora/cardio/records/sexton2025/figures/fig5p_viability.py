"""Fig. 5P(iii), right (p. 6): viability [%] in the core region, bar 1 Perfused, bar 2 Media Ctrl, with SD
error bars. See _fig5p.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5p", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5p.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_bars(image, at, [80, 60, 40, 20, 0])
