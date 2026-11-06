"""Shared reading code for Fig. 5 (PDF p. 6): input impedance of dog 71, modulus (top panel)
and phase (bottom panel): measured (filled squares), three-element windkessel (dotted line, as
the legend says) and four-element windkessel (solid line).

The figure is a scan, nearly black and white: ink is darker than 128 (of 255).

Calibration, all from the image:
- the y axis is the column with the most ink; it is broken in two vertical runs, one per panel;
- the y ticks point inwards (right of the y axis): short runs of ink 6-30 px right of it. In
  the modulus panel they are matched in order, top to bottom, to the printed labels
  1, 0.8, 0.6, 0.4, 0.2 and the x axis line to 0; in the phase panel to 0, -40, -80 and the x axis
  line to -120;
- the x ticks point inwards (above each x axis): short runs 6-30 px above it, matched to the
  printed labels 2, 4, ..., 12, and the y axis to 0. Both panels' ticks are fitted together.
A straight line is fitted to the marks of each axis; the largest misfit (px) widens every interval.

Markers: a binary opening with a square larger than the lines are thick keeps only the filled
squares; each is read at its centroid, with an interval of 3 px plus the calibration misfit.

Lines: after removing the squares, the ticks, the axes and the legend (top right of the modulus
panel), the ink is cut into connected pieces. A piece longer than 300 px is the solid line;
pieces shorter than 120 px, chained along the curve, are the dotted line. At a column the solid
line is read at the centre of its single run of ink; the interval is the run's half height (which
grows where the line is steep) plus 3 px plus the misfit. Where the solid line's run is thicker
than twice its usual thickness (it touches a square or the dotted line) the value is refused. The
dotted line is read at the centre of the dot covering the column, or interpolated between the
nearest dots either side (at most 60 px apart); a dotted reading that has solid ink within 25 px
is refused.
"""

import numpy as np
from scipy import ndimage

INK = 128


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    return a, b, mis


