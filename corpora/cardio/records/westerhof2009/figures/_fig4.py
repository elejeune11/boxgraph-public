"""Shared reading code for Fig. 4 (p. 3): measured aortic input impedance (grey line) with the
impedances of the two-element (dotted), three-element (dashed) and four-element (solid)
windkessels; modulus panel on top, phase panel below.

The crop holds both panels. The phase panel has no frequency tick labels of its own: it shares
the frequency axis of the modulus panel (same origin column, same right end of the curves), so
both panels are calibrated in x from the modulus panel's tick marks (labels 0, 2, ..., 12).
The y ticks are matched to the printed labels 0, 0.2, ..., 1.0 (modulus) and 0, -40, -80 (phase).

The figure is vector art: black ink is darker than 100 (of 255), the grey line is 130-210.
Black curves are told apart by the shape of their pieces: the solid line is one long piece,
the dashed line pieces 40-160 px long, the dotted line pieces shorter than 40 px. Where the
curves overlap (at low frequency) the pieces merge and the reading is refused.
"""

import numpy as np
from scipy import ndimage


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    return a, b, float(np.max(np.abs((v - a) / b - p)))


def _pick_regular(cands, labels):
    """The len(labels) candidates whose spacing is most even, paired with the labels in order."""
    import itertools
    n = len(labels)
    best = None
    for sub in itertools.combinations(sorted(cands), n):
        d = np.diff(sub)
        score = float(np.ptp(d)) / float(np.mean(d))
        if best is None or score < best[0]:
            best = (score, sub)
    return list(zip(best[1], labels))


