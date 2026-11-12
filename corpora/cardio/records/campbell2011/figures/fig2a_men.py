"""Fig. 2 A (PDF p. 5): cardiomyocyte width (um) against BSA (m2), per patient; the men (open circles).
The axis labels below are the printed tick labels, lowest first. See _fig2.py for the method.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("campbell_fig2", Path(__file__).with_name("_fig2.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)

Y_LABELS = [16, 20, 24, 28, 32, 36]
X_LABELS = [1.5, 1.7, 1.9, 2.1, 2.3, 2.5]


def read(image, at):
    return F.read_group(image, Y_LABELS, X_LABELS, "open")
