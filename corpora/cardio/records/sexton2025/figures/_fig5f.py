"""Shared reading code for Fig. 5F (PDF p. 6): normalized flow q/q_in in three branches (x = 1 Bottom,
blue; 2 Middle, red; 3 Top, green). Each branch shows three PIV measurements (open circle, square,
triangle), an error bar (+-1 SD, caption), the CFD value of that branch (grey "+") and the averaged CFD
value (grey dashed line). The figure is an embedded raster image; colours are noisy.

Calibration: the plot frame is the long dark lines; the y ticks point out of the left side. Their rows
are matched, from the top, to the printed labels 0.7, 0.6, ..., 0.0 (the last one at the x axis); a
straight line is fitted, misfit widens every interval. The branch columns are the three x ticks below
the frame, numbered from the left.

Branch colour masks: blue B > R+50 and B > G+30; red R > G+60 and R > B+60; green G > R+40 and
G > B+5; grey: R, G, B within 18 of each other and 110-200 (the inset drawing is darker, ~70-100).

Error bar: the stem is the column of the band (+-80 px about the branch tick) with the most branch
colour. Its caps are the rows where the coloured run through the stem is 40-80 px wide and 6-16 rows
thick, away from the markers' own wide edges; where a cap coincides with a marker edge (Middle: the
upper cap lies on the triangle's base), the reading says so and its interval covers the edge. The
value reported is the bar's midpoint (the mean of the three measurements), with the two caps as the
bar ends.

Markers: with the stem's columns (+-6) removed, the branch-colour mask falls into left and right
halves of each marker. A marker is a pair of halves of at least 40 rows; its value is the centre of its
row extent. Shapes: a square half has a straight outer side (its outermost column holds for most
rows), a triangle half widens downwards (outermost at its base), a circle half is widest in the middle.
Where two markers overlap (Bottom: square and triangle), the reading covers the merged extent.
"""

import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

LABELS = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
COLOURS = {1: "blue", 2: "red", 3: "green"}


def _masks(image):
    im = image[..., :3].astype(int)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    return {
        "blue": (B > R + 50) & (B > G + 30),
        "red": (R > G + 60) & (R > B + 60),
        "green": (G > R + 40) & (G > B + 5),
        "grey": (abs(R - G) < 18) & (abs(G - B) < 18) & (R > 110) & (R < 200),
    }


def calibrate(image):
    rows, cols = C.frame(image, 110, 0.5)
    left = cols[0]
    bottom = rows[-1]
    yt = C.ticks_on_vertical(image, left[1], left[2], "out", 8, rows[0][1] - 10, bottom[2] + 10)
    yt = [t[0] for t in yt]
    if len(yt) != len(LABELS):
        raise RuntimeError(f"expected {len(LABELS)} y ticks, found {yt}")
    xt = C.ticks_on_horizontal(image, bottom[1], bottom[2], "out", 8, left[2] + 5, cols[-1][1] - 5)
    xt = [t[0] for t in xt]
    if len(xt) != 3:
        raise RuntimeError(f"expected 3 x ticks, found {xt}")
    return C.Axis(yt, LABELS), xt, (rows[0][2] + 2, bottom[1] - 2)


def _stem(mask, tick):
    c0 = int(tick) - 80
    return c0 + int(np.argmax(mask[:, c0:c0 + 160].sum(axis=0)))


def _width_through(mask, r, c):
    if not (mask[r, c] or mask[r, c - 1] or mask[r, c + 1]):
        return 0
    lo = c
    while mask[r, lo - 1]:
        lo -= 1
    hi = c
    while mask[r, hi + 1]:
        hi += 1
    return hi - lo + 1


def _stem_width(m, stem, top, bot):
    ws = [_width_through(m, r, stem) for r in range(top, bot)]
    ws = [w for w in ws if 0 < w < 20]
    return int(np.median(ws)) if ws else 8


def _end_has_ink(m, r, c):
    return bool(m[max(r - 2, 0): r + 3, max(c - 3, 0): c + 4].any())


