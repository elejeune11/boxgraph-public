"""Fig. 3(b) (PDF p. 10): beta_phis/alphabar_ss, the salmon curve.

Reading by the shared code in _fig3.py (see its docstring for the calibration, the curve mask and
the intervals). Curve colour (255, 102, 102), sampled from the rendered page; legend samples are dropped as
parts narrower than 500 columns. Tick labels matched: x [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1]; y ticks {number from the axis: label} {3: 0.2, -3: -0.2}.
"""
import importlib.util
from pathlib import Path

SPEC = {"color": (255, 102, 102), "x_labels": [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1], "y_labels": {3: 0.2, -3: -0.2}}


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig3", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
