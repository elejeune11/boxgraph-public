"""Fig. 5: round markers cut by the frame, whose kind (square or circle) cannot be told."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "fig5_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5_common.py"))
_C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_C)


def read(image, at):
    return _C.read_kind(image, "unclassified")
