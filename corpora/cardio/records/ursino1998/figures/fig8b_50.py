"""Fig. 8B: the open triangles: mean arterial pressure measured by Schmidt et al. with 50 mmHg pulse amplitude (see _fig58.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig58", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig58.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_kind(image, "8b", "open")
