"""Fig. 4A (PDF p. 4): effective modulus E*FA against FA band size, E_ECM = 2.5 kPa (blue).

Reading by the shared code in _panel.py (see its docstring). Legend swatches blanked.
The hash pins _panel.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"

SPEC = {"kind": "curve", "color": (0, 0, 255), "others": [(0, 255, 0), (255, 0, 0), (0, 0, 0), (255, 255, 255)],
        "tol": 120, "blank": [(1430, 450, 1640, 790)],
        "x": {"labels": [0, 2, 4, 6, 8, 10, 12]}, "y": {"labels": [12, 8, 4, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
