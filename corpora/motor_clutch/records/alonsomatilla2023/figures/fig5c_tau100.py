"""Fig. 5(C) (PDF p. 10): the red line, tau = 100 (Eq. S55, F -> oo, K -> oo).

Read by the shared code in _fig.py (calibration from the inward tick marks matched to the
printed labels below; see that file's docstring). The hash pins _fig.py. The legend is blanked.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

SPEC = {"color": (200, 15, 15), "others": [(252, 228, 180), (12, 252, 252), (132, 180, 12), (141, 92, 130),
                                           (255, 255, 255)],
        "tol": 70, "ref_width": 1230, "left_from_top": True, "seed": (613, 492), "blank": [[730, 50, 1060, 430]],
        "x": {"labels": [0, 500, 1000, 1500, 2000], "x0_at_axis": True, "x_end_at_axis": True},
        "y": {"labels": [1, 0.8, 0.6, 0.4, 0.2, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
