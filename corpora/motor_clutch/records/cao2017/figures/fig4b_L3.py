"""Fig. 4B (PDF p. 4): normalized integrin force against normalized position, FA band size 3 um (green).

Reading by the shared code in _panel.py (see its docstring); ticks as in fig4b_L03.py.
This curve's legend swatch is blanked. The hash pins _panel.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"

SPEC = {"kind": "curve", "color": (0, 255, 0),
        "others": [(0, 0, 255), (255, 0, 0), (255, 0, 255), (0, 0, 0), (255, 255, 255)],
        "tol": 120, "blank": [(1520, 880, 1760, 960)],
        "x": {"labels": [0, 0.25, 0.5, 0.75, 1]}, "y": {"labels": [1, 0.75, 0.5, 0.25, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
