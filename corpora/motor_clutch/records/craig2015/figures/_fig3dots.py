"""The filled black dots (predicted adhesion density / maximum) of the right-hand panels of Fig. 3 (PDF p. 9).

Read by the kit's read_dots (_kit.py; see its docstring) with every dot read (x from the image) and no error
bars. Two changes, in a private copy of the kit: a dot must have an area of at least 800 px (the dots are
compact ~30-36 px squares of area 830-1080 at 1200 dpi), and blobs of area >= 600 whose bounding box is
elongated (aspect outside 0.7-1.4) are not dots: they are merged dark dashes of the 'whisker' series (the
myosin density, drawn as light 'x' glyphs with a dark dash beside each) or a whisker crossing a tick. The
ticks (area < 500) are unaffected. Ticks: inner only (the corner ticks merge with the frame).
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_kit_f3", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)

_blobs = _kit._blobs


def _compact_blobs(mask):
    out = []
    for b in _blobs(mask):
        h, w = b["r1"] - b["r0"], b["c1"] - b["c0"]
        if b["area"] >= 600 and not (0.7 <= h / w <= 1.4):
            continue
        out.append(b)
    return out


_kit._blobs = _compact_blobs  # this private copy only
_calibrate = _kit.calibrate


def _inner(image, xlabels, ylabels, **kw):
    return _calibrate(image, xlabels, ylabels, **{**kw, "y_inner_only": True, "x_inner_only": True})


_kit.calibrate = _inner  # corner ticks merge with the frame: inner ticks only


def read(image, at, xlabels, ylabels):
    return _kit.read_dots(image, at, xlabels, ylabels, error_bars=False, min_dot_area=800)
