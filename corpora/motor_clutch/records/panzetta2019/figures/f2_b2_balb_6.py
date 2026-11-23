"""Fig. 2 B.2 (top) (PDF p. 3): MSD against time lag, the purple line (6% deformation, by the legend); BALB/3T3, immediately after stretching the PDMS device with the cells.

Read by the shared code in _exp.py (log-log axes from the spine ends, checked against the tick marks;
the line traced by colour and continuity)."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

COLOR = (130, 75, 170)
OTHERS = [(15, 30, 200), (10, 100, 15), (0, 0, 0), (255, 255, 255), (150, 150, 150)]


def read(image, at):
    return E.read_msd(image, at, COLOR, OTHERS)
