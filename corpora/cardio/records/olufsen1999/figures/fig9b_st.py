"""Fig. 9(B) (PDF p. 9): |Z(0, omega)| of the structured tree (solid line), log-log. See _fig9.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig9", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig9.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)


def read(image, at):
    # y labels matched: 10^4 at the top frame, 10^2 at the bottom frame, 10^3 the major tick between
    return _k.read_solid(image, at, True, 1e4, 1e2, 1e3)
