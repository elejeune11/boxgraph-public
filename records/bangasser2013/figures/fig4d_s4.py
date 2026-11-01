"""Fig. 4D (PDF p. 5): traction force against substrate spring constant, the purple line (series 4 of 4).

Reading by the shared code in _panel.py (calibration from the tick marks matched to
the printed labels below; see that file's docstring for the method and intervals).
The hash pins _panel.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "5e2d57d5823de6d6e3f9a26d85c69ead8a33de9305b54a4066607a170d87ac44"

SPEC = {'color': (125, 96, 160),
 'kind': 'curve',
 'others': [(75, 128, 190), (190, 75, 70), (152, 186, 85), (0, 0, 0), (255, 255, 255)],
 'tol': 60,
 'x': {'labels': [0.1, 1, 10, 100], 'scale': 'log10'},
 'y': {'labels': [50, 40, 30, 20, 10, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
