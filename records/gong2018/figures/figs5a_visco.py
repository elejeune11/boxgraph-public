"""Fig. S5A (PDF p. 17): measured spreading area, viscoelastic HA (red bars,
mean +/- SD).  Read by _figs5.py / _bars.py (see their docstrings)."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs5", Path(__file__).with_name("_figs5.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, "a", "red")
