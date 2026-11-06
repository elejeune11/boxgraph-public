"""Fig. 2 (bottom, p. 4): 4-el. WK: bar height with its SE bar (see _fig2.py for the method and intervals).
The bar is chosen by its position from the left, given in `at`; 7 y tick positions are expected."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_bar(image, at, 7)
