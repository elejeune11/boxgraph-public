"""Fig. 1 top (PDF p. 4): velocity error VERR, bars 1-4 with their standard errors.
Read by the shared code in _fig1.py. Tick labels matched: y 0.6, 0.7, 0.8."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("pries2005_fig1", Path(__file__).with_name("_fig1.py"))
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_bars(image, at, [0.6, 0.7, 0.8])
