"""Pastel curves of the raster Fig. 4 profile panels (PDF p. 10): six thin, pale MATLAB curves per panel.

Calibration: the kit's (`_kit.calibrate`: grey frame; dark ticks paired top/bottom and left/right,
matched to the printed labels the stub gives; fit and misfit as in the kit).

Curve pixels: the curves are too pale for an RGB-distance mask (the green differs from grey by ~15
levels), so a pixel belongs to a curve when its hue lies in the curve's window and its saturation
(max - min of R, G, B) exceeds a floor. Windows and floors were set from the hue histogram of the curve
pixels of Fig. 4(b), whose six clusters are well apart: red 335-25 deg, yellow 50-80, green 88-150,
cyan 150-210, blue 225-265, magenta 270-310; floor 18 (green and cyan, the palest, 10). The green
window starts at 88, not 80: where yellow and green run together, the light antialiased fringe of the
yellow line has hues near 81 (seen in Fig. 4(a) at x = 0.5), while the green line's own pixels lie at
90-131 deg. A black curve ("black") is drawn by this raster as light grey (core ~184, edges ~211-218,
as grey as the frame, 200-209): its pixels are the neutral ones (saturation < 20) below grey 225; the frame
is excluded by position (below), and the curve must be read away from the dark tick columns. Pixels within
3 px of the frame are dropped. A legend's sample line (a short flat piece with dark legend text just
to its right) is dropped as in _kit.read_curve(legend_text=True).

Reading: in the 5 columns around each x, the rows of curve pixels split into runs (gaps > 6 px, the
raster's block size); the longest run is the curve (antialiased crossings of two other curves can blend
into a short run of a third hue). Where the curves bundle together, the fringe of one curve can fall
into another's hue window (in Fig. 4(a) at x = 0.5 a yellow fringe read as green), so a position is not
read when pixels of any other curve's class lie within 6 px (one raster block, i.e. no paper between
the two lines) of the run: there the curves touch and cannot be told apart. Value: the run's centre. Interval: the run's extent widened by half
a raster block (3 px), the y misfit and the x misfit times the local slope, converted to values.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location("craig2015_kit_pastel", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)

HUES = {"red": (335, 25, 18), "yellow": (50, 80, 18), "green": (88, 150, 10), "cyan": (150, 210, 10),
        "blue": (225, 265, 18), "magenta": (270, 310, 18)}


def _hue(a):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    d = np.where(mx - mn == 0, 1, mx - mn)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4))
    return h * 60.0, mx - mn


def mask(image, name, frame):
    a = np.asarray(image, dtype=float)[:, :, :3]
    h, s = _hue(a)
    if name == "black":  # the raster draws the 'black' line as light grey (core ~184, edges ~215)
        m = (s < 20) & (a.mean(axis=2) < 225)
    else:
        h0, h1, smin = HUES[name]
        inh = ((h >= h0) | (h < h1)) if h0 > h1 else ((h >= h0) & (h < h1))
        m = inh & (s > smin)
    L, T, R, B = frame
    m[:T + 3, :] = False
    m[B - 2:, :] = False
    m[:, :L + 3] = False
    m[:, R - 2:] = False
    dark = (_kit._gray(image) < 90) & ((a.max(axis=2) - a.min(axis=2)) < 60)
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if (sl[1].stop - sl[1].start) < 700 and (sl[0].stop - sl[0].start) < 15:
            c0, c1 = sl[1].stop + 5, min(sl[1].stop + 200, R - 50)
            if c1 > c0 and dark[max(sl[0].start - 40, 0):sl[0].stop + 40, c0:c1].sum() > 50:
                m[sl][lab[sl] == i + 1] = False
    return m


TOUCH = 6  # px, one raster block: no paper between the two lines


def read(image, at, xlabels, ylabels, name, inner_margin=12):
    # inner ticks only: the corner ticks merge with the frame (a tick closer than inner_margin px to it)
    cal = _kit.calibrate(image, xlabels, ylabels, y_inner_only=True, x_inner_only=True, inner_margin=inner_margin)
    m = mask(image, name, cal["frame"])
    others = np.zeros_like(m)
    for o in HUES:
        if o != name:
            others |= mask(image, o, cal["frame"])
    ky = abs(cal["ky"])
    out = []

    def centre(cc):
        rr = np.nonzero(m[:, max(cc - 2, 0):cc + 3].any(axis=1))[0]
        if not len(rr):
            return None
        runs = np.split(rr, np.nonzero(np.diff(rr) > 6)[0] + 1)
        run = max(runs, key=len)
        return 0.5 * (run.min() + run.max())

    for x in at:
        c = int(round((x - cal["cx"]) / cal["kx"]))
        rows = np.nonzero(m[:, max(c - 2, 0):c + 3].any(axis=1))[0]
        if not len(rows):
            out.append({"x": x, "y": None, "note": "no pixels of the curve's hue in this column"})
            continue
        runs = np.split(rows, np.nonzero(np.diff(rows) > 6)[0] + 1)
        run = max(runs, key=len)
        r0, r1 = int(run.min()), int(run.max())
        near = others[max(r0 - TOUCH, 0):r1 + TOUCH + 1, max(c - 2, 0):c + 3]
        if near.any():
            out.append({"x": x, "y": None, "note": f"another curve within {TOUCH} px of rows {r0}-{r1}: "
                                                     "the curves cannot be told apart here"})
            continue
        rc = 0.5 * (r0 + r1)
        cl, cr = centre(c - 40), centre(c + 40)
        slope = abs(cr - cl) / 80 if cl is not None and cr is not None else 0.0
        w = 3 + cal["my"] + slope * cal["mx"]
        ya, yb = cal["ky"] * (r0 - w) + cal["cy"], cal["ky"] * (r1 + w) + cal["cy"]
        y = cal["ky"] * rc + cal["cy"]
        out.append({"x": x, "y": y, "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, rc], "px_lo": r0, "px_hi": r1,
                    "note": f"longest run of the {name} hue, rows {r0}-{r1}" + (f" ({len(runs)} runs)" if len(runs) > 1 else "")})
    return out
