"""Fig. 5B (PDF p. 10), top sub-panel: the thick line (the volunteers' averaged waveform). See _wave.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_wave", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wave.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

LABELS = (80, 120)  # printed tick labels of this sub-panel's y axis: lower, upper


def read(image, at):
    return _k.read(image, at, 0, LABELS)