def _wide_groups(m, stem, top, bot):
    """Groups of rows where the coloured run through the stem is 40-90 px wide: caps and the
    horizontal edges of markers. For each: (centre row, first, last, free) where free means nothing
    coloured continues vertically from the run's two ends, 8 rows above and below (a cap)."""
    wide = []
    ends = {}
    for r in range(top, bot):
        w = _width_through(m, r, stem)
        if 40 <= w <= 90:
            wide.append(r)
            lo = stem
            while m[r, lo - 1]:
                lo -= 1
            ends[r] = (lo, lo + w - 1)
    out = []
    for c, a, b in C.merge(wide, gap=1):
        lo = int(np.median([ends[r][0] for r in range(a, b + 1) if r in ends]))
        hi = int(np.median([ends[r][1] for r in range(a, b + 1) if r in ends]))
        # caps are narrower (about 50-66 px here) than the markers' straight edges (70-76 px)
        width = float(np.median([ends[r][1] - ends[r][0] + 1 for r in range(a, b + 1) if r in ends]))
        out.append((c, a, b, width <= CAP_MAX))
    return out


CAP_MAX = 67  # px at 1200 dpi: the widest a cap's run is; square edges and triangle bases are 70-76


def _structure(image, x):
    ax, xt, (top, bot) = calibrate(image)
    masks = _masks(image)
    m = masks[COLOURS[x]]
    stem = _stem(m, xt[x - 1])
    sw = _stem_width(m, stem, top, bot)
    groups = _wide_groups(m, stem, top, bot)
    return ax, xt, top, bot, masks, m, stem, sw, groups


def _marker_halves(m, stem, sw, top, bot, cut_rows):
    mm = m.copy()
    mm[:, : stem - 90] = False
    mm[:, stem + 90:] = False
    mm[:, stem - sw // 2 - 3: stem + sw // 2 + 4] = False
    mm[: top] = False
    mm[bot:] = False
    for a, b in cut_rows:
        mm[a - 1: b + 2] = False
    lab, _ = ndi.label(mm)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab)):
        sub = lab[sl] == i + 1
        if sub.sum() < 100 or sl[0].stop - sl[0].start < 20:
            continue
        out.append(dict(r0=sl[0].start, r1=sl[0].stop, side="L" if sl[1].stop <= stem else "R", sub=sub))
    return out


def _shape(h):
    """square / triangle / circle of one marker half, from its outer side: a square's holds for most
    rows; a triangle's is outermost at the base; a circle's in the middle."""
    sub = h["sub"]
    outer = []
    for r in range(sub.shape[0]):
        cs = np.flatnonzero(sub[r])
        if len(cs):
            outer.append(-cs.min() if h["side"] == "L" else cs.max())
    outer = np.array(outer, float)
    held = float(np.mean(outer >= outer.max() - 3))
    where = float(np.argmax(outer)) / max(len(outer) - 1, 1)
    if held > 0.6:
        return "square"
    if where > 0.75:
        return "triangle"
    return "circle"


def read_marker(image, at, shape):
    """One marker shape in each branch. Free caps are cut out of the mask first (they join markers);
    a marker is a left and a right half with overlapping rows, both of the same shape and up to 90 rows
    tall. A half cut by a cap (its top or bottom on a cut row) is placed from its uncut end and the
    marker height of an uncut marker of the same shape in the figure. Where two markers overlap and
    cannot be told apart, the reading covers their merged extent."""
    allx = {}
    for x in (1, 2, 3):
        ax, xt, top, bot, masks, m, stem, sw, groups = _structure(image, x)
        cuts = [(a, b) for c, a, b, free in groups if free]
        hs = _marker_halves(m, stem, sw, top, bot, cuts)
        pairs = []
        for L in [h for h in hs if h["side"] == "L"]:
            for R in [h for h in hs if h["side"] == "R"]:
                ov = min(L["r1"], R["r1"]) - max(L["r0"], R["r0"])
                if ov > 0.5 * min(L["r1"] - L["r0"], R["r1"] - R["r0"]):
                    r0, r1 = min(L["r0"], R["r0"]), max(L["r1"], R["r1"])
                    cut = any(abs(r0 - (b + 2)) <= 2 or abs(r1 - (a - 1)) <= 2 for a, b in cuts)
                    pairs.append(dict(r0=r0, r1=r1, shapes={_shape(L), _shape(R)}, cut=cut, cuts=cuts))
        allx[x] = (ax, stem, pairs)
    heights = {}
    for x, (_, _, pairs) in allx.items():
        for p in pairs:
            if len(p["shapes"]) == 1 and not p["cut"] and p["r1"] - p["r0"] <= 90:
                heights.setdefault(next(iter(p["shapes"])), []).append(p["r1"] - p["r0"])
    out = []
    for xv in at:
        x = int(round(float(xv)))
        ax, stem, pairs = allx[x]
        mine = [p for p in pairs if p["shapes"] == {shape} and p["r1"] - p["r0"] <= 90]
        merged = [p for p in pairs if p["r1"] - p["r0"] > 90 or len(p["shapes"]) > 1]
        if mine:
            p = mine[0]
            r0, r1 = p["r0"], p["r1"]
            note = f"{shape} rows {r0}-{r1}"
            half = 3.0
            if p["cut"] and shape in heights:
                hgt = float(np.median(heights[shape]))
                if any(abs(r0 - (b + 2)) <= 2 for a, b in p["cuts"]):
                    r0 = r1 - hgt
                else:
                    r1 = r0 + hgt
                half = 6.0
                note += f"; cut by a cap, placed from its uncut end with the height {hgt:.0f} px of the figure's uncut {shape}s"
            c = (r0 + r1 - 1) / 2.0
            lo, hi = ax.interval(c, half)
            out.append({"x": x, "y": ax.val(c), "lo": lo, "hi": hi, "px": [float(stem), c], "note": note})
        elif merged and shape in ("square", "triangle"):
            p = merged[0]
            r0, r1 = p["r0"], p["r1"]
            c = (r0 + r1) / 2.0
            half = max((r1 - r0) / 2.0 - 30, 4.0)
            lo, hi = ax.interval(c, half)
            out.append({"x": x, "y": ax.val(c), "lo": lo, "hi": hi, "px": [float(stem), c],
                        "px_lo": c + half, "px_hi": c - half,
                        "note": f"overlapping markers (rows {r0}-{r1}, shapes read {sorted(p['shapes'])}); the value is "
                                f"the merged extent's centre and the interval covers a marker centre anywhere in it"})
        else:
            out.append({"x": x, "y": None, "note": f"no {shape} marker found"})
    return out


