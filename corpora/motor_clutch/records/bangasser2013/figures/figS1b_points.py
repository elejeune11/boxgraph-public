"""Fig. S1B (PDF p. 20): the green squares (Chan and Odde's measurements) with their error bars; a thick black line joins the squares.

Reading by the shared code in _panel.py (calibration from the tick marks matched to
the printed labels below; see that file's docstring for the method and intervals).
The hash pins _panel.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "5e2d57d5823de6d6e3f9a26d85c69ead8a33de9305b54a4066607a170d87ac44"

SPEC = {'color': (155, 187, 89),
 'error_bars': True,
 'kind': 'markers',
 'open': 6,
 'others': [(55, 96, 146), (80, 105, 45), (0, 0, 0), (255, 255, 255)],
 'stem_max': 12,
 'tol': 50,
 'x': {'labels': [0.1, 1, 10, 100], 'scale': 'log10'},
 'y': {'labels': [120, 110, 100, 90, 80, 70, 60]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
