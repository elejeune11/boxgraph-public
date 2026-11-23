"""Fig. 8(d) (PDF p. 10): the dark-blue curve, Nc = 20 (solid and dashed parts as one curve).

Reading code: phase_lib.py in this folder (read_curve; see its docstring for the calibration, the
reading and the interval). This file only says which panel and which line. The hash pins
phase_lib.py: if it changes, this file must change too, so a build cache keyed on this file
cannot serve a stale reading.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("phase_lib.py")
SHARED_SHA256 = "8d531308abd11445dd2ed9f4ebe46f6e33b3bc5750a2eb1aa94c3a303505f42e"
ARGS = {'xlabels': [0, 0.2, 0.4, 0.6, 0.8, 1], 'ylabels': [0, 5, 10, 15, 20, 25], 'color': [10, 10, 250], 'seed': [0.5, 13.5], 'tol': 80, 'min_run': 4, 'window': 45, 'x_edges': True, 'y_edges': True}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("phase_lib.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("shen2025_phase_lib", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, **ARGS)
