"""Fig. 8A: the filled circles: model open-loop mean arterial pressure with 40 mmHg peak-to-peak 2-Hz pulsation (see _fig58.py)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig58", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig58.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_kind(image, "8a", "fcircle")
