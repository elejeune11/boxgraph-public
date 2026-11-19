"""Fig. 3(g) (PDF p. 4): k / (d^1/2 delta^-3/2 sin^1/2 Theta) against lambda/delta, the solid curve.

Calibration and reading by the shared code in _fig3.py (see its docstring). The labelled y ticks
are 4 and 3 (from the top). In each column the curve is the longest dark run off the axes; the
reading positions avoid the dashed vertical line at lambda/delta = 2.44.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_fig3", Path(__file__).with_name("_fig3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _longest(runs, cal):
    runs = [r for r in runs if r[1] - r[0] + 1 >= 0.5 * cal["lw"]]
    if not runs:
        return None
    return max(runs, key=lambda r: r[1] - r[0])


def read(image, at):
    m = _mod()
    return m.read_at(image, at, [4.0, 3.0], _longest, what="solid curve, longest dark run in the column")
