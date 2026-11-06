"""Fig. 8, L Subclavian (E). Code in _fig8.py; y top frame labelled 130 mmHg."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig8", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig8.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_panel(image, at, 130)
