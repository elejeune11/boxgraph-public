"""Fig. 6 (PDF p. 12): the coarse-dotted line, kbar = 0.100. See _fig6.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("diab2013_fig6", Path(__file__).with_name("_fig6.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, "k0100")
