"""Fig. 4 top (PDF p. 6): the solid thick line, HD = 45% (present results, in vivo).

Read by the shared code in _kit.py (calibration from the frame's outward ticks, thick and thin ink
separated by an opening, the curve traced from a seed column). Tick labels matched: x 10, 100, 1000;
y 1, 1.5, 2, 3, 4, 5, 6, 8, 10. The curve is the second thick line in the seed column (x = 3.15 and 12), as the order of the
HD labels at the right of the panel and the line styles show.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("pries2005_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_s)
_s.loader.exec_module(K)

SPEC = {'xlabels': [10, 100, 1000], 'ylabels': [1, 1.5, 2, 3, 4, 5, 6, 8, 10], 'ylog': True, 'ink': 'thick', 'segments': [{'seed_x': 3.15, 'x_range': [3.05, 10.2], 'rank': 1}, {'seed_x': 12, 'x_range': [10.8, 2000], 'rank': 1}]}


def read(image, at):
    return K.read_curve(image, at, SPEC)
