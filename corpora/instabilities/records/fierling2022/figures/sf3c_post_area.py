"""Supp. Fig. 3c (PDF p. 25): posterior bin (light blue), apical area (dashed, the lower light-blue
line from t = 1). Reading in _sf3c.py."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _sf3c  # noqa: E402


def read(image, at):
    return _sf3c.read(image, at, "posterior", "lower")
