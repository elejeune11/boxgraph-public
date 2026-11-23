"""Extended Data Fig. 5(b) (PDF p. 70): measured cell traction of MEF WT cells without
blebbistatin (0 uM, pink circles), data of ref. 13.

Shared code in _hd.py. x: log axis, decade ticks 10^2 ... 10^6 (labelled 10^2, 10^4, 10^6);
y: the long ticks 0, 60, 120, 180 (the short ones between are 30, 90, 150). Symbols: blobs of
the fill colour (a coarse web raster), joined where a curve cuts them; the legends and the
coloured sigma_m labels are left out.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"scale": "log10", "marks": [(0, 1e2), (2, 1e4), (4, 1e6)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 60), (2, 120), (3, 180)], "major": 0.8},
}
EXCLUDE = [(990, 0, 2240, 570), (1000, 740, 1920, 1480), (2600, 265, 3590, 460), (2600, 1140, 3590, 1330),
           (2600, 1750, 3590, 1960)]
KW = {"mode": "fill"}


def read(image, at):
    return H.read_symbols(image, SPEC, (250, 155, 153), 50, "circle", exclude=EXCLUDE, **KW)
