"""Fig. 8 (PDF p. 14): simulated pressure at one site, solid line. Code in _common.py.
Labels matched in every panel: x ticks 3.4, 3.6, 3.8, 4, 4.2 s. y: top frame `ytop`, bottom frame 80 mmHg,
interior ticks every 10 mmHg between them (ytop = 130 for all panels but Brachialis (J), where it is 140)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read_panel(image, at, ytop):
    yt = [float(v) for v in range(int(ytop) - 10, 80, -10)]
    cal = _c.calibrate(image, (None, None), [3.4, 3.6, 3.8, 4.0, 4.2], (float(ytop), 80.0), yt)
    return _c.read_solid(cal, at)
