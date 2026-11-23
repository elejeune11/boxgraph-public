"""Fig. 4(g) (PDF p. 10): the two yellow markers on the 'No VD1' force-extension trace of talin
(ref. 22), at 5 and 10 pN: the points from which the text takes the ~40 nm extension difference.

Shared code in _hd.py. x: ticks 0, 5, ..., 25 pN; y: ticks 200, 400, 600, 800 nm; both sets of
ticks point into the frame. Markers: blobs of the yellow fill, at their centres. The lower pair
(below the 300 nm level, on the purple trace) is this reading; the upper pair is fig4g_vd1.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    # the 0 tick merges with the frame's corner and the 10 tick with a dashed guide line: the ticks
    # used are 5, 10, 15, 20, 25 (all ticks at least 0.4 of the longest)
    "x": {"marks": [(0, 5), (1, 10), (2, 15), (3, 20), (4, 25)], "major": 0.4, "inward": True,
          "region": (1100, 3000)},
    # the 800 tick merges with the frame's top: the ticks used are 200, 400, 600
    "y": {"marks": [(0, 200), (1, 400), (2, 600)], "major": 0.8, "inward": True, "region": (300, 1700)},
}


def read_part(image, lower):
    cal = H.calibrate(image, SPEC)
    cut = int(cal["y"].px(300.0))
    sp = cal["sp"]
    if lower:
        box = lambda s: (sp["c1"] + 2, cut, sp["x_to"], sp["r0"] - 1)  # noqa: E731
    else:
        box = lambda s: (sp["c1"] + 2, sp["y_from"], sp["x_to"], cut)  # noqa: E731
    spec = dict(SPEC, box=box)
    return H.read_symbols(image, spec, (255, 240, 0), 60, "circle", mode="fill")


def read(image, at):
    return read_part(image, True)
