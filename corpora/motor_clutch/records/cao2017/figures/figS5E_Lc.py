"""Fig. S5E (PDF p. 11): shear lag length Lc against ligand density (blue).

Reading by the shared code in _panel.py (see its docstring). Ticks point into the box; the
frame lines stand at x = 0, 100 and y = 0. The hash pins _panel.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"

SPEC = {"kind": "curve", "color": (0, 0, 255), "others": [(0, 0, 0), (255, 255, 255)], "tol": 120,
        "ticks_in": True, "tick_max": 80, "x_spines": [0, 100], "y_spine_bottom": 0,
        "x": {"labels": [20, 40, 60, 80]}, "y": {"labels": [0.4, 0.3, 0.2, 0.1]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
