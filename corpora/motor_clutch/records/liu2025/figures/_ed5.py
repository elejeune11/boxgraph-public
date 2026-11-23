"""Shared settings for Extended Data Fig. 5 (PDF p. 70), read by _fig.py.

Both panels: x log axis, major ticks at the decades 10^2 (at the spine) to 10^6, labelled
10^2, 10^4, 10^6 on every other one. y: (a) labelled ticks 0, 40, 80, 120; (b) 0, 60, 120, 180.
The model curves are saturated red, green and blue; the data markers are lighter tints of the
same colours and fall outside the colour boxes. The sigma_m labels and legends are coloured
text and are blanked.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_fig", Path(__file__).with_name("_fig.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)

RGB = {
    "red": ((170, 0, 0), (255, 70, 70)),
    "green": ((0, 160, 0), (80, 240, 80)),
    "blue": ((0, 0, 140), (80, 80, 255)),
}

PANEL = {
    "a": {
        "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)]},
        "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)]},
        "blank": [(195, 50, 320, 75), (220, 86, 340, 115), (240, 122, 365, 150), (210, 20, 265, 42)],
    },
    "b": {
        "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)]},
        "y": {"marks": [(0, 0), (1, 60), (2, 120), (3, 180)]},
        "blank": [(280, 25, 392, 48), (280, 125, 392, 145), (280, 194, 392, 214), (100, 18, 150, 64)],
    },
}


def read(image, at, panel, colour, pick="top", n_runs=None, blank=()):
    spec = dict(PANEL[panel])
    spec["rgb"] = RGB[colour]
    spec["pick"] = pick
    if n_runs:
        spec["n_runs"] = n_runs
    spec["blank"] = list(spec["blank"]) + list(blank)
    return F.read_curve(image, spec, at)


def debug(image, panel):
    cal = F.calibrate(image, PANEL[panel])
    return {"sp": cal["sp"], "xt": cal["xt"], "yt": cal["yt"], "xmis": cal["x"]["misfit"], "ymis": cal["y"]["misfit"]}
