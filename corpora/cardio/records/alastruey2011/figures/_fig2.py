"""Shared reading code for Fig. 2 (PDF p. 5): the uniaxial extension test of a silicone sample.

(a) normalised load (thin solid line) and extension (thick dashed line) against time; read only
    during the two holds (about 19-47 s at zero extension, 53-111 s at full extension), where the
    two lines are apart; in the ramps they lie on each other.
(b) the load-extension loop of the first cycle: loading (solid) and unloading (dashed) lie within
    about one line width of each other throughout and are read together, as one band.

Calibration, all from the image, with the frame and tick finders of _fig3.py (same MATLAB style):
the inward tick marks on the bottom and left frame lines with a dotted grid line from them, matched
to the printed labels in the spec (in (a) the curves hide the 0.2 tick: the ticks found are matched
on the even spacing between the first and last labels, _fig3._fit_gaps); a straight-line fit whose
largest misfit is added to every interval.

In (a) the lines are told apart in the flat holds: the dashed extension line makes runs exactly 25
px tall starting on one row, column after column; the solid load line (about 8 px wide, noisy)
makes runs 10-32 px tall that wander; grid dots are 9 px or less. The legend of (a) is found as a
rectangle (two dark rows with the same long run joined by dark columns at both ends) and masked;
_fig3's legend finder would take the long load line for a border.
  extension (a): the row band where runs 24-26 px tall start on the same row in at least 15 of the
    columns within 60 px of x; its centre, +- 3 px.
  load (a): the one run 10-32 px tall in the column of x outside that band (the load
    trace is noisy: it is read where it is), interval its extent less half the line's width (4 px),
    widened by 2 px. No such run or more than one: unreadable.
  loop (b): the reference row is the median centre of the runs 10 px or taller (grid dots are
    shorter) in the columns within 40 px of x, and the local slope a straight-line fit to them;
    the band is the runs in the column within 40 px of the reference (the arrows are farther);
    either branch lies in it from its top plus half a solid line's vertical thickness (8 px *
    sqrt(1 + slope^2)) to its bottom less that, widened by 2 px.
Every interval also has the calibration misfit and 1 px.
"""

import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage


def _f3():
    spec = importlib.util.spec_from_file_location("alastruey2011_fig3_for2", Path(__file__).with_name("_fig3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _dash_band(f3, ink, c):
    """Rows of the flat dashed line near column c: runs exactly 24-26 px tall starting on the same
    row in at least 15 of the columns within 60 px (the noisy solid line never repeats so)."""
    count = {}
    for k in range(c - 60, c + 61):
        for a, b in f3._runs(ink[:, k]):
            if 24 <= b - a <= 26:
                count[a] = count.get(a, 0) + 1
    if not count:
        return None
    a = max(count, key=count.get)
    return (a, a + 25) if count[a] >= 15 else None


def _box(f3, ink):
    """The legend box as a rectangle: two dark rows with the same longest run (at least 400 px, ends
    within 3 px), 150 px or more apart, joined at both ends by columns dark over 95% between them."""
    H = ink.shape[0]
    rows = []
    for r in range(H):
        a, b = f3._longest(ink[r])
        if b - a >= 400:
            rows.append((r, a, b))
    for i, (r1, a1, b1) in enumerate(rows):
        for r2, a2, b2 in rows[i + 1:]:
            if r2 - r1 < 150 or abs(a1 - a2) > 3 or abs(b1 - b2) > 3:
                continue
            left = ink[r1:r2, a1 + 2].mean() >= 0.95
            right = ink[r1:r2, b1 - 3].mean() >= 0.95
            if left and right:
                return (r1 - 6, r2 + 6, a1 - 6, b1 + 6)
    return None


def read_spec(image, at, spec):
    f3 = _f3()
    g = image[..., :3].astype(float).mean(axis=2)
    dark = g < 128
    fr = f3.frame(dark)
    xt, yt = f3.ticks(dark, fr)
    xa, xb, xm = f3._fit_gaps(xt, spec["x"], "x axis")
    ya, yb, ym = f3._fit_gaps(yt, spec["y"], "y axis")
    inside = np.zeros_like(dark)
    inside[fr["top"] + 3:fr["bottom"] - 3, fr["left"] + 3:fr["right"] - 3] = True
    leg = f3._legend(dark, fr) if spec["curve"] == "loop" else _box(f3, dark)
    if leg is not None:
        inside[max(leg[0], 0):leg[1], max(leg[2], 0):leg[3]] = False
    ink = dark & inside
    yy, xx = np.mgrid[-5:6, -5:6]
    thick = ndimage.binary_opening(ink, structure=(xx * xx + yy * yy) <= 5.5 * 5.5)
    thin = ink & ~ndimage.binary_dilation(thick, iterations=3)
    curve = spec["curve"]
    out = []
    for x in at:
        c = int(round((x - xa) / xb))
        if curve in ("extension", "load"):
            band = _dash_band(f3, ink, c)
        if curve == "extension":
            if band is None:
                out.append({"x": x, "y": None, "note": "no flat dashed line near"})
                continue
            yc = (band[0] + band[1] - 1) / 2.0
            lo, hi = yc - 3.0, yc + 3.0
            note = "dashed line"
        elif curve == "load":
            rs = [(a, b) for a, b in f3._runs(ink[:, c]) if 10 <= b - a <= 32
                  and (band is None or b <= band[0] or a >= band[1])]
            if len(rs) != 1:
                out.append({"x": x, "y": None, "note": f"{len(rs)} solid-line runs in the column"})
                continue
            a, b = rs[0]
            lo, hi = a + 4.0 - 2.0, b - 1 - 4.0 + 2.0
            if hi < lo:
                lo = hi = (a + b - 1) / 2.0
            yc = (lo + hi) / 2.0
            note = "solid line"
        else:
            near = [(k, (a + b - 1) / 2.0) for k in range(c - 40, c + 41) for a, b in f3._runs(ink[:, k])
                    if b - a >= 10]
            if len(near) < 20:
                out.append({"x": x, "y": None, "note": "no loop ink near"})
                continue
            f = float(np.median([m for _, m in near]))
            band = [(a, b) for a, b in f3._runs(ink[:, c]) if b - a >= 10 and abs((a + b - 1) / 2.0 - f) <= 40]
            if not band:
                out.append({"x": x, "y": None, "note": "no ink near the loop"})
                continue
            kk = np.array([k for k, _ in near], float)
            s = np.polyfit(kk, [m for _, m in near], 1)[0]
            h = 8.0 * np.sqrt(1 + s * s)
            top, bot = min(r[0] for r in band), max(r[1] for r in band) - 1
            lo, hi = top + h / 2 - 2, bot - h / 2 + 2
            if hi < lo:
                lo = hi = (top + bot) / 2.0
            yc = (lo + hi) / 2.0
            note = f"band of {len(band)} run(s)"
        pad = ym + 1.0
        lo, hi = lo - pad, hi + pad
        v, v1, v2 = (ya + yb * r for r in (yc, lo, hi))
        out.append({"x": float(x), "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(c), float(yc)], "px_lo": float(lo), "px_hi": float(hi),
                    "note": f"{note}; x misfit {xm:.1f} px, y misfit {ym:.1f} px"})
    return out
