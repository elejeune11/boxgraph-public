"""Fig. 4D (PDF p. 5): the red bars (REF Bead RMS) of the displacement histogram.

Uses the reading code of fig4d_strain.py (same panel, same calibration), with
the other colour. The hash pins that file: if it changes, this file must change
too, so a build cache keyed on this file cannot serve a stale reading.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("fig4d_strain.py")
SHARED_SHA256 = "519b69a0aee40c81771588af915200aba8b4fc9a7aa730b6e73d5170ad1fe9fd"


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("fig4d_strain.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("fig4d_shared", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_which(image, "red")
