"""Fig. S7 (PDF p. 18): black right-pointing triangle with error bar (covalently
cross-linked polyacrylamide, elastic).  See _figs7.py and _points.py; the
triangle's drawn point may sit off its bounding-box centre (center_px)."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_figs7", Path(__file__).with_name("_figs7.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_points(image, "pa")
