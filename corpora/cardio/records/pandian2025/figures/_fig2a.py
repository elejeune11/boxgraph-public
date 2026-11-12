"""Shared reading code for Fig. 2a (PDF p. 5): vessel diameters from three algorithms (y) against the
manually measured diameter of the same vessels (x). Pink filled squares: the paper's in-house code;
teal filled diamonds: mu-VES3D; light blue open circles: REAVER. Each series has a fit line drawn in
its own colour (pink solid, teal dotted, light blue dash-dot) that passes through some markers.

The figure is a raster image embedded in the PDF; rendered at 900 dpi one axis unit (1 um) is about
42 px.

Calibration (from the image, see _axes.py): the axis lines are the darkest column / row; the major
ticks are dark runs at least 25 px long outside the axes. Their centres are matched in order to the
printed labels 40, 30, 20, 10, 0 (y, top to bottom) and 0, 10, 20, 30, 40 (x, left to right); the
largest misfit of a straight line widens every interval.

Markers. Pixels of the series colour are found by RGB distance. The legend (upper left, left of
column 700 and above row 600) is left out.
- Filled markers (squares, diamonds) are about 55-60 px across, the fit lines at most about 25 px
  thick and the dots of the dotted line about 16 px. The distance transform of the colour mask is
  therefore above `core` (px) only inside a marker; each local maximum above `core`, at least `sep`
  px from a higher one, is a marker centre. Where a marker sits on its own fit line the maximum is
  pulled along the line by up to a few px; the interval allows `pull` px.
- The pink squares (three of which lie on the pink line) are then re-located by matching a square minus its
  surrounding ring (square_centres); this puts them at the same manual diameters as the other two series.
- Open circles are rings about 6-9 px thick, radius about 30 px. The thick dashes of the fit line
  are removed (a morphological opening with a 13 px square keeps only parts thicker than the ring,
  which are then dilated and subtracted). The remaining ring pixels are correlated with an annulus
  of the radius that gives the strongest response (searched 24-38 px); local maxima above half the
  best response are circle centres.

Each value is the marker centre converted with the calibration. Interval: +/- (pull + misfit + 2) px
in y; x is read the same way and reported in the note (the x positions are what the model uses).
"""

import numpy as np
from scipy import ndimage as ndi
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_axes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

FRAC = 0.28  # the ring half hidden behind two pink squares at x = 21 scores 0.33; stray dash ends score <= 0.19
COLORS = {"pink": (235, 25, 110), "teal": (1, 141, 145), "blue": (110, 205, 240)}


def calibrate(image):
    g = A.gray(image)
    ya, xa = A.frame(g, (250, 2050, 50, 2150))
    ty = A.ticks_left(g, ya, (50, xa[1] + 5), 25)
    tx = A.ticks_down(g, xa, (ya[0] - 5, 2050), 25)
    ay, by, my = A.fit(ty, [40, 30, 20, 10, 0])
    ax, bx, mx = A.fit(tx, [0, 10, 20, 30, 40])
    return dict(ay=ay, by=by, my=my, ax=ax, bx=bx, mx=mx, ya=ya, xa=xa)


def mask_of(image, name, tol=70):
    d = np.sqrt(((image[..., :3].astype(float) - np.array(COLORS[name], float)) ** 2).sum(axis=2))
    m = d < tol
    m[:600, :700] = False  # legend
    return m


