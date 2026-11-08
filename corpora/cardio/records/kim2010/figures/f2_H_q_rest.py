import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_wave  # noqa: E402

# seed: a point (x, y) on the curve meant, read by eye, only to pick the curve


def read(image, at):
    return read_wave(image, at, hlines=[400, 0, -40], xmax=1, seed=(0.65, 3.2), style='solid', label="the solid curve (Rest) of the flow rate panel titled 'H-Desc")
