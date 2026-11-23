"""Supp. Fig. 2e: the 9000 mJ/cm2 example curve (red). See _s2e.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_s2e", Path(__file__).with_name("_s2e.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def read(image, at):
    return S.curve(image, at, (200, 70, 70), 50)
