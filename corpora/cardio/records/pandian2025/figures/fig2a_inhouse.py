"""Fig. 2a (p. 5): the pink filled squares (the paper's in-house code), every one. See _fig2a.py.
Three squares sit on the pink fit line, which pulls a distance-transform maximum along the line by up to
about 10 px; the squares are therefore located by matching a square minus its surrounding ring
(_fig2a.square_centres), which a slide along the line penalises. Interval +/- (4 px + misfit + 2 px)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2a", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2a.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    cal = _f.calibrate(image)
    return _f.to_readings(cal, _f.square_centres(image, "pink"), 4, "pink square")
