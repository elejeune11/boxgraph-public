"""Shared reading code for Fig. 5(b), (c), (e), (f) (PDF p. 13): strain profiles against arclength s.

Each panel has black axes crossing at the origin (the horizontal axis is the strain 0, the vertical
axis s = 0), a grey band (the bend region), a thick solid blue line (Eq. 63, the large-bending model)
and a thinner red dashed line (Eq. 67, the classical model) drawn over it.

Calibration: as for Fig. 3, by the shared function calibrate() of _fig3.py (ticks crossing the
axes, matched to the printed labels; the vertical axis checked against s = 0 and the horizontal
axis against strain 0). The x ticks are every 0.5 (labelled 1, 2, 3); the y ticks as the spec says.

Colours (from the rendered page): blue (0, 0, 255), red (255, 0, 0); a pixel belongs to a colour
within 80 (RGB distance). Parts of the image listed in the spec's "exclude" (the legend) are blanked.

Blue (solid, under the red): in each column the runs of blue-or-red pixels are found; a run holding
blue is the blue stroke, possibly with red drawn over part of it. Its centre is
  both ends blue (red inside or absent): the run's middle, +- 2 px;
  only the upper end blue (red sticks out below): the upper edge + h/2, +- 2.5 px;
  only the lower end blue: the lower edge - h/2, +- 2.5 px;
where h = w sqrt(1 + slope^2), w the blue stroke's width (20th percentile of the lengths of runs with
both ends blue) and the slope from a parabola through the "both ends" centres within 40 columns;
the run used is the one nearest that parabola.
Red (dashed, on top): a parabola through the centres of the red runs within 60 columns (outliers
beyond 3 red widths dropped and refitted); in a column crossed by a dash, the dash's run nearest the
parabola gives the centre +- 2 px; in a gap between dashes the parabola gives it, +- (2 px + the
parabola's largest misfit).
A position where the curve is steeper than 1.5 px per px (the jumps at the bend region's edges) or
too few neighbours are found is not read. Every interval is widened by the y misfit + 1 px and by
|slope| times (the x misfit + the rounding of x to a column).
"""

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("haas2021_fig3_shared", Path(__file__).with_name("_fig3.py"))
_f3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f3)

BLUE = (0, 0, 255)
RED = (255, 0, 0)


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), (np.flatnonzero(d == -1) - 1).tolist()))


def _mask(img, col, tol=80.0):
    return np.sqrt(((img[..., :3].astype(float) - np.array(col, float)) ** 2).sum(axis=2)) < tol


def _blue_columns(B, U):
    """Per column: list of (a, b, kind) for union runs holding blue."""
    out = {}
    for k in range(B.shape[1]):
        lst = []
        for a, b in _runs(U[:, k]):
            if B[a:b + 1, k].sum() < 3:
                continue
            top = B[a, k] or B[min(a + 1, b), k]
            bot = B[b, k] or B[max(b - 1, a), k]
            lst.append((a, b, "both" if top and bot else "top" if top else "bottom" if bot else "none"))
        if lst:
            out[k] = lst
    return out


def _parabola(pts, x):
    ks = np.array([p[0] for p in pts], float)
    ys = np.array([p[1] for p in pts], float)
    P = np.polyfit(ks, ys, 2)
    return P, float(np.polyval(P, x)), float(np.polyval(np.polyder(P), x)), float(np.max(np.abs(np.polyval(P, ks) - ys)))


