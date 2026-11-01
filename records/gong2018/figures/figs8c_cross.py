"""Fig. S8C, right (PDF p. 19): the green crosses marking the timescales chosen for
the multiple-timescale simulation of the HA gel.  See _figs8spec.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs8spec", Path(__file__).with_name("_figs8spec.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, "c")
