"""Fig. 5A (PDF p. 5): stable FA band size against ECM modulus, n = 4 (magenta).

Reading by the shared code in _panel.py; as fig5a_n0.py. The hash pins _panel.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"

SPEC = {"kind": "curve", "color": (255, 0, 255),
        "others": [(255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0), (255, 255, 255)],
        "tol": 120, "blank": [(1180, 790, 1380, 1170)],
        "x": {"labels": [0, 5, 10, 15, 20]}, "y": {"labels": [12, 10, 8, 6, 4, 2, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
