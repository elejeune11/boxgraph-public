"""Fig. 4 bottom (PDF p. 6): the short-dashed thick line, HD = 30% (present results, in vivo).

Read by the shared code in _kit.py (calibration from the frame's outward ticks, thick and thin ink
separated by an opening, the curve traced from a seed column). Tick labels matched: x 10, 100, 1000;
y 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0. The curve is the third thick line in the seed column (x = 8 and 17 and 70), as the order of the
HD labels at the right of the panel and the line styles show.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("pries2005_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_s)
_s.loader.exec_module(K)

SPEC = {'xlabels': [10, 100, 1000], 'ylabels': [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 'ylog': False, 'ink': 'thick', 'segments': [{'seed_x': 8, 'x_range': [5.5, 10.3], 'rank': 2}, {'seed_x': 17, 'x_range': [10.7, 45], 'rank': 2}, {'seed_x': 70, 'x_range': [45.01, 2000], 'rank': 2}]}


def read(image, at):
    return K.read_curve(image, at, SPEC)
