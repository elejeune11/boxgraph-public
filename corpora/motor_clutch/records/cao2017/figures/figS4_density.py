"""Fig. S4 (PDF p. 11): normalized ligand density phi_i/phi_0 against ECM modulus (blue).

Reading by the shared code in _panel.py (see its docstring). The ticks point into the box; the
long ones (y = 2, 4; x = 5, 10, 15) are matched to their labels, and the frame lines stand at
x = 0 and 20 and y = 0 (the tick at y = 6 is covered by the curve). The dashed black line at
y = 1 is longer than a tick and is not taken for one. The hash pins _panel.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"

SPEC = {"kind": "curve", "color": (0, 0, 255), "others": [(0, 0, 0), (255, 255, 255)], "tol": 120,
        "ticks_in": True, "tick_max": 80, "x_spines": [0, 20], "y_spine_bottom": 0,
        "x": {"labels": [5, 10, 15]}, "y": {"labels": [4, 2]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