def calibrate(image):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < 100
    H, W = ink.shape
    # the y axes: the column with the most ink in the left third; split into two vertical runs
    cs = ink[:, : W // 3].sum(axis=0)
    ycol = int(np.argmax(cs))
    ycols = np.flatnonzero(cs > 0.8 * cs[ycol])
    yl, yr = int(ycols.min()), int(ycols.max()) + 1
    col = ink[:, ycol]
    vruns = sorted([r for r in _runs(col) if r[1] - r[0] > 300], key=lambda r: r[0])
    mod_run, ph_run = vruns[0], vruns[-1]
    # x axis of the modulus panel: the longest horizontal ink row near the bottom of its y axis
    rs = ink[mod_run[1] - 40: mod_run[1] + 10, yr:].sum(axis=1)
    xrow0 = mod_run[1] - 40 + int(np.argmax(rs))
    xrows = [r for r in range(mod_run[1] - 40, mod_run[1] + 10) if ink[r, yr:].sum() > 0.8 * rs.max()]
    xt, xb = min(xrows), max(xrows) + 1
    xline = ink[(xt + xb) // 2, :]
    xend = max(b for a, b in _runs(xline) if a <= yr + 2)
    # x ticks: short vertical marks hanging below the x axis
    probe = ink[xb + 4: xb + 24, :].all(axis=0)
    xc = [(a + b) / 2.0 for a, b in _runs(probe) if 4 <= b - a < 40]
    xmarks = _pick_regular(xc, [0, 2, 4, 6, 8, 10, 12])
    # y ticks: short horizontal marks left of each y axis
    probe = ink[:, yl - 22: yl - 4].all(axis=1)
    yc = [(a + b) / 2.0 for a, b in _runs(probe) if b - a < 40]
    ymod = [c for c in yc if mod_run[0] - 10 <= c <= mod_run[1] + 10]
    # the curves run along the phase axis near 0 Hz, so its top is found from the 0 tick instead
    yph = [c for c in yc if xb + 200 <= c <= ph_run[1] + 10]
    mod_marks = _pick_regular(ymod, [1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
    ph_marks = _pick_regular(yph, [0.0, -40.0, -80.0])
    ph_run = (int(ph_marks[0][0]) - 60, ph_run[1])
    # the phase panel's zero line
    zr = [r for r in range(ph_run[0], ph_run[0] + 200) if ink[r, yr + 50: yr + 1200].mean() > 0.9]
    return dict(g=g, ink=ink, yl=yl, yr=yr, mod_run=mod_run, ph_run=ph_run, xt=xt, xb=xb, xrow0=xrow0, xend=xend,
                xmarks=xmarks, mod_marks=mod_marks, ph_marks=ph_marks,
                zero=(min(zr), max(zr) + 1) if zr else None)


def _panel_box(cal, panel):
    """(r0, r1, c0, c1) of the plot interior, without the axes. The right edge is the end of the
    modulus panel's x axis line (the curves of both panels end there; the Zc arrow is beyond it)."""
    c0 = cal["yr"] + 8
    c1 = cal["xend"] + 4
    if panel == "mod":
        return cal["mod_run"][0] - 20, cal["xt"] - 6, c0, c1
    return cal["ph_run"][0] - 20, cal["ph_run"][1] + 40, c0, c1


def _legend_mask(cal, m):
    """Blank the legend box of the modulus panel: rows above y = 0.35, right of x = 1.8."""
    ya, yb, _ = _fit(cal["mod_marks"])
    xa, xb, _ = _fit(cal["xmarks"])
    r = int((0.35 - ya) / yb)
    c = int((1.8 - xa) / xb)
    m[:r, c:] = False
    return m


def black_pieces(cal, panel):
    ink = cal["ink"].copy()
    r0, r1, c0, c1 = _panel_box(cal, panel)
    m = np.zeros_like(ink)
    m[r0:r1, c0:c1] = ink[r0:r1, c0:c1]
    if panel == "mod":
        m = _legend_mask(cal, m)
    else:
        z0, z1 = cal["zero"]
        m[z0 - 3: z1 + 3, :] = False
    lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    pieces = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        if len(rr) < 30:
            continue
        rr = rr + sl[0].start
        cc = cc + sl[1].start
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        length = float(np.hypot(h, w))
        pieces.append(dict(lab=i, rr=rr, cc=cc, length=length, c0=sl[1].start, c1=sl[1].stop,
                           r0=sl[0].start, r1=sl[0].stop))
    return pieces, lab


def classify(p):
    if p["length"] > 260:
        return "solid"
    if p["length"] >= 52:
        return "dashed"
    return "dotted"


def chain(pieces, max_dev=40.0):
    """Drop pieces of a broken (dashed or dotted) line that do not continue it: a piece whose
    centre lies more than max_dev px from the line through its two neighbours (or, at an end,
    from its one neighbour) is a fragment of another line that happens to have the same size."""
    ps = sorted(pieces, key=lambda p: (p["c0"] + p["c1"]) / 2.0)
    for _ in range(3):
        keep = []
        cen = [((p["c0"] + p["c1"]) / 2.0, float(np.mean(p["rr"]))) for p in ps]
        for i, p in enumerate(ps):
            c, r = cen[i]
            if 0 < i < len(ps) - 1:
                (cl, rl), (cr, rr) = cen[i - 1], cen[i + 1]
                exp = rl + (rr - rl) * (c - cl) / (cr - cl) if cr != cl else (rl + rr) / 2
                ok = abs(r - exp) <= max_dev + 0.25 * abs(rr - rl) or (abs(r - rl) <= max_dev and abs(c - cl) < 120)
            elif len(ps) > 2:
                # an end piece: extrapolate from its two neighbours
                (c1, r1), (c2, r2) = (cen[1], cen[2]) if i == 0 else (cen[i - 1], cen[i - 2])
                exp = r1 + (r1 - r2) * (c - c1) / (c1 - c2) if c1 != c2 else r1
                ok = abs(r - exp) <= max_dev + 0.5 * abs(r1 - r2)
            else:
                ok = True
            if ok:
                keep.append(p)
        if len(keep) == len(ps):
            break
        ps = keep
    return ps


def centre_line(pieces):
    """(column, centre row, half-thickness) for each column covered by these pieces."""
    pts = {}
    for p in pieces:
        for c in range(p["c0"], p["c1"]):
            rows = p["rr"][p["cc"] == c]
            if len(rows) == 0:
                continue
            runs = _runs(np.isin(np.arange(rows.min(), rows.max() + 1), rows))
            # one run per column for a line piece; a piece that is a blob gives several
            a, b = max(runs, key=lambda r: r[1] - r[0])
            pts.setdefault(c, []).append(((a + b) / 2.0 + rows.min(), (b - a) / 2.0))
    return pts


def grey_mask(cal, panel):
    g = cal["g"]
    r0, r1, c0, c1 = _panel_box(cal, panel)
    m = np.zeros(g.shape, bool)
    m[r0:r1, c0:c1] = (g[r0:r1, c0:c1] > 130) & (g[r0:r1, c0:c1] < 210)
    m = ndimage.binary_opening(m, structure=np.ones((9, 9), bool))
    if panel == "mod":
        m = _legend_mask(cal, m)
    return m


def read_grey(image, at, panel):
    cal = calibrate(image)
    xa, xb, xmis = _fit(cal["xmarks"])
    marks = cal["mod_marks"] if panel == "mod" else cal["ph_marks"]
    ya, yb, ymis = _fit(marks)
    m = grey_mask(cal, panel)
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        runs = _runs(m[:, c])
        note = ""
        if not runs and panel == "ph" and cal["zero"]:
            # the grey line can run along the black zero line, which covers its middle
            z0, z1 = cal["zero"]
            raw = (cal["g"][z0 - 20: z1 + 20, c] > 130) & (cal["g"][z0 - 20: z1 + 20, c] < 210)
            rows = np.flatnonzero(raw) + z0 - 20
            if len(rows) >= 4:
                a, b = min(rows.min(), z0), max(rows.max() + 1, z1)
                row = (a + b) / 2.0
                e = (b - a) / 2.0 + ymis
                out.append({"x": x, "y": ya + yb * row, "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
                            "px": [col, row], "px_lo": row - e, "px_hi": row + e,
                            "note": "grey line runs along the zero line; its edges show either side, centre taken mid-way"})
                continue
        if len(runs) == 1:
            a, b = runs[0]
        else:
            # hidden under a black line or absent: interpolate between the nearest columns either side
            found = {}
            for d in range(1, 41):
                for s in (-1, 1):
                    rr = _runs(m[:, c + s * d])
                    if len(rr) == 1 and s not in found:
                        found[s] = (d, rr[0])
            if len(runs) > 1 or len(found) < 2:
                out.append({"x": x, "y": None, "note": f"grey line not found alone at this frequency ({len(runs)} runs)"})
                continue
            (dl, (al, bl)), (dr, (ar, br)) = found[-1], found[1]
            wl, wr = dr / (dl + dr), dl / (dl + dr)
            a, b = wl * al + wr * ar, wl * bl + wr * br
            note = f"grey line hidden at this column; interpolated over {dl + dr} px"
        row = (a + b) / 2.0
        # steepness: the change of centre row over +-6 columns widens the interval
        nb = []
        for d in (-6, 6):
            rr = _runs(m[:, c + d])
            if len(rr) == 1:
                nb.append((rr[0][0] + rr[0][1]) / 2.0)
        slope = max([abs(v - row) for v in nb], default=0.0)
        e = 3.0 + ymis + xmis * slope / 6.0 + (slope if note else 0.0)
        out.append({"x": x, "y": ya + yb * row, "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
                    "px": [col, row], "px_lo": row - e, "px_hi": row + e,
                    "note": (note + f"; line {b - a:.0f} px thick").strip("; ")})
    return out


def read_black(image, at, panel, style):
    cal = calibrate(image)
    xa, xb, xmis = _fit(cal["xmarks"])
    marks = cal["mod_marks"] if panel == "mod" else cal["ph_marks"]
    ya, yb, ymis = _fit(marks)
    pieces, lab = black_pieces(cal, panel)
    mine = [p for p in pieces if classify(p) == style]
    if style != "solid":
        mine = chain(mine)
    pts = centre_line(mine)
    cols = np.array(sorted(pts))
    # typical half-thickness of this line where it runs flat; thicker columns are merged lines
    halves = np.array([v[0][1] for v in pts.values() if len(v) == 1])
    typical = float(np.median(halves)) if len(halves) else 8.0
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        if c in pts and len(pts[c]) == 1:
            row, half = pts[c][0]
            gap = 0
        else:
            left = cols[cols < c]
            right = cols[cols > c]
            if len(left) == 0 or len(right) == 0 or (c in pts and len(pts[c]) > 1):
                out.append({"x": x, "y": None, "note": f"no single {style} line at this frequency"})
                continue
            cl, cr = int(left[-1]), int(right[0])
            if cr - cl > 90 or len(pts[cl]) > 1 or len(pts[cr]) > 1:
                out.append({"x": x, "y": None, "note": f"{style} line not found within 45 px either side"})
                continue
            (rl, hl), (rr_, hr) = pts[cl][0], pts[cr][0]
            w = (c - cl) / (cr - cl)
            row = (1 - w) * rl + w * rr_
            half = max(hl, hr)
            gap = cr - cl
        # are other black pieces (any style) touching this column within 2 line widths? then refuse
        nb = [pts[k][0][0] for k in (c - 8, c + 8) if k in pts and len(pts[k]) == 1]
        slope = abs(nb[1] - nb[0]) / 16.0 if len(nb) == 2 else 0.0
        perp = half / np.sqrt(1.0 + slope ** 2)
        if perp > 1.6 * typical + 2 and not gap:
            out.append({"x": x, "y": None, "note": f"the {style} line is {2 * perp:.0f} px thick here (typically {2 * typical:.0f}): it touches another line"})
            continue
        near = []
        for p in pieces:
            if classify(p) == style:
                continue
            rows = p["rr"][np.abs(p["cc"] - c) <= 3]
            # on a piece of its own the line is separate unless another piece reaches its edge;
            # across a gap, another line nearby could be the one bridged, so keep a wider margin
            margin = (2 * max(typical, 6) + 6) if gap else (half + 4)
            if len(rows) and np.min(np.abs(rows - row)) < margin:
                near.append(p)
        if near:
            out.append({"x": x, "y": None, "note": f"another black line within {4 * max(half, 6):.0f} px; the {style} line is not separable here"})
            continue
        # the piece's slope near c widens the interval when the centre was interpolated over a gap
        e = 3.0 + ymis + xmis * slope + (0.15 * gap if gap else 0.0)
        out.append({"x": x, "y": ya + yb * row, "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
                    "px": [col, row], "px_lo": row - e, "px_hi": row + e,
                    "note": (f"interpolated across a {gap} px gap between {style} pieces" if gap else f"on a {style} piece")})
    return out
