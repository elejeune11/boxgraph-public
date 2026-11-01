"""Fig. 3A (PDF p. 5): mean spreading speed vs tau_s/tau_b at ka + kl = 1.1 pN/nm,
red open circles (kl = 10^-1).  Read by _fig3a.py (annulus template, one ring per
grid column, see its docstring).  Rings mostly hidden by other markers are not found.
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_fig3a", Path(__file__).with_name("_fig3a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_red(image, at)
