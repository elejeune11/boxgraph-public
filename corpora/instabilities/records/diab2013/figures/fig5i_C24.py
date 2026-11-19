"""Fig. 5 inset (PDF p. 11): the dotted folding curve C24. See _fig5inset.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("diab2013_fig5i", Path(__file__).with_name("_fig5inset.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, "C24")
