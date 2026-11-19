"""Fig. 4C (PDF p. 6), panels 2-6: percent EdU-positive cells in fold sub-regions 1-6 (bars 1-6 from the
left). These panels draw the same six ticks as the first (Control) panel, at the same spacing, but print no
labels; the shared y label 'percent Edu+' and the labels 80, 60, 40, 20 are on the first panel only, so the
ticks are taken to stand for the same values, 100 (top) to 0 (x axis). Read by _xlbars.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_xlbars", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_xlbars.py"))
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)

LABELS = [100, 80, 60, 40, 20, 0]
ORDER = {float(i): i for i in range(1, 7)}


def read(image, at):
    return _b.read(image, at, LABELS, ORDER, expect=6)
