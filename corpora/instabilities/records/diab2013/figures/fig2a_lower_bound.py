"""Fig. 2a (PDF p. 6): the chain curve, lower bound of the crease strain (FEM). See _fig2a.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("diab2013_fig2a", Path(__file__).with_name("_fig2a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curves(image, at, "chain")
