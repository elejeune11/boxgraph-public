"""Fig. 7, top right: the diamonds: extrasplanchnic volume shift measured by Brunner et al., mean and SD (three diamonds at one pressure) (see _fig7.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_brunner(image, "b")
