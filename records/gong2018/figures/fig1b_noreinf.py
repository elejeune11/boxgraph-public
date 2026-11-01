"""Fig. 1B (PDF p. 3): spreading speed vs stiffness, elastic substrate, green plus markers
("No reinforcement").  Read by the shared code in _common.py (see its docstring):
axes from the inward tick marks matched to the printed labels below; markers by a
plus-sign template (the dotted line's dots fill too little of it).  The markers at
k = 0.01 and 100 are cut by the spines and are not read.
"""
import importlib.util
from pathlib import Path

SPEC = {
    "x": {"labels": [0.01, 0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"]},
    "y": {"labels": [120, 100, 80, 60, 40, 20, 0], "edge_ticks": ["end"], "sides": "either"},
    "color": [0, 128, 0], "tol": 90, "plus": [28, 7], "score": 0.75, "pad": 40,
    # the green label "No reinforcement" inside the plot
    "exclude": [[2420, 1540, 3720, 1720]],
    "src_px": 8,
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("gong2018_common", Path(__file__).with_name("_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
