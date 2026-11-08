import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_wave  # noqa: E402

# seed: a point (x, y) on the curve meant, read by eye, only to pick the curve


def read(image, at):
    return read_wave(image, at, hlines=[130, 60], xmax=1, seed=(0.6, 87.6), style='dashed', label="the dashed curve (50% diameter reduction) of the panel 'Left", solid_seed=(0.6, 89.8))
