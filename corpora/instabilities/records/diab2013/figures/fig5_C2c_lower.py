"""Fig. 5 (PDF p. 11): the setback-crease curve C2c, branch from T towards R. See _fig5.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("diab2013_fig5", Path(__file__).with_name("_fig5.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, "C2c_lower")
