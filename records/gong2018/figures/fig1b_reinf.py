"""Fig. 1B (PDF p. 3): spreading speed vs stiffness, elastic substrate, red open circles
("With reinforcement").  Read by the shared code in _common.py (see its docstring):
axes from the inward tick marks matched to the printed labels below; markers by an
annulus template.  The marker at k = 0.01 is cut by the left spine and is not read.
"""
import importlib.util
from pathlib import Path

SPEC = {
    "x": {"labels": [0.01, 0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"]},
    "y": {"labels": [120, 100, 80, 60, 40, 20, 0], "edge_ticks": ["end"], "sides": "either"},
    "color": [255, 0, 0], "tol": 120, "ring": [28, 42], "score": 0.6, "pad": 40,
    # the red label "With reinforcement" inside the plot
    "exclude": [[2420, 330, 3720, 500]],
    "src_px": 8,
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
