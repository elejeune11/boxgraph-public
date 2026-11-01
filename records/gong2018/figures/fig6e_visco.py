"""Fig. 6E (PDF p. 8): model-predicted spreading area, viscoelastic substrates
(dark red bars).  Read by _fig6.py / _bars.py (see their docstrings)."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_fig6", Path(__file__).with_name("_fig6.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, "e", "red_e")