def calibrate(image):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < INK
    H, W = ink.shape
    cs = ink[:, : W // 3].sum(axis=0)
    ycols = np.flatnonzero(cs > 0.8 * cs.max())
    yl, yr = int(ycols.min()), int(ycols.max()) + 1
    yc = (yl + yr - 1) / 2.0
    vr = sorted([r for r in _runs(ink[:, int(yc)]) if r[1] - r[0] > 1000])
    mod_run, ph_run = vr[0], vr[1]
    # x axis of each panel: rows near the bottom of its y axis run where the ink spans > 2/3 of the width
    xaxes = []
    for run in (mod_run, ph_run):
        rows = [r for r in range(run[1] - 30, min(run[1] + 10, H)) if ink[r, yr:].sum() > 0.66 * (W - yr)]
        xaxes.append((min(rows), max(rows) + 1))
    # y ticks: short runs right of the y axis
    band = ink[:, yr + 6: yr + 30].all(axis=1)
    tk = [((a + b - 1) / 2.0) for a, b in _runs(band) if b - a < 20]
    mod_t = sorted(t for t in tk if mod_run[0] - 5 <= t < xaxes[0][0] - 5)
    ph_t = sorted(t for t in tk if ph_run[0] - 5 <= t < xaxes[1][0] - 5)
    if len(mod_t) != 5 or len(ph_t) != 3:
        raise RuntimeError(f"y ticks not found as expected: {mod_t} {ph_t}")
    mod_marks = list(zip(mod_t + [(xaxes[0][0] + xaxes[0][1] - 1) / 2.0], [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]))
    ph_marks = list(zip(ph_t + [(xaxes[1][0] + xaxes[1][1] - 1) / 2.0], [0.0, -40.0, -80.0, -120.0]))
    # x ticks: short runs above each x axis, right of the y axis
    xmarks = [(yc, 0.0)]
    for x0, _ in xaxes:
        b = ink[x0 - 30: x0 - 6, :].all(axis=0)
        t = [((a + c - 1) / 2.0) for a, c in _runs(b) if c - a < 20 and a > yr + 50]
        if len(t) != 6:
            raise RuntimeError(f"x ticks not found as expected: {t}")
        xmarks += list(zip(t, [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]))
    xend = max(c for a, c in _runs(ink[(xaxes[0][0] + xaxes[0][1]) // 2, :]) if a <= yr + 2)
    return dict(g=g, ink=ink, yl=yl, yr=yr, mod_run=mod_run, ph_run=ph_run, xaxes=xaxes, xend=xend,
                xmarks=xmarks, mod_marks=mod_marks, ph_marks=ph_marks)


def _box(cal, panel):
    """rows r0:r1, cols c0:c1 of the plot interior, without axes and ticks."""
    run = cal["mod_run"] if panel == "mod" else cal["ph_run"]
    xa = cal["xaxes"][0] if panel == "mod" else cal["xaxes"][1]
    return run[0], xa[0] - 60, cal["yr"] + 60, cal["xend"]


def markers(cal, panel):
    ink = cal["ink"]
    run = cal["mod_run"] if panel == "mod" else cal["ph_run"]
    xa = cal["xaxes"][0] if panel == "mod" else cal["xaxes"][1]
    m = np.zeros_like(ink)
    m[run[0]: xa[0], cal["yl"] - 40: cal["xend"]] = ink[run[0]: xa[0], cal["yl"] - 40: cal["xend"]]
    sq = ndimage.binary_opening(m, structure=np.ones((25, 25), bool))
    if panel == "mod":
        sq = _no_legend(cal, sq)
    lab, n = ndimage.label(sq)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        if len(rr) < 900:
            continue
        out.append(dict(col=float(cc.mean() + sl[1].start), row=float(rr.mean() + sl[0].start),
                        r0=sl[0].start, r1=sl[0].stop, c0=sl[1].start, c1=sl[1].stop))
    return sorted(out, key=lambda d: d["col"]), sq


def _no_legend(cal, m):
    """Blank the legend: the modulus panel above y = 0.6 and right of x = 3 Hz (no curve is there)."""
    ya, yb, _ = _fit(cal["mod_marks"])
    xa, xb, _ = _fit(cal["xmarks"])
    r = int((0.6 - ya) / yb)
    c = int((3.0 - xa) / xb)
    m = m.copy()
    m[:r, c:] = False
    return m


def pieces(cal, panel):
    ink = cal["ink"]
    r0, r1, c0, c1 = _box(cal, panel)
    _, sq = markers(cal, panel)
    sqd = ndimage.binary_dilation(sq, structure=np.ones((7, 7), bool))
    m = np.zeros_like(ink)
    m[r0:r1, c0:c1] = ink[r0:r1, c0:c1]
    m &= ~sqd
    if panel == "mod":
        m = _no_legend(cal, m)
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    ps = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        if len(rr) < 8:
            continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        ps.append(dict(rr=rr + sl[0].start, cc=cc + sl[1].start, length=float(np.hypot(h, w)),
                       c0=sl[1].start, c1=sl[1].stop))
    return ps


def _cols(ps):
    pts = {}
    for p in ps:
        for c in range(p["c0"], p["c1"]):
            rows = np.sort(p["rr"][p["cc"] == c])
            if len(rows) == 0:
                continue
            for a, b in _runs(np.isin(np.arange(rows.min(), rows.max() + 1), rows)):
                pts.setdefault(c, []).append((rows.min() + a, rows.min() + b))
    return pts


def _axes(cal, panel):
    xa, xb, xmis = _fit(cal["xmarks"])
    ya, yb, ymis = _fit(cal["mod_marks"] if panel == "mod" else cal["ph_marks"])
    return xa, xb, xmis, ya, yb, ymis


def read_markers(image, at, panel):
    cal = calibrate(image)
    xa, xb, xmis, ya, yb, ymis = _axes(cal, panel)
    ms, _ = markers(cal, panel)
    out = []
    for m in ms:
        e = 3.0 + ymis
        ex = 3.0 + xmis
        out.append({"x": xa + xb * m["col"], "y": ya + yb * m["row"], "lo": ya + yb * (m["row"] + e),
                    "hi": ya + yb * (m["row"] - e), "px": [m["col"], m["row"]], "px_lo": m["row"] - e,
                    "px_hi": m["row"] + e,
                    "note": f"square {m['c1'] - m['c0']}x{m['r1'] - m['r0']} px at its centroid; x read as "
                            f"{xa + xb * m['col']:.3f} Hz +- {abs(xb) * ex:.3f}"})
    return out


def read_solid(image, at, panel):
    cal = calibrate(image)
    xa, xb, xmis, ya, yb, ymis = _axes(cal, panel)
    ps = [p for p in pieces(cal, panel) if p["length"] > 300]
    pts = _cols(ps)
    th = np.median([b - a for v in pts.values() if len(v) == 1 for a, b in v])
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        runs = pts.get(c, [])
        if len(runs) != 1:
            out.append({"x": x, "y": None, "note": f"{len(runs)} runs of the solid line at this column"})
            continue
        a, b = runs[0]
        # steepness from the neighbouring columns
        nb = [np.mean(pts[k][0]) for k in (c - 10, c + 10) if len(pts.get(k, [])) == 1]
        slope = abs(nb[1] - nb[0]) / 20.0 if len(nb) == 2 else 0.0
        if (b - a) > 2 * th + 2 * slope * th + 4:
            out.append({"x": x, "y": None, "note": f"solid line {b - a} px tall here (usual {th:.0f}): it touches another mark"})
            continue
        # does any non-solid ink (dots, squares) touch this run? then it is not the solid line alone
        row = (a + b - 1) / 2.0
        e = (b - a) / 2.0 + 3.0 + ymis + slope * xmis
        out.append({"x": x, "y": ya + yb * row, "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
                    "px": [col, row], "px_lo": row - e, "px_hi": row + e,
                    "note": f"solid line, run {b - a} px"})
    return out


def read_dotted(image, at, panel):
    cal = calibrate(image)
    xa, xb, xmis, ya, yb, ymis = _axes(cal, panel)
    allp = pieces(cal, panel)
    solid = _cols([p for p in allp if p["length"] > 300])
    dots = [p for p in allp if p["length"] < 120]
    cen = sorted(((p["c0"] + p["c1"]) / 2.0, float(np.mean(p["rr"])), p) for p in dots)
    # keep dots that continue the chain: within 40 px (+ the local slope) of the line through their neighbours
    for _ in range(3):
        keep = []
        for i, (c, r, p) in enumerate(cen):
            if 0 < i < len(cen) - 1:
                cl, rl, _ = cen[i - 1]
                cr, rr_, _ = cen[i + 1]
                exp = rl + (rr_ - rl) * (c - cl) / (cr - cl) if cr != cl else (rl + rr_) / 2.0
                ok = abs(r - exp) <= 25 + 0.3 * abs(rr_ - rl)
            else:
                ok = True
            if ok:
                keep.append((c, r, p))
        if len(keep) == len(cen):
            break
        cen = keep
    dpts = _cols([p for _, _, p in cen])
    cols = np.array(sorted(dpts))
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        if len(dpts.get(c, [])) == 1:
            a, b = dpts[c][0]
            row, half, gap = (a + b - 1) / 2.0, (b - a) / 2.0, 0
        else:
            left, right = cols[cols < c], cols[cols > c]
            if len(left) == 0 or len(right) == 0:
                out.append({"x": x, "y": None, "note": "no dotted line here"})
                continue
            cl, cr = int(left[-1]), int(right[0])
            if cr - cl > 60 or len(dpts[cl]) != 1 or len(dpts[cr]) != 1:
                out.append({"x": x, "y": None, "note": f"dotted line not found within 30 px either side ({cr - cl} px gap)"})
                continue
            rl, rr_ = np.mean(dpts[cl][0]) - 0.5, np.mean(dpts[cr][0]) - 0.5
            w = (c - cl) / (cr - cl)
            row = (1 - w) * rl + w * rr_
            half = max(dpts[cl][0][1] - dpts[cl][0][0], dpts[cr][0][1] - dpts[cr][0][0]) / 2.0 + abs(rr_ - rl) / 2.0
            gap = cr - cl
        near = [r for k in range(c - 4, c + 5) for r in solid.get(k, []) if min(abs(r[0] - row), abs(r[1] - row)) < 25]
        if near:
            out.append({"x": x, "y": None, "note": "the solid line is within 25 px: the dotted line is not separable here"})
            continue
        e = half + 3.0 + ymis
        out.append({"x": x, "y": ya + yb * row, "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
                    "px": [col, row], "px_lo": row - e, "px_hi": row + e,
                    "note": f"interpolated across a {gap} px gap between dots" if gap else "on a dot"})
    return out
