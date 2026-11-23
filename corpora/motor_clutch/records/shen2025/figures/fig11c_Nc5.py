"""Fig. 11(c) (PDF p. 11): the blue dashed line, Nc = 5.

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
ARGS = {'xlabels': [1, 1.5], 'ylabels': [0, 1, 2, 3, 4], 'color': [0, 114, 189], 'seed': [1.7, 3.6], 'tol': 60, 'min_run': 4, 'window': 110, 'x_edges': False, 'y_edges': True}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("phase_lib.py changed; update SHARED_SHA256 here after checking this reading")
    spec = importlib.util.spec_from_file_location("shen2025_phase_lib", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, **ARGS)
