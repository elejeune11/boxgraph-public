"""Fig. 4 (PDF p. 10): panel (d), the growth rate dA1/deps of case (i), up to its peak at eps_w. See _fig4.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("diab2013__fig4", Path(__file__).with_name("_fig4.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, "d_i")
