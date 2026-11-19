"""Fig. 3b (PDF p. 7): orange open squares with error bars, MuVi SPIM, area fold change at t = -1 min
by row (plotted 0.1 left of each row's tick). Error bars: minimum and maximum over the embryos.
Calibration and marker reading in _fig3b.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _fig3b  # noqa: E402


def read(image, at):
    return _fig3b.read(image, at, _fig3b.ORANGE, [_fig3b.RED, _fig3b.BLUE], True, (0.735, 1.25))
