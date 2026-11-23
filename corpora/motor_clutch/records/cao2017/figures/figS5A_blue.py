"""Fig. S5A (PDF p. 11, reprinted from ref. 24): normalized integrin force against x/L, L << 4Lc (blue).

Reading by the shared code in _panel.py; calibrated as figS5A_red.py. The blue line runs just
under the top frame and merges with it near x/L = 1, where it is not read. The hash pins _panel.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"

SPEC = {"kind": "curve", "color": (0, 0, 255), "others": [(0, 255, 0), (255, 0, 0), (0, 0, 0), (255, 255, 255)],
        "tol": 120, "ticks_in": True, "tick_max": 60, "x_spines": [0, 1], "blank": [(1140, 620, 1300, 1040)],
        "x": {"labels": [0.2, 0.4, 0.6, 0.8]}, "y": {"labels": [0.8, 0.6, 0.4, 0.2]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