def read_errorbar(image, at):
    """Error bar ends: the topmost and bottommost free caps on the stem. Where an end has no free cap
    (it lies on a marker's edge), the marker edge nearest the stem's end is taken and the interval of that
    end covers the edge's rows plus 4 px. The value is the midpoint of the two ends (the mean)."""
    out = []
    for xv in at:
        x = int(round(float(xv)))
        ax, xt, top, bot, masks, m, stem, sw, groups = _structure(image, x)
        # stem extent: the stem column (+-2) in the branch colour or grey (the CFD '+' crosses it)
        mg = m | masks["grey"]
        rows = [r for r in range(top + 120, bot) if mg[r, stem - 2: stem + 3].any()]
        segs = C.merge(rows, gap=30)  # bridges the stem's faint stretches, not the 50+ rows inside a circle
        _, s0, s1 = max(segs, key=lambda g: g[2] - g[1])
        inside = [g for g in groups if s0 - 8 <= g[0] <= s1 + 8]
        caps = [g for g in inside if g[3]]
        mid_seg = (s0 + s1) / 2.0
        notes = []
        up = [g for g in caps if g[0] < mid_seg]
        dn = [g for g in caps if g[0] > mid_seg]
        if up:
            u = up[0]
            hi_c, hi_h = u[0], (u[2] - u[1]) / 2.0 + 2
        else:
            u = min(inside, key=lambda g: g[0])
            hi_c, hi_h = u[0], (u[2] - u[1]) / 2.0 + 4
            notes.append(f"no cap at the upper end: taken at the marker edge there (rows {u[1]}-{u[2]}), where the cap is hidden")
        if dn:
            d = dn[-1]
            lo_c, lo_h = d[0], (d[2] - d[1]) / 2.0 + 2
        else:
            d = max(inside, key=lambda g: g[0])
            lo_c, lo_h = d[0], (d[2] - d[1]) / 2.0 + 4
            notes.append(f"no cap at the lower end: taken at the marker edge there (rows {d[1]}-{d[2]}), where the cap is hidden")
        mid = (hi_c + lo_c) / 2.0
        y = ax.val(mid)
        lo, hi = ax.interval(mid, (hi_h + lo_h) / 2.0)
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(stem), mid],
                    "bar_lo": ax.val(lo_c), "bar_hi": ax.val(hi_c),
                    "bar_lo_outer": ax.interval(lo_c, lo_h)[0], "bar_hi_outer": ax.interval(hi_c, hi_h)[1],
                    "px_lo": lo_c, "px_hi": hi_c,
                    "note": "; ".join([f"midpoint of the error bar (the mean of N = 3); ends at rows {hi_c:.1f} and {lo_c:.1f}; "
                                       f"misfit {ax.misfit:.2f} px"] + notes)})
    return out


