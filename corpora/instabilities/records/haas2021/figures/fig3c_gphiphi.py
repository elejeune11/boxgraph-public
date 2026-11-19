"""Fig. 3(c) (PDF p. 10): gamma_phiphi/alphabar_ss, the pale green curve.

Reading by the shared code in _fig3.py (see its docstring for the calibration, the curve mask and
the intervals). Curve colour (194, 214, 153), sampled from the rendered page. The legend text
"alphabar_ss" of the second legend entry is drawn over the curve near eta = 0.8 and cuts off its
right end (eta > 0.82, about 330 columns), so parts narrower than 300 columns are dropped here
(the legend sample is about 265 columns long). Tick labels matched: x [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1]; y ticks {number from the axis: label} {2: 0.02, 4: 0.04, 6: 0.06, 8: 0.08}.
"""
import importlib.util
from pathlib import Path

SPEC = {"color": (194, 214, 153), "x_labels": [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1], "y_labels": {2: 0.02, 4: 0.04, 6: 0.06, 8: 0.08}, "min_width": 300}


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig3", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
