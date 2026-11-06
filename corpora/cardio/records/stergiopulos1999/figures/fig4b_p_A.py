"""Fig. 4B, type A: the measured aortic pressure of the type A beat.
Read by `read_thick` in _waves.py (method and intervals in its docstring). CFG holds the printed
axis labels matched to the tick marks found, the panel (from the top) and the legend box blanked."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_waves", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_waves.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

CFG = {"panel": 1, "ylabels": [120, 100, 80, 60], "yframe": True, "xlabels": [0, 0.2, 0.4, 0.6, 0.8], "xframe": False}


def read(image, at):
    return _f.read_thick(image, at, CFG)
