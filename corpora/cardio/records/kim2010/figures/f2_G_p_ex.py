import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_wave  # noqa: E402

# seed: a point (x, y) on the curve meant, read by eye, only to pick the curve


def read(image, at):
    return read_wave(image, at, hlines=[138, 68], xmax=1, seed=(0.6, 132.8), style='dashed', label='the dashed curve (Exercise, light exercise) of the pressure ', solid_seed=(0.45, 90.5))
