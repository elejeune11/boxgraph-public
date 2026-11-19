"""Fig. 3b (PDF p. 7): blue open squares, simulations, area fold change at t = -1 min by row (on each
row's tick; no error bars). Calibration and marker reading in _fig3b.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3b  # noqa: E402


def read(image, at):
    return _fig3b.read(image, at, _fig3b.BLUE, [], False, (0.67, 1.25))
