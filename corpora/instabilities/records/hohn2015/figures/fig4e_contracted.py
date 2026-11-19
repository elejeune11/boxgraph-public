"""Fig. 4(e) (PDF p. 4): meridional curvature kappa_s R against s/R of the contracted computed shape (thin solid line, red over the bend region; legend icon: the mushroom shape).

Reading code in _fig4.py: axes calibrated from the x axis (level with the label 0.0), the y ticks
every 2.5 (labels every 5) and the x ticks every pi/8 from the y axis (labels pi/2, pi);
the thin line is told apart from the other by its weight.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_fig4", Path(__file__).with_name("_fig4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _mod().read(image, at, "thin", 0.0, 2.5)
