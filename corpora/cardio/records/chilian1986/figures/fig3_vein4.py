"""Fig. 3 (p. 6): the 4th filled marker from the top in every condition. See _fig3.py for the method and intervals."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig3.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_vessel(image, at, 'filled', {1: 4, 2: 4, 3: 4}, {})
