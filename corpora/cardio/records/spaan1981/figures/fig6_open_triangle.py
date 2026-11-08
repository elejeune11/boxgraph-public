"""Fig. 6: the measured R_a vs R_c points drawn as open triangles (one dog), rings excluded."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "fig6_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig6_common.py"))
_C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_C)


def read(image, at):
    return _C.read_kind(image, "open_triangle")
