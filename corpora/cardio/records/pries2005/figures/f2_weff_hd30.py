"""Fig. 2 (PDF p. 4): the short-dashed line, Weff (Eq. 11) for HD = 30%.

Read by the shared code in _kit.py (calibration from the frame's outward ticks, line ink separated by
an opening, which also removes the thinner vertical hatching, the curve traced from seed columns).
Tick labels matched: x 10, 100; y 0.0, 0.5, 1.0, 1.5, 2.0 (the long ticks). The curve is the third line in the seed columns (x = 7 and 17), as the order of the HD labels at the right and the line styles show; the peak near 10.5 um is not traced.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("pries2005_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_s)
_s.loader.exec_module(K)

SPEC = {'xlabels': [10, 100], 'ylabels': [0, 0.5, 1, 1.5, 2], 'ylog': False, 'ylong': True, 'ink': 'thick', 'w': 9.0, 'segments': [{'seed_x': 7, 'x_range': [3.3, 10.3], 'rank': 2}, {'seed_x': 17, 'x_range': [11.2, 90], 'rank': 2}]}


def read(image, at):
    return K.read_curve(image, at, SPEC)
