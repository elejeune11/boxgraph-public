import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fig6 import read_series  # noqa: E402


def read(image, at):
    return read_series(image, at, "circle", False, "Rest (open circles)")
