"""Fig. 3A (left) (PDF p. 4): MSD at 1 s of BALB/3T3 on PDMS, seven bars: 1 0%; 2-4 6% (on stretched devices, post stretching, 2 h after stretching); 5-7 9% (the same three).

Read by the shared code in _exp.py (y axis from tick marks where the chart has them,
otherwise from the printed labels' centres; bars left to right, black error bars).
Printed y labels matched: [8, 6, 4, 2, 0]."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

LABELS = [8, 6, 4, 2, 0]


def read(image, at):
    return E.read_bars(image, at, LABELS, scale=1e-4)
