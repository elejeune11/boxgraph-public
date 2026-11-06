"""Fig. 3A (PDF p. 5): mean spreading speed vs tau_s/tau_b at ka + kl = 1.1 pN/nm,
blue markers (kl = 10^-2; the legend shows an asterisk, the plot shows small filled
squares).  Read by _fig3a.py (filled-square template, see its docstring).  Markers
under the red circles or the yellow squares are not found.
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_fig3a", Path(__file__).with_name("_fig3a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_blue(image, at)
