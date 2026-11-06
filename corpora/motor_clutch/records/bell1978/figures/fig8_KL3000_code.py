"""Fig. 8 (PDF p. 7 = 624): the curve labelled KL=3000 (third from the top).

Uses the reading code of fig8_KL300_code.py (same panel, same calibration, same
tracing), following curve 2 (0 = top) at f* = 2. The hash pins that file: if it
changes, this file must change too, so a build cache keyed on this file cannot serve
a stale reading.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("fig8_KL300_code.py")
SHARED_SHA256 = "d9775af4131786e51ab6f823cf01ca316487e1174c1e2ba0bd58cde5dff72f67"
WHICH = 2


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("fig8_KL300_code.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("fig8_shared", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_which(image, at, WHICH)
