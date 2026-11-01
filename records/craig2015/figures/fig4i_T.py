"""Fig. 4(i) (PDF p. 10): the black curve, traction (caption).

Read by _pastel.py with its neutral-dark class (the raster blurs the black line to greys); away from the
tick columns x = 2, 4, 6, whose ticks are dark too. Only the printed inner tick labels are given here.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_pastel", Path(__file__).with_name("_pastel.py"))
_pastel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pastel)


def read(image, at):
    return _pastel.read(image, at, [2, 4, 6], [0.3, 0.2, 0.1], "black")
