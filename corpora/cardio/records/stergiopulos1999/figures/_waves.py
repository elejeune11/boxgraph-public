"""Shared reading code for the pressure and flow waves of Figs. 1, 3 and 4 (PDF pp. 3-5).

Each figure is a scan, nearly black and white (ink darker than 128). A crop holds one column of
framed panels stacked vertically; `CFG["panel"]` picks one, counted from the top.

Calibration, from the image:
- the frame: the left and right frame lines are the columns with the most ink; the panels are the
  long vertical runs of ink in the left frame line; a panel's top and bottom frame lines are the
  rows near its ends where ink spans most of the width;
- y ticks point inwards from the right frame line: the short runs of ink 6-22 px left of it. They
  are matched in order, top to bottom, to the printed labels `CFG["ylabels"]`; when `CFG["yframe"]`
  is true, the top and bottom frame lines carry the first and last label (the printed label sits
  level with them);
- x ticks point inwards from the bottom frame line: short runs 6-22 px above it, matched left to
  right to `CFG["xlabels"]`; when `CFG["xframe"]` is true the left and right frame lines carry the
  first and last label.
The labels are those printed on the figure (for an upper panel with no time labels of its own,
those printed under the column, whose tick marks fall on the same columns). A straight line is
fitted to each axis' marks; the largest misfit (px) widens every interval.

Lines: within the panel interior (frame lines and ticks excluded, and the legend box
`CFG["legend"]` in axis units blanked), a binary opening with a 15 px disk keeps only the thick
line (the measured wave) and removes the thin (about 12 px) line of a windkessel fit and the dots
of a dotted line.
- thick: read at the centre of the one run of the opened mask in the column; the interval is half
  the run + 3 px + misfit (the run is taller where the line is steep, which widens it). A run more
  than twice the usual height (plus steepness) means another line lies along it: refused.
- thin: the ink left after removing the thick line (dilated by 6 px) and pieces under 300 px of
  ink; read at the centre of its one run in the column; refused where it is hidden under the thick
  line, where it has several runs, or where thick ink lies within 6 px of it.
- dotted: pieces shorter than 90 px (diagonal) of the ink left after removing the thick line,
  chained along the curve; read at the dot covering the column or interpolated between the
  nearest dots (at most 70 px apart); refused where thin-line ink lies within 25 px.
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
    return a, b, float(np.max(np.abs((v - (a + b * p)) / b)))


def calibrate(image, cfg):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < INK
    H, W = ink.shape
    # panels: consecutive pairs of long horizontal frame lines (top, bottom)
    rs = ink.sum(axis=1)
    lines = _runs(rs > 0.5 * rs.max())
    pairs = [(lines[i], lines[i + 1]) for i in range(0, len(lines) - 1, 2)]
    ft, fb = pairs[cfg["panel"]]
    # side frame lines: the columns inked over most of this panel's height
    cs = ink[ft[1]: fb[0], :].sum(axis=0)
    groups = _runs(cs > 0.8 * (fb[0] - ft[1]))
    (ll, lr), (rl, rr) = groups[0], groups[-1]
    band = ink[ft[1] + 15: fb[0] - 15, rl - 22: rl - 6].all(axis=1)
    yt = [(a + b - 1) / 2.0 + ft[1] + 15 for a, b in _runs(band) if b - a < 25]
    if cfg["yframe"]:
        yt = [(ft[0] + ft[1] - 1) / 2.0] + yt + [(fb[0] + fb[1] - 1) / 2.0]
    if len(yt) != len(cfg["ylabels"]):
        raise RuntimeError(f"y ticks: found {len(yt)} for labels {cfg['ylabels']}: {yt}")
    ymarks = list(zip(yt, cfg["ylabels"]))
    bandx = ink[fb[0] - 22: fb[0] - 6, lr + 15: rl - 15].all(axis=0)
    xt = [(a + b - 1) / 2.0 + lr + 15 for a, b in _runs(bandx) if b - a < 25]
    if cfg["xframe"]:
        xt = [(ll + lr - 1) / 2.0] + xt + [(rl + rr - 1) / 2.0]
    if len(xt) != len(cfg["xlabels"]):
        raise RuntimeError(f"x ticks: found {len(xt)} for labels {cfg['xlabels']}: {xt}")
    xmarks = list(zip(xt, cfg["xlabels"]))
    return dict(ink=ink, lr=lr, rl=rl, ft=ft, fb=fb, xmarks=xmarks, ymarks=ymarks)


def _masks(cal, cfg):
    ink = cal["ink"]
    xa, xb, xmis = _fit(cal["xmarks"])
    ya, yb, ymis = _fit(cal["ymarks"])
    r0, r1 = cal["ft"][1] + 70, cal["fb"][0] - 70
    c0, c1 = cal["lr"] + 45, cal["rl"] - 45
    m = np.zeros_like(ink)
    m[r0:r1, c0:c1] = ink[r0:r1, c0:c1]
    if cfg.get("legend"):
        x0, x1, y0, y1 = cfg["legend"]
        cc = sorted(int((v - xa) / xb) for v in (x0, x1))
        rr = sorted(int((v - ya) / yb) for v in (y0, y1))
        m[max(rr[0], 0):rr[1], max(cc[0], 0):cc[1]] = False
    yy, xx = np.mgrid[-7:8, -7:8]
    disk = (xx ** 2 + yy ** 2) <= 7.5 ** 2
    thick = ndimage.binary_opening(m, structure=disk)
    rest = m & ~ndimage.binary_dilation(thick, structure=np.ones((13, 13), bool))
    lab, n = ndimage.label(rest, structure=np.ones((3, 3), bool))
    pieces = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rr_, cc_ = np.nonzero(lab[sl] == i)
        pieces.append(dict(rr=rr_ + sl[0].start, cc=cc_ + sl[1].start, n=len(rr_),
                           length=float(np.hypot(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start)),
                           c0=sl[1].start, c1=sl[1].stop))
    return thick, pieces, (xa, xb, xmis, ya, yb, ymis)


def _cols(ps):
    pts = {}
    for p in ps:
        order = np.lexsort((p["rr"], p["cc"]))
        cc, rr = p["cc"][order], p["rr"][order]
        cuts = np.flatnonzero(np.diff(cc)) + 1
        for ccol, rows in zip(np.split(cc, cuts), np.split(rr, cuts)):
            # runs of consecutive rows
            brk = np.flatnonzero(np.diff(rows) > 1) + 1
            for seg in np.split(rows, brk):
                pts.setdefault(int(ccol[0]), []).append((int(seg[0]), int(seg[-1]) + 1))
    return pts


def _value(x, row, e, ax, col, note):
    xa, xb, xmis, ya, yb, ymis = ax
    return {"x": x, "y": ya + yb * row, "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
            "px": [col, row], "px_lo": row - e, "px_hi": row + e, "note": note}


def read_thick(image, at, cfg):
    cal = calibrate(image, cfg)
    thick, _, ax = _masks(cal, cfg)
    xa, xb, xmis, ya, yb, ymis = ax
    allruns = [b - a for c in range(thick.shape[1]) for a, b in _runs(thick[:, c]) if thick[:, c].any()]
    usual = float(np.median(allruns)) if allruns else 18.0
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        rs = _runs(thick[:, c])
        if len(rs) != 1:
            out.append({"x": x, "y": None, "note": f"{len(rs)} runs of the thick line at this column"})
            continue
        a, b = rs[0]
        nb = [np.mean(_runs(thick[:, k])[0]) for k in (c - 10, c + 10) if len(_runs(thick[:, k])) == 1]
        slope = abs(nb[1] - nb[0]) / 20.0 if len(nb) == 2 else 0.0
        if (b - a) > 2 * usual * np.sqrt(1 + slope ** 2) + 4:
            out.append({"x": x, "y": None, "note": f"thick run {b - a} px (usual {usual:.0f}): another line lies along it"})
            continue
        row = (a + b - 1) / 2.0
        e = (b - a) / 2.0 + 3.0 + ymis + slope * xmis
        out.append(_value(x, row, e, ax, col, f"thick line, run {b - a} px"))
    return out


def read_thin(image, at, cfg):
    cal = calibrate(image, cfg)
    thick, pieces, ax = _masks(cal, cfg)
    xa, xb, xmis, ya, yb, ymis = ax
    pts = _cols([p for p in pieces if p["n"] >= 300])
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        rs = pts.get(c, [])
        if len(rs) != 1:
            out.append({"x": x, "y": None, "note": f"{len(rs)} runs of the thin line here (hidden under the thick line or crossed)"})
            continue
        a, b = rs[0]
        near = thick[max(a - 6, 0): b + 6, c - 3: c + 4].any()
        if near:
            out.append({"x": x, "y": None, "note": "the thick line is within 6 px: the thin line is not separable here"})
            continue
        nb = [np.mean(pts[k][0]) for k in (c - 10, c + 10) if len(pts.get(k, [])) == 1]
        slope = abs(nb[1] - nb[0]) / 20.0 if len(nb) == 2 else 0.0
        row = (a + b - 1) / 2.0
        e = (b - a) / 2.0 + 3.0 + ymis + slope * xmis
        out.append(_value(x, row, e, ax, col, f"thin line, run {b - a} px"))
    return out


def read_dotted(image, at, cfg):
    cal = calibrate(image, cfg)
    thick, pieces, ax = _masks(cal, cfg)
    xa, xb, xmis, ya, yb, ymis = ax
    thin = _cols([p for p in pieces if p["n"] >= 300])
    dots = [p for p in pieces if p["n"] < 300 and p["n"] >= 15]
    cen = sorted(((p["c0"] + p["c1"]) / 2.0, float(np.mean(p["rr"])), i) for i, p in enumerate(dots))
    for _ in range(3):
        keep = []
        for i, (c, r, j) in enumerate(cen):
            if 0 < i < len(cen) - 1:
                cl, rl, _ = cen[i - 1]
                cr, rr_, _ = cen[i + 1]
                exp = rl + (rr_ - rl) * (c - cl) / (cr - cl) if cr != cl else (rl + rr_) / 2.0
                ok = abs(r - exp) <= 25 + 0.3 * abs(rr_ - rl)
            else:
                ok = True
            if ok:
                keep.append((c, r, j))
        if len(keep) == len(cen):
            break
        cen = keep
    dpts = _cols([dots[j] for _, _, j in cen])
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
            if cr - cl > 70 or len(dpts[cl]) != 1 or len(dpts[cr]) != 1:
                out.append({"x": x, "y": None, "note": f"dotted line not found within 35 px either side ({cr - cl} px gap)"})
                continue
            rl, rr_ = np.mean(dpts[cl][0]) - 0.5, np.mean(dpts[cr][0]) - 0.5
            w = (c - cl) / (cr - cl)
            row = (1 - w) * rl + w * rr_
            half = max(dpts[cl][0][1] - dpts[cl][0][0], dpts[cr][0][1] - dpts[cr][0][0]) / 2.0 + abs(rr_ - rl) / 2.0
            gap = cr - cl
        near = [r for k in range(c - 4, c + 5) for r in thin.get(k, []) if min(abs(r[0] - row), abs(r[1] - row)) < 25]
        if near or thick[max(int(row) - 25, 0): int(row) + 26, c - 4: c + 5].any():
            out.append({"x": x, "y": None, "note": "another line within 25 px: the dotted line is not separable here"})
            continue
        e = half + 3.0 + ymis
        out.append(_value(x, row, e, ax, col, f"interpolated across a {gap} px gap between dots" if gap else "on a dot"))
    return out
