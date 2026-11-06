"""Fig. 3 (PDF p. 3): the '+' data points (Eh/r0 estimated from volume compliances). Code in _common.py.
Labels matched as in fig3_fit.py. The legend (upper right, 'fit' and '+ data') is excluded: the
right 30% of the box above 7 x 10^6."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def read(image, at):
    cal = _c.calibrate_linear(image, (0.0, 0.8), [0.2, 0.4, 0.6], (8e6, 0.0), [6e6, 4e6, 2e6])
    left, right, top = cal["left"], cal["right"], cal["top"]
    legend_bottom = int(round(top + (cal["bot"] - top) * (1 - 6.6 / 8)))
    exclude = (int(left + 0.7 * (right - left)), top, right, legend_bottom)
    return _c.read_plus_markers(cal, arm_frac=0.006, exclude=exclude)
