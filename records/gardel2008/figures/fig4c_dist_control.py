"""Fig. 4 C, left panel (PDF p. 5): mean traction stress against cell edge distance, CONTROL, red diamonds.

Matched labels: x 10, 8, ..., 2, 0 on the long ticks (12 at the left frame edge), short ticks halfway; y 20, 40, ..., 120 on the long ticks (0 at the bottom frame edge),
short ticks halfway. See _fig4c.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_fig4c", Path(__file__).with_name("_fig4c.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    return C.read_colour(image, "red", (12.0, 0.0), 2.0, (0.0, (None, 1)), 20.0, "CONTROL, red diamonds marker")
