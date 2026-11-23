"""Fig. 4(c) (PDF p. 10): measured cell traction of vinculin VD1-expressing MEF cells (blue
downward triangles), data of refs. 13, 21.

Shared code in _hd.py. x: log axis, decade ticks 10^2 ... 10^6 left of the axis break (labelled
10^2, 10^4, 10^6); y: ticks 0, 60, 120, 180. Symbols: blobs of the fill colour, joined where a
curve or another symbol cuts them; the legends are left out.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "major": 0.8, "region": (300, 1520)},
    "y": {"marks": [(0, 0), (1, 60), (2, 120), (3, 180)], "major": 0.8},
}
EXCLUDE = [(0, 0, 2500, 215), (1290, 925, 2100, 1440)]


def read_kind(image, rgb, shape, **kw):
    return H.read_symbols(image, SPEC, rgb, 50, shape, exclude=EXCLUDE, mode="fill", **kw)


def read(image, at):
    return read_kind(image, (133, 210, 250), "down")
