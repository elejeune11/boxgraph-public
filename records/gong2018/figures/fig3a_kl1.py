"""Fig. 3A (PDF p. 5): mean spreading speed vs tau_s/tau_b at ka + kl = 1.1 pN/nm,
yellow open squares (kl = 10^0).  Read by _fig3a.py (at each column of the marker
grid found from the blue squares, the rows the yellow square fills; see its
docstring).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_fig3a", Path(__file__).with_name("_fig3a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_yellow(image, at)
