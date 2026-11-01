"""Supp. Fig. 1d, the line labelled nC=25 (light blue, second from the bottom). See _s1d.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_s1d", Path(__file__).with_name("_s1d.py"))
_s1d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s1d)


def read(image, at):
    return _s1d.read_curve(image, at, "25")
