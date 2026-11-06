"""Fig. 6(b) (PDF p. 8): the lower red line, time for 1 Monte Carlo run.

Read by the shared code in _fig.py (calibration from the tick marks matched to the
printed labels below; see that file's docstring for the method and intervals).
The hash pins _fig.py: if it changes, this reading must be re-checked.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "208eb26904aa875ef138d7d51f48841cce4eb9e0ed67f333a48281771866738e"

SPEC = {'color': (215, 52, 38),
 'others': [(40, 70, 165), (20, 20, 20), (255, 255, 255)],
 'pick': 'bottom',
 'x': {'labels': [1, 10, 100, 1000], 'scale': 'log10'},
 'y': {'labels': [100, 1, 0.01, 0.0001], 'scale': 'log10'}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013b_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
