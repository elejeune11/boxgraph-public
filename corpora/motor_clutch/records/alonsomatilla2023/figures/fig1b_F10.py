"""Fig. 1(B) (PDF p. 3): the dark green line, F = 10 (mean-field model, tau = 10, omega = 2000).

Read by the shared code in _fig.py (calibration from the inward tick marks matched to the
printed labels below; log10 on x: long ticks at the labelled decades 10^-4, 10^-2, 10^0, the
right edge of the box at 10^1; see that file's docstring). The hash pins _fig.py. The legend
is blanked. The light green F = 20 line runs close to it; the colour test keeps them apart.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

OTHERS = [(156, 204, 60), (12, 12, 132), (228, 12, 84), (230, 205, 60), (255, 255, 255), (30, 30, 30)]
SPEC = {"color": (12, 60, 60), "others": OTHERS, "tol": 45, "smax": 30, "drop_markers": 1.5, "major": 0.75,
        "ref_width": 1800, "seed": (650, 560), "blank": [[1100, 80, 1690, 630]],
        "x": {"labels": [1e-4, 1e-2, 1, 10], "scale": "log10", "x0_at_axis": True, "x_end_at_axis": True},
        "y": {"labels": [1, 0.8, 0.6, 0.4, 0.2, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
