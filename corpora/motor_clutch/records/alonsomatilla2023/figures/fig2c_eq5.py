"""Fig. 2(C) (PDF p. 6): the dark-blue dashed line, Eq. 5 (critical activity on soft substrates).

Read by the shared code in _fig.py (calibration from the inward tick marks matched to the
printed labels below; x: the tick at 5, the left axis at 0 and the right line of the box at
10; y: ticks at 0.2, 0.4, 0.6, the bottom axis at 0 and the top line at 0.8). The hash pins
_fig.py. The legend is blanked. The symbols sit on the line at tau = 1, 2, ..., 10, so it is
read half-way between them; the dashes' gaps are bridged.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

OTHERS = [(200, 0, 0), (80, 20, 245), (140, 187, 140), (255, 255, 255), (30, 30, 30)]
SPEC = {"color": (5, 45, 95), "others": OTHERS, "tol": 60, "smax": 40,
        "ref_width": 2603, "seed": (1041, 1334), "blank": [[680, 190, 1370, 640]], "gap": 90,
        "x": {"labels": [0, 5, 10], "x0_at_axis": True, "x_end_at_axis": True},
        "y": {"labels": [0.8, 0.6, 0.4, 0.2, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