def read_spec(image, at, spec):
    cal = _f3.calibrate(image, spec)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    img = image[..., :3].copy()
    for x0, y0, x1, y1 in spec.get("exclude", []):
        img[y0:y1, x0:x1] = 255
    B, R = _mask(img, BLUE), _mask(img, RED)
    U = B | R
    out = []
    if spec["curve"] == "blue":
        cols = _blue_columns(B, U)
        both = {k: [(a, b) for a, b, kind in v if kind == "both"] for k, v in cols.items()}
        lens = [b - a + 1 for v in both.values() for a, b in v]
        w = float(np.percentile(lens, 20))
        for x in at:
            cx = (x - xa) / xb
            c = int(round(cx))
            pts = [(k, (a + b) / 2.0) for k in range(c - 40, c + 41) if k != c
                   for a, b in both.get(k, []) if len(both.get(k, [])) == 1]
            if len(pts) < 10:
                out.append({"x": x, "y": None, "note": "too few clear blue columns nearby"})
                continue
            _, pred, slope, _ = _parabola(pts, cx)
            if abs(slope) > 1.5:
                out.append({"x": x, "y": None, "note": "steep: not read"})
                continue
            h = w * np.sqrt(1 + slope * slope)
            cand = cols.get(c, [])
            if not cand:
                out.append({"x": x, "y": None, "note": "no blue in this column"})
                continue
            a, b, kind = min(cand, key=lambda r: abs((r[0] + r[1]) / 2.0 - pred))
            if kind == "both":
                yc, half = (a + b) / 2.0, 2.0
            elif kind == "top":
                yc, half = a + h / 2.0, 2.5
            elif kind == "bottom":
                yc, half = b - h / 2.0, 2.5
            else:
                out.append({"x": x, "y": None, "note": "blue stroke wholly under red"})
                continue
            if abs(yc - pred) > h:
                out.append({"x": x, "y": None, "note": "blue run far from the neighbours' trend"})
                continue
            state = {"both": "blue stroke, both edges blue", "top": "blue upper edge (red below)",
                     "bottom": "blue lower edge (red above)"}[kind]
            wname = f"w {w:.0f} px"
            pad = ym + 1.0 + abs(slope) * (xm + abs(c - cx))
            lo, hi = yc - half - pad, yc + half + pad
            out.append(_entry(x, cx, yc, lo, hi, ya, yb, f"{state}; {wname}; x misfit {xm:.1f} px, y misfit {ym:.1f} px; "
                                                      f"axis offsets from 0: x {cal['x0_off']:.1f} px, y {cal['y0_off']:.1f} px"))
        return out
    # red dashed
    rcols = {k: _runs(R[:, k]) for k in range(R.shape[1])}
    rl = [b - a + 1 for v in rcols.values() for a, b in v]
    wr = float(np.percentile(rl, 20)) if rl else 10.0
    for x in at:
        cx = (x - xa) / xb
        c = int(round(cx))
        pts = [(k, (a + b) / 2.0) for k in range(c - 60, c + 61) if k != c for a, b in rcols.get(k, [])]
        if len(pts) < 10:
            out.append({"x": x, "y": None, "note": "too few red dashes nearby"})
            continue
        P, pred, slope, mis = _parabola(pts, cx)
        keep = [p for p in pts if abs(np.polyval(P, p[0]) - p[1]) <= 3 * wr]
        if len(keep) < 10:
            out.append({"x": x, "y": None, "note": "red dashes nearby do not fall on one curve"})
            continue
        P, pred, slope, mis = _parabola(keep, cx)
        if abs(slope) > 1.5:
            out.append({"x": x, "y": None, "note": "steep: not read"})
            continue
        h = wr * np.sqrt(1 + slope * slope)
        here = [(a, b) for a, b in rcols.get(c, []) if abs((a + b) / 2.0 - pred) <= h]
        if here:
            a, b = min(here, key=lambda r: abs((r[0] + r[1]) / 2.0 - pred))
            if b - a + 1 <= h + 4:
                yc, half, state = (a + b) / 2.0, 2.0, "red dash"
            else:
                yc, half, state = pred, (b - a + 1 - h) / 2.0 + 2.0, "red dash end or run longer than the line"
        else:
            yc, half, state = pred, 2.0 + mis, "gap between red dashes: parabola through the dashes"
        pad = ym + 1.0 + abs(slope) * (xm + abs(c - cx))
        out.append(_entry(x, cx, yc, yc - half - pad, yc + half + pad, ya, yb,
                          f"{state}; red width {wr:.0f} px; fit misfit {mis:.1f} px; x misfit {xm:.1f} px, "
                          f"y misfit {ym:.1f} px"))
    return out


def _entry(x, cx, yc, lo, hi, ya, yb, note):
    v, v1, v2 = ya + yb * yc, ya + yb * lo, ya + yb * hi
    return {"x": x, "y": float(v), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
            "px": [float(cx), float(yc)], "px_lo": float(lo), "px_hi": float(hi), "note": note}
