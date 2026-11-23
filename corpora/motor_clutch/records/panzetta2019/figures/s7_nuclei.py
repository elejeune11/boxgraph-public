"""Fig. S7 (right) (PDF p. 18): nuclei area of MC3T3 on PDMS: 1 0%, 2 9% (on deformed devices), 3 9% (2 h after deformation, hatched).

Read by the shared code in _exp.py (y axis from tick marks where the chart has them,
otherwise from the printed labels' centres; bars left to right, black error bars).
Printed y labels matched: [350, 300, 250, 200, 150, 100, 50, 0]."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

LABELS = [350, 300, 250, 200, 150, 100, 50, 0]


def read(image, at):
    return E.read_bars(image, at, LABELS)
