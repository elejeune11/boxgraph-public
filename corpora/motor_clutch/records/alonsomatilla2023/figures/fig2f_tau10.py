"""Fig. 2(F) (PDF p. 6): the solid green line, tau = 10 (Eq. 6 with C2 = 0.4, C3 = 0.05, F = 2).

Read by the shared code in _fig.py (calibration from the inward tick marks matched to the
printed labels below; see that file's docstring). The hash pins _fig.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

SPEC = {"color": (10, 110, 60), "others": [(10, 10, 130), (230, 15, 90), (250, 65, 15), (255, 255, 255)],
        "tol": 70, "ref_width": 1450, "seed": (640, 780), "blank": [[740, 0, 1250, 440]],
        "x": {"labels": [500, 1000, 1500]},
        "y": {"labels": [0.03, 0.02, 0.01, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
