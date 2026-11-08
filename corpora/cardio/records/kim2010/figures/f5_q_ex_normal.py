import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_wave  # noqa: E402

# seed: a point (x, y) on the curve meant, read by eye, only to pick the curve


def read(image, at):
    return read_wave(image, at, hlines=[11, 0], xmax=0.3, seed=(0.195, 9.89), style='solid', label="the solid curve (Normal) of the panel 'Left anterior descend")
