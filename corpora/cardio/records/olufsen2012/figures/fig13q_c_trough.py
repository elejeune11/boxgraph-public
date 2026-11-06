"""Fig. 13(c), fourth row (PDF p. 22): the dashed red line labelled Trough: trough flow in the main pulmonary artery against the % change in large-vessel stiffness (read right of the legend). Code in _wave.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "13q_ac", "red", half_window=60)
