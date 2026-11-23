"""Fig. 5 (right) (PDF p. 6): MSD against time lag of BALB/3T3 on PDMS, the red line: 6% then 9% (two steps), acquired 4 h after the first.

Read by the shared code in _exp.py (log-log axes from the spine ends, checked against the tick marks;
the line traced by colour and continuity)."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

COLOR = (220, 30, 30)
OTHERS = [(15, 30, 200), (130, 75, 170), (10, 100, 15), (0, 0, 0), (255, 255, 255), (150, 150, 150)]


def read(image, at):
    return E.read_msd(image, at, COLOR, OTHERS)
