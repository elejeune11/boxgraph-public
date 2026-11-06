"""Fig. 4 bottom (PDF p. 6): the long-dashed thin line, HD = 20% (glass tubes, ref. 27).

Read by the shared code in _kit.py (calibration from the frame's outward ticks, thick and thin ink
separated by an opening, the curve traced from a seed column). Tick labels matched: x 10, 100, 1000;
y 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0. The curve is the fourth thin line in the seed column (x = 10.5), as the order of the
HD labels at the right of the panel and the line styles show.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("pries2005_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_s)
_s.loader.exec_module(K)

SPEC = {'xlabels': [10, 100, 1000], 'ylabels': [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 'ylog': False, 'ink': 'thin', 'segments': [{'seed_x': 10.5, 'x_range': [3.05, 2000], 'rank': 3}]}


def read(image, at):
    return K.read_curve(image, at, SPEC)
