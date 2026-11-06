"""Fig. S8C (PDF p. 51): the magenta bars (GFP-Actin Transfected) with their error bars.

Uses the reading code of figS8C_control.py (same panel, same calibration), with
the other colour. The hash pins that file: if it changes, this file must change
too, so a build cache keyed on this file cannot serve a stale reading.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("figS8C_control.py")
SHARED_SHA256 = "76a0979e1b6d84d88899b8aa7d0360f3da507cca9476e39abd3279924f1ab016"


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("figS8C_control.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("figS8C_shared", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_which(image, "gfp")
