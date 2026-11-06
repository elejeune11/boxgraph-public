"""Fig. 5-6(b) (p. 11): Qco, the fine dotted line, read at the tops of its two short spikes above
the Qct curve (near 36.02 s and 36.35 s), where it is the highest ink of the plot; see _common.py.
Labels as in fig5_6b_qci.py; the legend (top right) is left out. A narrow window (6 px) keeps the
read on the spike itself."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)

LEGEND = (1990, 60, 2720, 600)


def read(image, at):
    return _c.read_outermost(image, at, [-600, -400, -200, 0, 200, 400, 600, 800, 1000], [36, 36.5, 37],
                             -800, None, top=True, legend_box=LEGEND, window=6)
