"""Fig. 3(h) (PDF p. 4): Delta beta^(i) / cos Theta in units of d delta^-1 against lambda/delta,
the thick solid curve.

Calibration and reading by the shared code in _fig3.py (see its docstring). The labelled y ticks
are 0.4, 0.2 and 0 (from the top). In each column the solid curve is the thickest dark run off
the axes (the dashed line for Delta beta^(c) is thinner); reading positions avoid lambda/delta
below 1.5 (where the curve meets the dashed line), the tick labels 5 and 10 just under the axis,
and the stretches where the curve runs along the axis (y near 0).
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_fig3", Path(__file__).with_name("_fig3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _thickest(runs, cal):
    runs = [r for r in runs if r[1] - r[0] + 1 >= 0.5 * cal["lw"]]
    if not runs:
        return None
    return max(runs, key=lambda r: r[1] - r[0])


def read(image, at):
    m = _mod()
    return m.read_at(image, at, [0.4, 0.2, 0.0], _thickest, what="thick solid curve, thickest dark run in the column", below_axis=True)
