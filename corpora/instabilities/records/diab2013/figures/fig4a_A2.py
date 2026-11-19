"""Fig. 4 (PDF p. 10): panel (a), kbar = 0.628, the dashed line A2 after its rise. See _fig4.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("diab2013__fig4", Path(__file__).with_name("_fig4.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, "a_A2")
