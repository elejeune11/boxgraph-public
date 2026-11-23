"""Fig. S6 (PDF p. 17): MSD against time lag of BALB/3T3 on PDMS, the blue line: 0%.

Read by the shared code in _exp.py (log-log axes from the spine ends, checked against the tick marks;
the line traced by colour and continuity)."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

COLOR = (15, 30, 200)
OTHERS = [(245, 175, 20), (220, 30, 30), (0, 0, 0), (255, 255, 255), (150, 150, 150)]


def read(image, at):
    return E.read_msd(image, at, COLOR, OTHERS)
