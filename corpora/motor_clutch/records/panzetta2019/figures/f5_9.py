"""Fig. 5 (right) (PDF p. 6): MSD against time lag of BALB/3T3 on PDMS, the green line: 9% in a single step, acquired immediately after.

Read by the shared code in _exp.py (log-log axes from the spine ends, checked against the tick marks).
The red line (6% then 9%) is drawn over the green one and hides it over long stretches, so the
line cannot be followed by continuity: every green pixel per column is taken (trace=False), with the
legend (the lower right corner of the plot) blanked. Where red hides green over more than 40 px on
either side, the position is not read."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("panzetta2019_exp", Path(__file__).with_name("_exp.py"))
E = importlib.util.module_from_spec(_s)
_s.loader.exec_module(E)

COLOR = (10, 100, 15)
OTHERS = [(15, 30, 200), (130, 75, 170), (220, 30, 30), (0, 0, 0), (255, 255, 255), (150, 150, 150)]
LEGEND = (1760, 640, 2400, 1387)


def read(image, at):
    return E.read_msd(image, at, COLOR, OTHERS, trace=False, blank=[LEGEND])
