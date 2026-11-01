"""Fig. 2(d) left (PDF p. 4): paxillin intensity / maximum, 16 black bars of 0.5 um bins.

Read by _blackbars.py (see its docstring for the method and the intervals).
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_blackbars", Path(__file__).with_name("_blackbars.py"))
_bb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bb)


def read(image, at):
    return _bb.read(image, at)
