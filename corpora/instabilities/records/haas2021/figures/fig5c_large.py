"""Fig. 5(c) (PDF p. 13): K_s against s, large-bending model (blue solid line, Eq. 63).

Reading by the shared code in _fig5strain.py (calibration, colour mask, intervals); y tick step
2.5, read from the printed labels. Steep jumps of the curve are left out of the positions read.
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig5strain", Path(__file__).with_name("_fig5strain.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, mod.BLUE, 2.5)
