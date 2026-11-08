"""Fig. 3 (p. 6): the 4th open marker from the top when covered (exposed and oil not assignable). See _fig3.py for the method and intervals."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig3.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_vessel(image, at, 'open', {1: 4}, {})
