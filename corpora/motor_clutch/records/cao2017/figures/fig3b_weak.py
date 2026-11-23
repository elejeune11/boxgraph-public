"""Fig. 3B (PDF p. 3): DFN normalized fibre density against contraction per perimeter, the green
square markers (the network the arrow labels "Weaker Crosslinks"; the green fit line is not read).

Read by the shared code in _fig3b.py (see its docstring). The hash pins _fig3b.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig3b.py")
SHARED_SHA256 = "e532939844e25edc93cd310f885398cef0c2e0125ed287a5c84486fd50db64d8"
G, R, B, K, W = (0, 255, 0), (255, 0, 0), (0, 0, 255), (0, 0, 0), (255, 255, 255)


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig3b.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_fig3b", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, G, [R, B, K, W])
