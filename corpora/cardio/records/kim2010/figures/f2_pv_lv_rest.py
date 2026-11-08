import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_wave  # noqa: E402

# seed: a point (x, y) on the curve meant, read by eye, only to pick the curve


def read(image, at):
    return read_wave(image, at, hlines=[150, 0], xmax=150, seed=(90, 125.3), style='solid', label='the upper (ejection) branch of the left ventricle loop, soli')
