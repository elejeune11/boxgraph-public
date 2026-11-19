"""Fig. 3(h) (PDF p. 4): Delta beta^(c) in units of d delta^-1 against lambda/delta, the dashed line.

Calibration by the shared code in _fig3.py (see its docstring); labelled y ticks 0.4, 0.2, 0.
The dashed line is the topmost dark run in a column, read where the solid curve is far below it
(lambda/delta from 4 to 8). Columns within +-2 dash periods are pooled so that gaps between the
dashes are bridged; columns falling in a gap give no run and are skipped.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_fig3", Path(__file__).with_name("_fig3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _top(runs, cal):
    runs = [r for r in runs if r[1] - r[0] + 1 >= 0.3 * cal["lw"]]
    if not runs:
        return None
    return min(runs, key=lambda r: r[0])


def read(image, at):
    m = _mod()
    return m.read_at(image, at, [0.4, 0.2, 0.0], _top, what="dashed line, topmost dark run", half=40, below_axis=True)
