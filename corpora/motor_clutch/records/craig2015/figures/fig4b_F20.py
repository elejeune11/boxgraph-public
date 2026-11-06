"""Fig. 4(b) (PDF p. 10): the magenta curve, F = 20 (legend of panel (a)).

Read by _pastel.py (hue windows for the pale raster curves; see its docstring for the method and the
intervals). Only the printed inner tick labels matched to the ticks found are given here.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_pastel", Path(__file__).with_name("_pastel.py"))
_pastel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pastel)


def read(image, at):
    return _pastel.read(image, at, [2, 4, 6], [0.8, 0.6, 0.4, 0.2], "magenta")
