"""Fig. 9(C) (PDF p. 9): phase of Z(0, omega) of the structured tree (solid line). See _fig9.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig9", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig9.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)


def read(image, at):
    # y labels matched: 90 at the top frame, -90 at the bottom frame, 0 the major tick between
    return _k.read_solid(image, at, False, 90.0, -90.0, 0.0)
