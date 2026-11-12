"""Supplemental Fig. 2 (PDF p. 13): every red ring (one per patient): baseline MBV by observer 1 (y) against observer 2 (x). Read by _sfig2.py (see its docstring)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_sfig2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sfig2.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read(image, at, "red")
