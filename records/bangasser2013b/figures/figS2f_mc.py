"""Fig. S2F (PDF p. 20): the grey Monte Carlo curve.

Read by the shared code in _fig.py (calibration from the tick marks matched to the
printed labels below; see that file's docstring for the method and intervals).
The hash pins _fig.py: if it changes, this reading must be re-checked.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "208eb26904aa875ef138d7d51f48841cce4eb9e0ed67f333a48281771866738e"

SPEC = {'color': (128, 128, 128),
 'others': [(255, 0, 0), (0, 255, 0), (0, 0, 255), (112, 48, 160), (20, 20, 20), (255, 255, 255)],
 'x': {'labels': [0.1, 1, 10, 100], 'scale': 'log10'},
 'y': {'labels': [100, 10, 1, 0.1, 0.01], 'scale': 'log10'}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013b_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
