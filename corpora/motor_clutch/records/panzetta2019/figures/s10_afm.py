"""Fig. S10 (PDF p. 21): AFM Young's modulus of cells on PDMS: 1 BALB/3T3 0%, 2 MC3T3 0%, 3 BALB/3T3 9%, 4 MC3T3 9% (by the legend: solid BALB/3T3, hatched MC3T3).

Read by the shared code in _exp.py (y axis from tick marks where the chart has them,
otherwise from the printed labels' centres; bars left to right, black error bars).
Printed y labels matched: [2500, 2000, 1500, 1000, 500, 0]."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

LABELS = [2500, 2000, 1500, 1000, 500, 0]


def read(image, at):
    return E.read_bars(image, at, LABELS)
