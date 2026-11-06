"""Fig. 5 (p. 6), top: the modulus of the dotted line (three-element WK in the legend); see _fig5.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_dotted(image, at, "mod")
