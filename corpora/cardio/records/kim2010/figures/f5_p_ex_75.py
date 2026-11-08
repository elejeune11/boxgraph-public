import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_wave  # noqa: E402

# seed: a point (x, y) on the curve meant, read by eye, only to pick the curve


def read(image, at):
    return read_wave(image, at, hlines=[130, 0], xmax=0.3, seed=(0.18, 36.9), style='dotted', label="the dotted curve (75% diameter reduction) of the panel 'Left", solid_seed=(0.18, 71.8), dashed_seed=((0.09, 113.6), (0.18, 57.2)))
