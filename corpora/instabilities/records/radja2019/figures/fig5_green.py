# Fig. 5: every green state dot on the tree, by angular position (see _fig5.py).
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5", os.path.join(os.path.dirname(__file__), "_fig5.py"))
_fig5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fig5)


def read(image, at):
    return _fig5.read_colour(image, "green")
