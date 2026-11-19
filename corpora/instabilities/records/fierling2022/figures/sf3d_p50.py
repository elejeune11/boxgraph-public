"""Supp. Fig. 3d (PDF p. 25): the line x = 50 um (yellow). Calibration and colours in _sf3d.py."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _sf3d  # noqa: E402


def read(image, at):
    return _sf3d.read(image, at, "50")
