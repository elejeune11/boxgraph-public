"""Fig. S7 (PDF p. 18): blue squares with error bars (covalently cross-linked
hyaluronic acid, elastic).  See _figs7.py and _points.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs7", Path(__file__).with_name("_figs7.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_points(image, "ha")
