"""Fig. 7, middle right: the open squares (Shoukas): normalized total systemic resistance in vagotomized animals (see _fig7.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_markers(image, "d", "open_square", "open square, at the centre of its hole")
