"""Fig. 5B (PDF p. 10), bottom sub-panel: the 1-D model's waveform (thick line). See _wave.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

LABELS = (80, 120)  # printed tick labels of this sub-panel's y axis: lower, upper


def read(image, at):
    return _k.read(image, at, 1, LABELS)
