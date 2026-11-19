"""Fig. 5(b) (PDF p. 13): the right edge of the grey band marking the bend region s0 - w < s < s0.

Read as s at given levels of eps E_s (rows), by the shared code in _fig5strain.py.
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig5strain", Path(__file__).with_name("_fig5strain.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_band_edge(image, at, "right", 0.1)
