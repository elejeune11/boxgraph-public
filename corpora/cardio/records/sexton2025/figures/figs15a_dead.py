"""Fig. S15A(i) (p. 65): cell area frequency distribution, dead cells (red bars). See _figs15a.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_figs15a", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs15a.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "dead")
