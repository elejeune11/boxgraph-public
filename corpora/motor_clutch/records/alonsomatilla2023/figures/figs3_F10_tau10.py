"""Fig. S3, right (PDF p. 27): the solid green line, tau = 10, F = 10 (Eq. 6 with C2 = 0.4, C3 = 0.05).

Read by the shared code in _fig.py (calibration from the inward tick marks matched to the
printed labels below; see that file's docstring). The hash pins _fig.py. Symbols of the same
colour on the line are left out and bridged; positions are chosen between the symbols. The
legend is blanked.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")
SHARED_SHA256 = "7bb929929258596d080593ab569aadb81597a1f7e10a4a6e2017c0217e5f40d5"

SPEC = {"color": (40, 115, 65), "others": [(20, 10, 150), (220, 30, 100), (250, 70, 10), (255, 255, 255), (30, 30, 30)],
        "tol": 60, "smax": 40, "drop_markers": 1.5, "left_from_top": True, "ref_width": 3030, "seed": (1970, 1909),
        "blank": [[1850, 200, 2900, 980]],
        "x": {"labels": [500, 1000, 1500]},
        # the tick at 0.01 is hidden by the magenta curve on the left and not found on the right
        "y": {"labels": [0.02, 0.015, 0.005, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_fig.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # the curve starts at the top-left corner and hides the top of the left axis: take the
    # left axis as found, but its top (where the inward x ticks hang from the top line) from
    # the top line, as the 'left_from_top' search finds it
    plain = mod.axes_lines

    def axes_lines(img, s):
        left, bottom = plain(img, dict(s, left_from_top=False))
        top_left, _ = plain(img, dict(s, left_from_top=True))
        return dict(left, r0=top_left["r0"]), bottom

    mod.axes_lines = axes_lines
    return mod.read_spec(image, at, SPEC)
