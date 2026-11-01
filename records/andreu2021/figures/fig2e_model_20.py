"""Fig. 2e, 20% stretch (PDF p. 4): the black model line on the adhesion-length axis.

Reading by the shared code in _fig2e.py (calibration from the tick marks matched to the
printed labels; see that file's docstring for the method and intervals).
The hash pins _fig2e.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig2e.py")
SHARED_SHA256 = "f6a695efd0a107457f00e59f61fe11b88e4d621084dbb5b628c8c952e407671e"


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig2e.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("andreu2021_fig2e", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at)
