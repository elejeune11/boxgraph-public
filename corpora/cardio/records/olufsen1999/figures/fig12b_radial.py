"""Fig. 12(B) (PDF p. 11): the 'Radial' curve (measured, ref. 41) at its peak. See _fig12.py.

Labels matched as in fig12b_0cm.py. Around its peak (t 0.17-0.22 s) the radial curve is far above
all other curves, so it is the uppermost dark run (read over a few columns to bridge its gaps).
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig12", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig12.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    cal = _f.calibrate(image, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], slice(None),
                       [80.0, 100.0, 120.0, 140.0], slice(0, None, 2))
    return _f.read_top(cal, at, None)  # from the top of the crop
