"""Fig. 7H (PDF p. 7): cell spreading area of MC3T3 on PU, two bars: 1 0%, 2 9% PU deformation, 2 h after.

Read by the shared code in _exp.py (y axis from tick marks where the chart has them,
otherwise from the printed labels' centres; bars left to right, black error bars).
Printed y labels matched: [3.6, 2.7, 1.8, 0.9, 0]."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

LABELS = [3.6, 2.7, 1.8, 0.9, 0]


def read(image, at):
    return E.read_bars(image, at, LABELS, scale=1e3)
