"""Shared stub body for Fig. S1(B) (PDF p. 23): the fraction of bound clutches against K
(log10 axis) for F = 0.25 (dark blue) and F = 0.5 (crimson), tau = 10, omega = 2000.
Read by _fig.py: x from the long ticks at 10^-2 and 10^0 with the left line of the box at
10^-4 and the right line at 10^1; y from the ticks at 0.2-0.6 with the bottom line at 0 and
the top line at 1. Symbols of the same colour on the lines are left out and bridged.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

COLOURS = {"0.25": (23, 15, 152), "0.5": (228, 38, 100), "1": (225, 220, 75), "10": (30, 75, 65),
           "20": (165, 215, 65)}
SEEDS = {"0.25": (920, 297), "0.5": (920, 384)}


def read_F(image, at, F):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    others = [c for k, c in COLOURS.items() if k != F] + [(255, 255, 255), (30, 30, 30)]
    spec = {"color": COLOURS[F], "others": others, "tol": 60, "smax": 40, "drop_markers": 1.5,
            "major": 0.75, "ref_width": 2300, "seed": SEEDS[F], "left_from": 250,
            "x": {"labels": [1e-4, 1e-2, 1, 10], "scale": "log10", "x0_at_axis": True, "x_end_at_axis": True},
            "y": {"labels": [1, 0.6, 0.4, 0.2, 0], "y0_at_axis": True, "y_end_at_axis": True}}
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.read_spec(image, at, spec)
