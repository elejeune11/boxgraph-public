"""Fig. S6A (PDF p. 18): yellow, initial modulus 3.4 kPa.  See _figs6a.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs6a", Path(__file__).with_name("_figs6a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, "k34")
