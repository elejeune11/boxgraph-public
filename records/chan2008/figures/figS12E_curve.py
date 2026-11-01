"""Fig. S12E (PDF p. 55): the red fitted Gaussian, read at the integer shifts.

Uses the reading code of figS12E_points.py (same panel, same calibration). The
hash pins that file: if it changes, this file must change too.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("figS12E_points.py")
SHARED_SHA256 = "889a89d0d39684903f0456b34f8c4fa37c83a25d566fce29162271bfd27974c4"


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("figS12E_points.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("figS12E_shared", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_which(image, "curve")
