"""Shared stub body for the four lines of Fig. 5(A) (PDF p. 10): F_opt against omega on a rigid
substrate, tau = 1, 5, 10, 20. Read by _fig.py (calibration from the inward tick marks matched
to the printed labels: x ticks at 200-800 and the right line of the box at 1000; y ticks at
1, 2, 3, the bottom line at 0 and the top line at 4). The legend is blanked. Symbols of the
same colour on the lines are left out and bridged; positions are chosen between them.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

COLOURS = {1: (255, 117, 1), 5: (158, 200, 241), 10: (207, 154, 230), 20: (251, 190, 201)}
SEEDS = {1: (1212, 1455), 5: (1212, 1318), 10: (1212, 1220), 20: (1212, 1100)}


def read_tau(image, at, tau):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    others = [c for t, c in COLOURS.items() if t != tau] + [(255, 255, 255), (30, 30, 30)]
    spec = {"color": COLOURS[tau], "others": others, "tol": 45, "smax": 40, "drop_markers": 1.5,
            "ref_width": 2017, "seed": SEEDS[tau], "left_from": 300, "blank": [[1400, 180, 1930, 690]],
            "x": {"labels": [200, 400, 600, 800, 1000], "x_end_at_axis": True},
            "y": {"labels": [4, 3, 2, 1, 0], "y0_at_axis": True, "y_end_at_axis": True}}
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.read_spec(image, at, spec)
