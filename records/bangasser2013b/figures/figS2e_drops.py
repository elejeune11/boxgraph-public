"""Fig. S2E (PDF p. 20): the vertical segments of the r = 1 (blue), r = 2 (green) and r = 3 (red) ODE lines; x is r, y the time of the drop.

Read by the shared code in _fig.py (calibration from the tick marks matched to the
printed labels below; see that file's docstring for the method and intervals).
The hash pins _fig.py: if it changes, this reading must be re-checked.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "208eb26904aa875ef138d7d51f48841cce4eb9e0ed67f333a48281771866738e"

SPEC = {'drop_from': 0.05,
 'drop_to': 0.5,
 'kind': 'drops',
 'others': [(0, 0, 255), (0, 255, 0), (255, 0, 0), (20, 20, 20), (255, 255, 255)],
 'series': [(0, 0, 255), (0, 255, 0), (255, 0, 0)],
 'x': {'labels': [0, 20, 40, 60, 80]},
 'y': {'labels': [1, 0.8, 0.6, 0.4, 0.2, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013b_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
