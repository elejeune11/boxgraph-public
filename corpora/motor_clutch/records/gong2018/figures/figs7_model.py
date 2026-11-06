"""Fig. S7 (PDF p. 18): the predicted spreading speed (red line, with reinforcement)
vs stiffness of an elastic substrate, read at the reader's chosen stiffnesses.
See _figs7.py and _lines.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs7", Path(__file__).with_name("_figs7.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_line(image, at)
