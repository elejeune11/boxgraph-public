"""Fig. 5(g) (PDF p. 13): d against k = -kappa_b for w = 0.6, large-bending model (the thick blue solid line).

Reading by the shared code in _fig5g.py (calibration, colour mask, lower branch, intervals).
Curve colour (26, 26, 255), sampled from the rendered page.
"""
import importlib.util
from pathlib import Path

COLOR = (26, 26, 255)


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig5g", Path(__file__).with_name("_fig5g.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, COLOR)
