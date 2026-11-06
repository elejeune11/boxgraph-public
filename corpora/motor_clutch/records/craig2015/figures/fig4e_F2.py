"""Fig. 4(e) (PDF p. 10): the green curve, F = 2 (legend of panel (d)).

Read by _pastel.py (hue windows for the pale raster curves; see its docstring for the method and the
intervals). Only the printed inner tick labels matched to the ticks found are given here.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_pastel", Path(__file__).with_name("_pastel.py"))
_pastel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pastel)


def read(image, at):
    return _pastel.read(image, at, [2, 4, 6], [0.08, 0.04], "green")
