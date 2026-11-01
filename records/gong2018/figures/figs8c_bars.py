"""Fig. S8C, left (PDF p. 19): spreading velocity for the HA substrate of Fig. 5
(elastic, effective timescale, multiple timescales).  See _figs8bc.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs8bc", Path(__file__).with_name("_figs8bc.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at)
