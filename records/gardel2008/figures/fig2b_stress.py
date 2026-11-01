"""Fig. 2 B (PDF p. 3): mean traction stress (green dots) against distance from the cell edge,
blebbistatin-treated cell. See _fig2b.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_fig2b", Path(__file__).with_name("_fig2b.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)


def read(image, at):
    return B.read_stress(image)
