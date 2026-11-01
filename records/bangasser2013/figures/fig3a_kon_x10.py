"""Fig. 3A (PDF p. 5), panel kon: retrograde flow rate against substrate spring constant, kon at 10 times the base value (teal).

Reading by the shared code in _panel.py (calibration from the tick marks matched to
the printed labels below; see that file's docstring for the method and intervals).
The hash pins _panel.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "5e2d57d5823de6d6e3f9a26d85c69ead8a33de9305b54a4066607a170d87ac44"

SPEC = {'above': 10,
 'below': 30,
 'bridge': 80,
 'color': (65, 170, 200),
 'kind': 'curve',
 'others': [(72, 125, 190),
            (190, 72, 72),
            (152, 186, 85),
            (122, 95, 160),
            (0, 0, 0),
            (255, 255, 255)],
 'tol': 60,
 'x': {'labels': [0.01, 1, 100], 'scale': 'log10'},
 'x_tick_skip': 45,
 'y': {'labels': [100, 50, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
