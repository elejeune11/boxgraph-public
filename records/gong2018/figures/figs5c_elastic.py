"""Fig. S5C (PDF p. 17): model-predicted spreading area, elastic HA (grey bars).
Read by _figs5.py / _bars.py (see their docstrings)."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs5", Path(__file__).with_name("_figs5.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, "c", "grey_c")
