"""Fig. 13(a), fourth row (PDF p. 22): the dash-dot green line labelled Peak: peak flow in the proximal aorta against the % change in large-vessel stiffness. Code in _wave.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "13q_ac", "green", half_window=60)
