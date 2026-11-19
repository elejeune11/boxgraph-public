"""Fig. 4(d) (PDF p. 4): meridional stretch f_s against s/R of the uncontracted computed shape (thick line; legend icon: the purse-string shape of Fig. 4(a)).

Reading code in _fig4.py: axes calibrated from the x axis (level with the label 1.0), the y ticks
every 0.05 (labels every 0.1) and the x ticks every pi/8 from the y axis (labels pi/2, pi);
the thick line is told apart from the other by its weight.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_fig4", Path(__file__).with_name("_fig4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _mod().read(image, at, "thick", 1.0, 0.05)
