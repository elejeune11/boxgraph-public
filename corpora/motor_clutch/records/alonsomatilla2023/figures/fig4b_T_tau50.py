"""Fig. 4(B), left (PDF p. 9): the green solid line, tau = 50 (omega = 1000, K -> oo; Eqs. S31-S36).

Read by the shared code in _fig.py (calibration from the inward tick marks matched to the
printed labels below; see that file's docstring). The hash pins _fig.py. Symbols of the same
colour on the line are left out and bridged; the dashed low-F asymptote of the same colour
lies off the read positions.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

OTHERS = [(204, 36, 108), (252, 252, 132), (108, 132, 60), (12, 60, 132), (128, 128, 128), (255, 255, 255),
          (30, 30, 30)]
COLOR = (108, 132, 60)
SPEC = {"color": COLOR, "others": [o for o in OTHERS if o != COLOR], "tol": 50, "smax": 40,
        "drop_markers": 1.5, "ref_width": 1105, "seed": (872, 311), "left_from_top": True,
        "x": {"labels": [0, 1, 2, 3, 4], "x0_at_axis": True, "x_end_at_axis": True},
        "y": {"labels": [1.5, 1, 0.5, 0], "y0_at_axis": True}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
