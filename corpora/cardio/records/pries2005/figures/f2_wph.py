"""Fig. 2 (PDF p. 4): the solid upper boundary of the vertically hatched area, Wph (Eq. 10).

Read by the shared code in _kit.py (calibration from the frame's outward ticks, line ink separated by
an opening, which also removes the thinner vertical hatching, the curve traced from seed columns).
Tick labels matched: x 10, 100; y 0.0, 0.5, 1.0, 1.5, 2.0 (the long ticks). The boundary is the sixth (lowest) line in the seed column (x = 17), below the five Weff curves.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("pries2005_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_s)
_s.loader.exec_module(K)

SPEC = {'xlabels': [10, 100], 'ylabels': [0, 0.5, 1, 1.5, 2], 'ylog': False, 'ylong': True, 'ink': 'thick', 'w': 9.0, 'segments': [{'seed_x': 17, 'x_range': [3.5, 95], 'rank': 5}]}


def read(image, at):
    return K.read_curve(image, at, SPEC)
