"""Fig. S7 (PDF p. 12): the experimental bars (solid grey or black, ref. 16) with their error bars,
x = 1 hydrogel soft, 2 hydrogel stiff, 3 fibrous soft, 4 fibrous stiff.

Read by the shared code in _s7.py (see its docstring). The hash pins _s7.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_s7.py")
SHARED_SHA256 = "b4dea2ed03c68c5e3142587b98024fb56bc28b9f80ca087dc7e800fbf797520c"


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_s7.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_s7", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, ["grey", "black"], error_bars=True)