def filled_centres(image, name, core, split=20.0, inset=4.0):
    """Marker centres: each connected region where the distance transform is >= core. A single marker
    gives a small core (under 10 px across); two overlapping markers give an elongated core, which is
    split into two centres at the ends of its long axis, each moved `inset` px inwards."""
    m = mask_of(image, name)
    dt = ndi.distance_transform_edt(m)
    lab, n = ndi.label(dt >= core)
    out = []
    for k in range(1, n + 1):
        rr, cc = np.nonzero(lab == k)
        pts = np.c_[cc, rr].astype(float)
        mu = pts.mean(axis=0)
        if len(pts) < 3:
            out.append((float(mu[0]), float(mu[1]), float(dt[rr, cc].max()), "single"))
            continue
        w, v = np.linalg.eigh(np.cov((pts - mu).T))
        ax = v[:, -1]
        t = (pts - mu) @ ax
        if t.max() - t.min() < split:
            # the dt maximum, not the core's centroid: a line through the marker extends the core one way
            i = int(np.argmax(dt[rr, cc]))
            out.append((float(cc[i]), float(rr[i]), float(dt[rr[i], cc[i]]), "single"))
        else:
            for e in (t.min() + inset, t.max() - inset):
                p = mu + e * ax
                out.append((float(p[0]), float(p[1]), float(t.max() - t.min()), "split"))
    return out


def square_centres(image, name, ringw=4):
    """Filled squares that may sit on their own fit line: the mask is correlated with a kernel that is +1 on a
    square of side s and -1 on a ring of width `ringw` around it (each part normalised to its area). A position
    slid along the line puts square pixels into the ring and scores lower, so the maximum stays on the square.
    The side s is the one (38-50 px) whose best match over the plot is strongest. Each square is searched
    within 30 px of its distance-transform maximum (filled_centres)."""
    m = mask_of(image, name).astype(float)
    seeds = filled_centres(image, name, 18, split=1e9)
    best = None
    for s in range(38, 51, 2):
        h = s // 2
        R = h + ringw
        k = np.full((2 * R + 1, 2 * R + 1), -1.0 / ((2 * R + 1) ** 2 - (2 * h + 1) ** 2))
        k[R - h:R + h + 1, R - h:R + h + 1] = 1.0 / (2 * h + 1) ** 2
        sc = ndi.correlate(m, k, mode="constant")
        if best is None or sc.max() > best[1].max():
            best = (s, sc)
    s, sc = best
    out = []
    for c, r, _, _ in seeds:
        r0, c0 = int(r), int(c)
        win = sc[r0 - 30:r0 + 31, c0 - 30:c0 + 31]
        rr, cc = np.unravel_index(int(np.argmax(win)), win.shape)
        out.append((float(c0 - 30 + cc), float(r0 - 30 + rr), float(win.max()), f"square side {s} px"))
    return out


def ring_centres(image, name):
    m = mask_of(image, name)
    thick = ndi.binary_opening(m, structure=np.ones((13, 13)))
    ring = m & ~ndi.binary_dilation(thick, iterations=4)
    best = None
    yy, xx = np.mgrid[-45:46, -45:46]
    rr = np.hypot(yy, xx)
    for R in range(24, 39):
        ann = ((rr >= R - 4) & (rr <= R + 4)).astype(float)
        resp = ndi.convolve(ring.astype(float), ann, mode="constant") / ann.sum()
        if best is None or resp.max() > best[1].max():
            best = (R, resp)
    R, resp = best
    pk = A.peaks(resp, FRAC * resp.max(), R)
    return [(float(c), float(r), float(resp[r, c]), "ring") for r, c in pk], R


def to_readings(cal, cents, pull, kind):
    out = []
    tol = pull + cal["my"] + 2
    for c, r, s, how in sorted(cents):
        t = tol + (8 if how == "split" else 0)
        x = cal["ax"] + cal["bx"] * c
        y = cal["ay"] + cal["by"] * r
        lo, hi = sorted((cal["ay"] + cal["by"] * (r + t), cal["ay"] + cal["by"] * (r - t)))
        out.append({"x": round(x, 3), "y": y, "lo": lo, "hi": hi, "px": [c, r],
                    "px_lo": r + t, "px_hi": r - t,
                    "note": f"{kind} ({how}) at x = {x:.2f} um (manual diameter); score {s:.2f}; tick misfit "
                            f"{cal['my']:.2f} px (y), {cal['mx']:.2f} px (x)"})
    return out
