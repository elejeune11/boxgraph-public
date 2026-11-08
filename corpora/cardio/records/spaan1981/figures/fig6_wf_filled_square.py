"""Fig. 6: the waterfall-model line of the dog drawn as filled squares (encircled): its two calculated points."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "fig6_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig6_common.py"))
_C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_C)


def read(image, at):
    return _C.read_waterfall(image, "filled_square")
