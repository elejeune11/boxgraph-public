"""Fig. 6I (PDF p. 6): nucleus area of BALB/3T3 on PDMS, three bars: 1 0%, 2 6%, 3 9% PDMS deformation, 2 h after.

Read by the shared code in _exp.py (y axis from tick marks where the chart has them,
otherwise from the printed labels' centres; bars left to right, black error bars).
Printed y labels matched: [320, 240, 160, 80, 0]."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

LABELS = [320, 240, 160, 80, 0]


def read(image, at):
    return E.read_bars(image, at, LABELS)
