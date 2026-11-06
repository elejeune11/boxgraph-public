"""Fig. 4 C, right panel (PDF p. 5): mean traction stress against F-actin speed, CA-RAC, blue triangles.

Matched labels: x 0, 5, ..., 35 on the long ticks and frame edges where on the grid, short ticks halfway; y 20, 40, ..., 120 on the long ticks (0 at the bottom frame edge),
short ticks halfway. See _fig4c.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_fig4c", Path(__file__).with_name("_fig4c.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    return C.read_colour(image, "blue", (0.0, 35.0), 5.0, (0.0, (None, 1)), 20.0, "CA-RAC, blue triangles marker")
