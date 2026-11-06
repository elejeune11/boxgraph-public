"""Fig. S1A (PDF p. 14): blue open squares ("KMC method"), mean spreading speed vs
stiffness of an elastic substrate.  Read by _figs1a.py (see its docstring)."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs1a", Path(__file__).with_name("_figs1a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, "kmc")
