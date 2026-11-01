"""Fig. 6E (PDF p. 7): the purple line (Traction force), right axis.

Reading by the shared code in _panel.py (calibration from the tick marks matched to
the printed labels below; see that file's docstring for the method and intervals).
The hash pins _panel.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "5e2d57d5823de6d6e3f9a26d85c69ead8a33de9305b54a4066607a170d87ac44"

SPEC = {'blank': [[2700, 1530, 3520, 1720]],
 'color': (125, 96, 160),
 'kind': 'curve',
 'others': [(72, 125, 190),
            (248, 168, 136),
            (248, 200, 184),
            (248, 184, 168),
            (248, 184, 152),
            (248, 216, 200),
            (152, 72, 8),
            (0, 0, 0),
            (255, 255, 255)],
 'tol': 60,
 'x': {'labels': [0.01, 0.1, 1, 10, 100], 'scale': 'log10'},
 'y': {'labels': [45, 40, 35, 30, 25, 20, 15, 10, 5, 0], 'side': 'right'}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
