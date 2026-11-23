"""Fig. S9A (right) (PDF p. 20): histogram of cell orientation, MC3T3 on PDMS stretched 9% with the cells, 2 h after (patterned green).

Read by the shared code in _exp.py (read_hist): x from the bin-edge labels' centres, y from the
count labels' centres; each bin read in its central columns.
Printed labels matched: x [-90, -60, -30, 0, 30, 60, 90], y [25, 20, 15, 10, 5, 0]."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

LABELS = [25, 20, 15, 10, 5, 0]
EDGES = [-90, -60, -30, 0, 30, 60, 90]


def read(image, at):
    return E.read_hist(image, at, LABELS, EDGES)
