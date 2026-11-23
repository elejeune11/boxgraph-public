"""Fig. 13(e) (PDF p. 12): the boundary between SS (above) and S (below) (F~ = F~(w~=1), as Fig. 5(a)).

Reading code: phase_lib.py in this folder (read_boundary; see its docstring for the calibration, the
reading and the interval). This file only says which panel and which line. The hash pins
phase_lib.py: if it changes, this file must change too, so a build cache keyed on this file
cannot serve a stale reading.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("phase_lib.py")
SHARED_SHA256 = "8d531308abd11445dd2ed9f4ebe46f6e33b3bc5750a2eb1aa94c3a303505f42e"
ARGS = {'xlabels': [0, 5, 10, 15], 'ylabels': [0.2, 0.4, 0.6, 0.8], 'above': 'SS', 'below': 'S', 'pick': 'bottom', 'y_edges': False}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("phase_lib.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("shen2025_phase_lib", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_boundary(image, at, **ARGS)
