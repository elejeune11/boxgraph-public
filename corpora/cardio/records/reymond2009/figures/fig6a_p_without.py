"""Fig. 6A (PDF p. 11), common carotid artery, pressure: the dark line ('Without cerebral arterial tree'). See _fig6.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig6", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig6.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)

LABELS = (80, 120)  # printed tick labels of the y axis: lower, upper


def read(image, at):
    return _k.read(image, at, "dark", LABELS)