def read_cfd(image, at):
    """The grey '+' of each branch: a grey horizontal run 35-65 px long whose midpoint column holds a
    grey vertical run 35-65 px long centred within 8 px of that row, within +-80 px of the branch column."""
    ax, xt, (top, bot) = calibrate(image)
    g = _masks(image)["grey"]
    out = []
    for xv in at:
        x = int(round(float(xv)))
        c0, c1 = int(xt[x - 1]) - 80, int(xt[x - 1]) + 80
        # first: a grey component 30-70 px both ways with a full-width row and a full-height column
        mm = g.copy()
        mm[:, :c0] = False
        mm[:, c1:] = False
        mm[: top + 120] = False
        mm[bot - 10:] = False
        lab, _ = ndi.label(mm)
        comp = None
        for i, sl in enumerate(ndi.find_objects(lab)):
            sub = lab[sl] == i + 1
            h, w = sub.shape
            if not (30 <= h <= 70 and 30 <= w <= 70):
                continue
            rs, cs = sub.sum(axis=1), sub.sum(axis=0)
            if rs.max() < 0.6 * w or cs.max() < 0.5 * h:
                continue
            bar = np.flatnonzero(rs >= 0.6 * w)
            comp = (sl[0].start + (bar.min() + bar.max()) / 2.0 + 0.5, sl[1].start + float(np.argmax(cs)) + 0.5,
                    (bar.max() - bar.min() + 1) / 2.0, sl[0].start + bar.min(), sl[0].start + bar.max())
        if comp is not None:
            cr, cc, half, a, b = comp
            lo, hi = ax.interval(cr, half + 2)
            out.append({"x": x, "y": ax.val(cr), "lo": lo, "hi": hi, "px": [cc, cr],
                        "note": f"grey '+' (a separate component), horizontal bar rows {a}-{b}"})
            continue
        # else (the '+' touches the inset drawing): runs, as described above
        cands = []
        for r in range(top + 120, bot - 10):
            for s, e in C.runs(g[r, c0:c1]):
                if not 35 <= e - s <= 65:
                    continue
                cm = c0 + (s + e) // 2
                for vs, ve in C.column_runs(g, cm, top + 100, bot):
                    if 35 <= ve - vs <= 65 and abs((vs + ve) / 2 - r) <= 8:
                        cands.append((r, cm))
        if not cands:
            out.append({"x": x, "y": None, "note": "no grey '+' found"})
            continue
        groups = C.merge([c[0] for c in cands], gap=1)
        cr, a, b = max(groups, key=lambda t: t[2] - t[1])
        cc = float(np.median([c[1] for c in cands if a <= c[0] <= b]))
        lo, hi = ax.interval(cr, (b - a + 1) / 2.0 + 2)
        out.append({"x": x, "y": ax.val(cr), "lo": lo, "hi": hi, "px": [cc, cr],
                    "note": f"grey '+' horizontal bar rows {a}-{b}"})
    return out


def read_dashed(image, at):
    """The grey dashed line: the rows where grey covers at least 30% of the plot width; read near each
    branch column as the weighted centre of the grey in those rows (+-4) within 120 px."""
    ax, xt, (top, bot) = calibrate(image)
    g = _masks(image)["grey"]
    left, right = int(xt[0]) - 200, int(xt[2]) + 200
    count = g[:, left:right].sum(axis=1)
    band = [r for r in range(top + 120, bot - 10) if count[r] >= 0.3 * (right - left)]
    if not band:
        return [{"x": int(round(float(v))), "y": None, "note": "dashed line not found"} for v in at]
    b0, b1 = min(band) - 4, max(band) + 5
    out = []
    for xv in at:
        x = int(round(float(xv)))
        c = int(xt[x - 1])
        w = g[b0:b1, c - 120: c + 120]
        prof = w.sum(axis=1).astype(float)
        if prof.sum() == 0:
            out.append({"x": x, "y": None, "note": "no dash within 120 px of the branch column"})
            continue
        r = b0 + float((prof * np.arange(len(prof))).sum() / prof.sum()) + 0.5
        lo, hi = ax.interval(r, (b1 - b0) / 2.0)
        out.append({"x": x, "y": ax.val(r), "lo": lo, "hi": hi, "px": [float(c), r],
                    "note": f"dashed line rows {b0}-{b1}; weighted centre near the branch column"})
    return out

