"""Fig. 3 D (PDF p. 4): one framed strip of the four stacked time courses of a single FA,
black dots joined by lines.

Calibration from the image: the strip's frame (the longest dark lines in the crop); x from
the long ticks on the strip's bottom edge, labelled 0, 2, ..., 14 in the bottom strip (all
strips share the columns), anchored on the left frame edge (0) and the short ticks halfway;
y from the long ticks on the left edge, anchored on the bottom frame edge (0, the caller says
the step), short ticks halfway. The top and right edges carry no label and are not used.
Markers: dark blobs that survive an opening with a disk narrower than a dot (which removes the
joining lines, the dashed line and text strokes) and are about one dot in size; see _dots.py.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_dots", Path(__file__).with_name("_dots.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
L = D.L


def read_strip(img, ystep, open_r=14, what="black dot"):
    mask = L.neutral_dark(img, 110)
    return D.read_markers(img, mask, (0.0, (None, 1)), 2.0, (0.0, (None, 1)), ystep, open_r=open_r,
                          what=what, shape="blob")
