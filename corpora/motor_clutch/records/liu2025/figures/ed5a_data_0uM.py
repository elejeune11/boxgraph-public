"""Extended Data Fig. 5(a) (PDF p. 70): measured cell traction of MEF Talin 1 KO, Talin 2 shRNA
cells without blebbistatin (0 uM, pink circles), data of ref. 13.

Shared code in _hd.py. x: log axis, the decade ticks 10^2, 10^3, 10^4, 10^5, 10^6 (labelled
10^2, 10^4, 10^6); y: the long ticks 0, 40, 80, 120 (the short ones between are 20, 60, 100).
Symbols: blobs of the fill colour (the figure is a coarse web raster), each at its centroid; the
legend and the coloured sigma_m labels are left out.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 40), (2, 80), (3, 120)], "major": 0.8},
}
EXCLUDE = [(700, 150, 1480, 740), (1950, 0, 3400, 380), (1850, 470, 2800, 690), (2050, 810, 3050, 1030),
           (2270, 1140, 3250, 1350)]
SYMBOL = ((250, 155, 153), 50, "circle")
KW = {"mode": "fill"}  # a coarse web raster (about 7.6 rendered px per source pixel): symbols by their fill


def read(image, at):
    fill, tol, shape = SYMBOL
    return H.read_symbols(image, SPEC, fill, tol, shape, exclude=EXCLUDE, **KW)
