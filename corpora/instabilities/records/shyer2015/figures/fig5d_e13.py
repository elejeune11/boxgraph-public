"""Fig. 5D (PDF p. 7): the blue trace (E13) of anti-SHH staining intensity against distance. Read by
_fig5d_profile.py (see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5d_profile", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5d_profile.py"))
_p = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p)


def read(image, at):
    return _p.read(image, at, "blue")
