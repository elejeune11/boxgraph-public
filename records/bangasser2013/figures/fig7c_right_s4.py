"""Fig. 7C (PDF p. 8), right: retrograde flow rate of the catch-slip motor-clutch model, the purple line (series 4 of 6; the legend names only nm = nc = 10 and nm = nc = 300).

Reading by the shared code in _panel.py (calibration from the tick marks matched to
the printed labels below; see that file's docstring for the method and intervals).
The hash pins _panel.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "5e2d57d5823de6d6e3f9a26d85c69ead8a33de9305b54a4066607a170d87ac44"

SPEC = {'color': (110, 75, 140),
 'kind': 'curve',
 'others': [(60, 110, 170),
            (165, 60, 60),
            (136, 168, 72),
            (60, 155, 175),
            (216, 125, 45),
            (0, 0, 0),
            (255, 255, 255)],
 'tol': 50,
 'x': {'labels': [0.1, 1, 10, 100], 'scale': 'log10'},
 'y': {'labels': [120, 110, 100, 90, 80, 70, 60, 50, 40]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
