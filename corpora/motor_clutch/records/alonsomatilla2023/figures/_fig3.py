"""Shared stub body for lines of Fig. 3(A, B) (PDF p. 7): time-averaged traction against the
clutch stiffness parameter beta_c (log10 axis), F = 1, omega' = 200, K' = 0.01 (A) or 1 (B).
Read by _fig.py: x calibrated from the long tick at 10^0 with the left line of the box at
10^-2 and the right line at 10^2 (log10); y from the ticks the stub names (lines hide the others
on both sides) with the bottom line at 0 and the top line at 1. Symbols of the same colour on the lines are left out and bridged.
The legend of (B) is blanked.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

COLOURS = {1: (115, 200, 235), 2: (140, 65, 5), 5: (5, 150, 105), 10: (250, 65, 5)}


def read_line(image, at, tau, seed, width, blank=(), ylabels=(1, 0.8, 0.6, 0.4, 0.2, 0), colours=None):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    colours = colours or COLOURS               # Fig. 3(D) names its lines by F, not tau
    others = [c for t, c in colours.items() if t != tau] + [(255, 255, 255), (30, 30, 30)]
    spec = {"color": colours[tau], "others": others, "tol": 50, "smax": 40, "drop_markers": 1.5,
            "major": 0.75, "ref_width": width, "seed": seed, "blank": [list(b) for b in blank],
            "x": {"labels": [0.01, 1, 100], "scale": "log10", "x0_at_axis": True, "x_end_at_axis": True},
            "y": {"labels": list(ylabels), "y0_at_axis": True, "y_end_at_axis": True}}
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    # the lines run into the bottom-right corner and hide the end of the bottom axis: take the
    # box's right end from the right line itself, the first dark run from the right edge of
    # the crop along the middle row of the box
    plain = mod.axes_lines

    def axes_lines(img, s):
        left, bottom = plain(img, s)
        m = mod.dark(img, s.get("thr", 110), s.get("smax", 70))
        mid = (left["r0"] + bottom["r0"]) // 2
        c = img.shape[1] - 1
        while c > left["c1"] and not m[mid, c]:
            c -= 1
        return left, dict(bottom, c1=int(c))

    mod.axes_lines = axes_lines
    return mod.read_spec(image, at, spec)
