"""Fig. 3C (PDF p. 4): the red bars (57 kPa) of the flow-rate histogram.

Uses the reading code of fig3c_260.py (same panel, same calibration), with the
other colour. The hash pins that file: if it changes, this file must change too,
so a build cache keyed on this file cannot serve a stale reading.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("fig3c_260.py")
SHARED_SHA256 = "bfe4b44ad7286f79aa1be83f7cd0a97bbe6724ba5774855db286e04987fc0d0b"


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("fig3c_260.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("fig3c_shared", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_which(image, "red")
