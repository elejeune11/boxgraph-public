"""Fig 11k (PDF p. 21): substrate stiffness, line 4 of the legend. See _fig11k.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_fig11k", os.path.join(os.path.dirname(__file__), "_fig11k.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_curve(image, at, 4)
