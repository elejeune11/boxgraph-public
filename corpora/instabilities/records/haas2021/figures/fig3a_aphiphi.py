"""Fig. 3(a) (PDF p. 10): alpha_phiphi/alphabar_ss, the light blue curve.

Reading by the shared code in _fig3.py (see its docstring for the calibration, the curve mask and
the intervals). Curve colour (179, 179, 255), sampled from the rendered page; legend samples are dropped as
parts narrower than 500 columns. Tick labels matched: x [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1]; y ticks {number from the axis: label} {5: 0.5, 10: 1}.
"""
import importlib.util
from pathlib import Path

SPEC = {"color": (179, 179, 255), "x_labels": [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1], "y_labels": {5: 0.5, 10: 1}}


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig3", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
