"""Fig. 13(b), 3% Sylgard (mu = 38.2 kPa): the red band of measured points. Shared code in _fig13.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("wang2014_fig13", Path(__file__).with_name("_fig13.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, "b")
