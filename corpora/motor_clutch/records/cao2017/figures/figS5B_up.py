"""Fig. S5B (PDF p. 11): normalized displacement of the FA plaque u_p against x/Lc, FA of size 16 Lc (blue).

Reading by the shared code in _panel.py (see its docstring). Ticks point into the box; the
frame lines stand at x = 0, 16 and y = 0. Legend swatches blanked. Where the red u_s curve is
drawn over this one (about x/Lc = 1.5 to 11.5) the blue curve is not read. The hash pins _panel.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"

SPEC = {"kind": "curve", "color": (0, 0, 255), "others": [(255, 0, 0), (0, 0, 0), (255, 255, 255)], "tol": 120,
        "ticks_in": True, "tick_max": 80, "x_spines": [0, 16], "y_spine_bottom": 0,
        "blank": [(1090, 520, 1380, 770)],
        "x": {"labels": [4, 8, 12]}, "y": {"labels": [0.8, 0.6, 0.4, 0.2]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
