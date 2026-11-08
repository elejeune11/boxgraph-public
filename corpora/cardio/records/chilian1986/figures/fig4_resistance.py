"""Fig. 4, right panel (p. 7): coronary resistance bars, 1 = control (filled), 2 = papaverine (open),
with their upper SE bars. See _fig4.py for the method and intervals."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_bar(image, at, [0, 0.2, 0.4, 0.6, 0.8, 1.0])
