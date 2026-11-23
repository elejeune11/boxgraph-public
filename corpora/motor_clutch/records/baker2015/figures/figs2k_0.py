"""Supp. Fig. 2k: the 0 mJ series (green diamonds). See _s2k.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_s2k", Path(__file__).with_name("_s2k.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def read(image, at):
    return S.points(image, (0, 176, 80), 45)
