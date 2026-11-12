"""Fig. 4A (PDF p. 7): every statistic of the blue Tukey box (HFrEF, n = 27):
x 1 = lower whisker end, 2 = 25th percentile, 3 = median, 4 = 75th percentile, 5 = upper whisker end.
Read by the shared code in _kit.py (boxes / read_box_stats)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_kit", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

YLABELS = [0.0, 500.0, 1000.0, 1500.0, 2000.0, 2500.0]   # y tick labels as printed


def read(image, at):
    return K.read_box_stats(image, at, 'blue', 0, YLABELS)
