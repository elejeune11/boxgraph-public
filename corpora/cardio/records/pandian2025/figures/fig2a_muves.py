"""Fig. 2a (p. 5): the teal filled diamonds (mu-VES3D), every one. See _fig2a.py. Two diamonds overlap
near x = 21 um (and the pink line is drawn over them); their joint core is split at its ends, with
8 px more allowed in the interval."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2a", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2a.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    cal = _f.calibrate(image)
    return _f.to_readings(cal, _f.filled_centres(image, "teal", 18, split=20.0), 4, "teal diamond")
