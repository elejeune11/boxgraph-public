"""Fig 10k (PDF p. 20): binding probability, curve 1 of the legend. See _fig10k.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_fig10k", os.path.join(os.path.dirname(__file__), "_fig10k.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_curve(image, at, 1)
