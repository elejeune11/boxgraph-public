"""Fig. 7B (PDF p. 8), upper histogram: blue bars, normalized frequency of clutch length; bins 20 nm wide labelled by their centres, the last one '290+'.

Reading by the shared code in _panel.py (calibration from the tick marks matched to
the printed labels below; see that file's docstring for the method and intervals).
The hash pins _panel.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "5e2d57d5823de6d6e3f9a26d85c69ead8a33de9305b54a4066607a170d87ac44"

SPEC = {'categories': [30, 50, 70, 90, 110, 130, 150, 170, 190, 210, 230, 250, 270, 290],
 'color': (8, 40, 200),
 'kind': 'bars',
 'others': [(0, 0, 0), (255, 255, 255)],
 'tol': 80,
 'y': {'labels': [0.15, 0.1, 0.05, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
