"""Fig. 1A (PDF p. 2): the blue (U87 glioma cells, ref. 4) points with their error bars.

Reading by the shared code in _panel.py (calibration from the tick marks matched to
the printed labels below; see that file's docstring for the method and intervals).
The hash pins _panel.py: if it changes, this file must be re-checked and updated.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_panel.py")
SHARED_SHA256 = "5e2d57d5823de6d6e3f9a26d85c69ead8a33de9305b54a4066607a170d87ac44"

SPEC = {'above': 0,
 'bar_gap': 45,
 'bar_smax': 70,
 'color': (64, 105, 155),
 'error_bars': True,
 'kind': 'markers',
 'open': 9,
 'others': [(159, 65, 62), (127, 155, 72), (104, 82, 133), (0, 0, 0), (255, 255, 255)],
 'stem_max': 36,
 'tol': 45,
 'x': {'labels': [0.01, 1, 100, 10000], 'scale': 'log10'},
 'y': {'labels': [1.4, 1.2, 1, 0.8, 0.6, 0.4, 0.2, 0]}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_panel.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2013_panel", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
