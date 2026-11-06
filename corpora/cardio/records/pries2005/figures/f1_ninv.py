"""Fig. 1 middle (PDF p. 4): number of inverted segments NINV, bars 1-4 with their standard errors.
Read by the shared code in _fig1.py. Tick labels matched: y 0, 5, 10, 15, 20."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("pries2005_fig1", Path(__file__).with_name("_fig1.py"))
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_bars(image, at, [0, 5, 10, 15, 20])
