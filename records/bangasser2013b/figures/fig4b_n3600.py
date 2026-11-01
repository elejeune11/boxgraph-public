"""Fig. 4(b) (PDF p. 7): the dark blue (last, rightmost) curve, nm = nc = 3600 by the legend's arrow (ODE, r = 3).

Read by the shared code in _fig.py (calibration from the tick marks matched to the
printed labels below; see that file's docstring for the method and intervals).
The hash pins _fig.py: if it changes, this reading must be re-checked.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "208eb26904aa875ef138d7d51f48841cce4eb9e0ed67f333a48281771866738e"

SPEC = {'color': (40, 105, 180),
 'others': [(185, 35, 25),
            (215, 52, 38),
            (245, 180, 25),
            (230, 225, 55),
            (150, 200, 85),
            (5, 180, 85),
            (70, 165, 215),
            (20, 20, 20),
            (255, 255, 255)],
 'tol': 70,
 'x': {'labels': [0.1, 10, 1000], 'scale': 'log10'},
 'y': {'labels': [120, 100, 80, 60, 40, 20, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013b_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
