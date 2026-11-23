"""Fig. 3(a) (PDF p. 8): measured cell traction of MEF WT cells on substrates coated with
10 ug/ml fibronectin (pink circles), data of ref. 13.

Shared code in _hd.py. x: log axis, decade ticks 10^2 ... 10^6 (labelled 10^2, 10^4, 10^6);
y: ticks 0, 60, 120, 180. Symbols: blobs of the fill colour, joined where a curve cuts them; the
two legends are left out.
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
EXCLUDE = [(300, 0, 920, 440), (1070, 800, 1800, 1160)]
KW = {"mode": "fill"}
FILLS = {"circle": (248, 152, 152), "up": (119, 255, 119), "down": (133, 210, 250)}


def read_kind(image, shape, **kw):
    return H.read_symbols(image, SPEC, FILLS[shape], 50, shape, exclude=EXCLUDE, **KW, **kw)


def read(image, at):
    return read_kind(image, "circle")
