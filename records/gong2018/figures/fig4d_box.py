"""Fig. 4D (PDF p. 6): measured spreading area, median with the box (0 elastic red,
1 viscoelastic blue).  Read by _fig45d.py / _boxplot.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_fig45d", Path(__file__).with_name("_fig45d.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, "4d", "box")
