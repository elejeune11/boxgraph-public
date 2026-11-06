"""Fig. 4B (PDF p. 6): measured relaxation stiffness of the elastic PA gel (blue
dots).  Read by _fig45b.py (see its docstring)."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_fig45b", Path(__file__).with_name("_fig45b.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_main(image, at, "4b", "blue")
