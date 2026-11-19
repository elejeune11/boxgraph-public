# Fig. 5 (PDF p. 9): circular family tree with coloured state dots at the tips (orange: at
# equilibrium; pink: not at equilibrium, lambda > 3 um; green: 1-3 um; blue: < 1 um). Each dot
# is found by colour (hue band, saturation > 0.3), opened with a disk to drop thin coloured tree
# lines and text, and split into single dots at the maxima of its distance transform (touching
# dots of one colour); maxima closer than 18 px (about one dot radius at 600 dpi) are one dot.
# Calibration: the tree centre is the least-squares circle through the centres of all dots of
# all colours (the dots of a family stack radially, the innermost dot of each family lies on
# one circle); each dot is reported by its angular position about that centre, in degrees
# clockwise from 12 o'clock (x), with y = 1 for "this state is present" (one point per dot).
# Every reading of this figure uses the same centre, so the four colours can be matched by angle.
import numpy as np
from scipy import ndimage

BANDS = {"orange": (10, 50), "green": (70, 140), "blue": (180, 230), "pink": (300, 345)}
MERGE_PX = 18.0


def _hue_sat(image):
    im = image[..., :3].astype(float) / 255
    mx, mn = im.max(-1), im.min(-1)
    sat = mx - mn
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    d = np.where(sat > 0, sat, 1)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, sat


def dots(image, colour):
    h, sat = _hue_sat(image)
    lo, hi = BANDS[colour]
    yy, xx = np.mgrid[-9:10, -9:10]
    disk = xx**2 + yy**2 <= 81
    m = (sat > 0.3) & (h >= lo) & (h < hi)
    m = ndimage.binary_fill_holes(ndimage.binary_opening(m, structure=disk))
    dt = ndimage.distance_transform_edt(m)
    pk = (dt == ndimage.maximum_filter(dt, size=21)) & (dt > 11)
    lab, n = ndimage.label(pk)
    cs = ndimage.center_of_mass(pk, lab, range(1, n + 1))
    pts = []
    for (y, x) in sorted(cs):
        if all((y - p[0]) ** 2 + (x - p[1]) ** 2 >= MERGE_PX**2 for p in pts):
            pts.append((float(y), float(x)))
    return pts


def centre(image):
    pts = [p for c in BANDS for p in dots(image, c)]
    Y = np.array([p[0] for p in pts])
    X = np.array([p[1] for p in pts])
    A = np.c_[2 * X, 2 * Y, np.ones(len(X))]
    sol, *_ = np.linalg.lstsq(A, X**2 + Y**2, rcond=None)
    cx, cy = float(sol[0]), float(sol[1])
    radius = float(np.sqrt(sol[2] + cx**2 + cy**2))
    return cx, cy, radius


def read_colour(image, colour):
    cx, cy, radius = centre(image)
    out = []
    for (y, x) in dots(image, colour):
        ang = float(np.degrees(np.arctan2(x - cx, -(y - cy))) % 360)
        rr = float(np.hypot(x - cx, y - cy))
        # the angle is uncertain by about 2 px of the dot centre at its radius
        da = float(np.degrees(2.0 / rr))
        out.append({"x": round(ang, 3), "y": 1.0, "lo": 1.0, "hi": 1.0, "px": [x, y],
                    "note": f"{colour} dot at {ang:.2f} deg (+/- {da:.2f}), radius {rr:.0f} px; centre ({cx:.0f}, {cy:.0f})"})
    out.sort(key=lambda d: d["x"])
    return out
