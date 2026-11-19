"""Shared reading code for the plots of huang2005 (Figs. 3, 5, 7, 10, 11).

All the plots are vector drawings rendered from the PDF, so lines are crisp.

Calibration, all from the image:
- the y axis is the band of columns holding the longest vertical black run in the left half, the
  x axis the band of rows holding the longest horizontal black run in the lower half;
- every labelled tick protrudes outward from its axis (to the left of the y axis, below the x
  axis) and is longer than the minor ticks; the outward black runs touching the axis are
  collected, the longest ones kept and the evenly spaced subset taken (this drops the corner
  where the other axis line overshoots). They must be as many as the printed labels, which are
  matched to them in order; a straight line (in log10 for a logarithmic axis) is fitted through
  (pixel, label), and its largest residual is the calibration misfit (at least 0.5 px).
Curves: a colour mask (red, blue, green or black) inside the frame (the axis lines, frame lines
and the tick bands along them removed). Thin features (dashed guide lines, dots) can be removed
by a morphological opening. The curve is followed column by column from a seed column, where the
curve is the n-th run of the mask from the top, taking in each column the run nearest the
position extrapolated from the last clean points. A run much thicker than the line (a crossing,
a marker, a label touching the line) is kept on the path but marked unclean. A value is the
centre of the line at the column of x; its 95% interval spans the ink of the line over the
columns within the x misfit, widened by the y misfit. Where the line is partly hidden under
another curve (visible part thinner than 0.8 of the line width), the interval spans the whole
stack of ink in that column.
Markers: the mask's holes are filled (open markers become solid), an opening with a disc a bit
smaller than the marker removes the lines, and each remaining component is a marker, read at
the centre of its bounding box; the interval is the misfit plus 2 px plus the distance between
the box centre and the centroid (for a triangle the two differ).
"""
import numpy as np
from scipy import ndimage

from boxgraph.digitize import Axis, regular_ticks


# ---------------------------------------------------------------- masks

def masks(img):
    im = img[..., :3].astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    return {
        "black": (r < 110) & (g < 110) & (b < 110),
        "red": (r > 170) & (g < 110) & (b < 110),
        "blue": (b > 170) & (r < 110) & (g < 110),
        "green": (g > 150) & (r < 130) & (b < 130),
        "ink": (r + g + b) < 600,
    }


def _groups(idx, gap=1):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(int(i))
        else:
            out.append([int(i)])
    return out


def _runs(v):
    """(start, end inclusive) of True runs of a 1-D boolean array."""
    idx = np.flatnonzero(v)
    if idx.size == 0:
        return []
    cuts = np.flatnonzero(np.diff(idx) > 1)
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]]
    return list(zip(starts.tolist(), ends.tolist()))


def _longest(v):
    rs = _runs(v)
    if not rs:
        return 0, 0, -1
    s, e = max(rs, key=lambda t: t[1] - t[0])
    return e - s + 1, s, e


# ---------------------------------------------------------------- calibration

def frame(black):
    H, W = black.shape
    col_len = np.array([_longest(black[:, c])[0] for c in range(W)])
    half = W // 2
    m = col_len[:half].max()
    ycols = [c for c in range(half) if col_len[c] >= 0.9 * m]
    ycols = max(_groups(ycols), key=len)
    row_len = np.array([_longest(black[r, :])[0] for r in range(H)])
    m2 = row_len[H // 2:].max()
    xrows = [r for r in range(H // 2, H) if row_len[r] >= 0.9 * m2]
    xrows = max(_groups(xrows), key=len)
    # extent of the y axis line and x axis line
    _, ytop, ybot = _longest(black[:, ycols[len(ycols) // 2]])
    _, xl, xr = _longest(black[xrows[len(xrows) // 2], :])
    # a right frame: a long vertical run in the right half spanning most of the y axis
    # (a frame line meets the end of the other axis; long plotted lines do not)
    right = [c for c in range(half, W) if col_len[c] >= 0.8 * m and abs(c - xr) <= 12]
    top = [r for r in range(0, H // 2) if row_len[r] >= 0.8 * m2 and abs(r - ytop) <= 12]
    return {
        "ycols": (ycols[0], ycols[-1]), "xrows": (xrows[0], xrows[-1]),
        "ytop": ytop, "xright": xr,
        "right": (min(right), max(right)) if right else None,
        "top": (min(top), max(top)) if top else None,
    }


def _outward(black, fr, which):
    """(centre, length) of black runs protruding outward from an axis."""
    out = []
    if which == "x":
        r1 = fr["xrows"][1]
        H = black.shape[0]
        lens = []
        for c in range(black.shape[1]):
            n = 0
            r = r1 + 1
            while r < H and black[r, c]:
                n += 1
                r += 1
            lens.append(n)
        lens = np.array(lens)
    else:
        c0 = fr["ycols"][0]
        lens = []
        for r in range(black.shape[0]):
            n = 0
            c = c0 - 1
            while c >= 0 and black[r, c]:
                n += 1
                c -= 1
            lens.append(n)
        lens = np.array(lens)
    cand = np.flatnonzero(lens >= 6)
    for g in _groups(cand):
        if len(g) > 40:  # not a tick
            continue
        out.append((float(np.mean(g)) + 0.5, int(lens[g].max())))
    return out


def calibrate(img, xlabels, ylabels, xscale="linear", yscale="linear"):
    """Axes from the image. Labels in increasing value (x left to right, y bottom to top)."""
    mk = masks(img)
    black = mk["black"]
    fr = frame(black)
    res = {}
    for which, labels, scale in (("x", xlabels, xscale), ("y", ylabels, yscale)):
        ticks = _outward(black, fr, which)
        if not ticks:
            raise ValueError(f"no outward ticks on the {which} axis")
        L = max(t[1] for t in ticks)
        major = [t[0] for t in ticks if t[1] >= 0.75 * L]
        major = regular_ticks(major, tol=2.5)
        if len(major) != len(labels):
            raise ValueError(f"{which} axis: {len(major)} labelled ticks found {major}, {len(labels)} labels")
        vals = list(labels) if which == "x" else list(reversed(labels))
        ax = Axis(scale, list(zip(major, vals)))
        res[which] = ax
        res[which + "_ticks"] = major
        res[which + "_tick_len"] = L
    res["frame"] = fr
    res["masks"] = mk
    return res


def interior(cal, margin=None):
    """Boolean mask of the plot area away from axis lines, frame lines and tick bands."""
    fr = cal["frame"]
    black = cal["masks"]["black"]
    H, W = black.shape
    m = int(margin if margin is not None else max(cal["x_tick_len"], cal["y_tick_len"]) * 0.8 + 6)
    inside = np.zeros((H, W), bool)
    c0 = fr["ycols"][1] + m
    r1 = fr["xrows"][0] - m
    c1 = W if fr["right"] is None else fr["right"][0] - m
    r0 = 0 if fr["top"] is None else fr["top"][1] + m
    inside[r0:r1, c0:c1] = True
    return inside


def prepared(mask, inside, open_px=0):
    m = mask & inside
    if open_px:
        st = _disc(open_px)
        m = ndimage.binary_opening(m, structure=st)
    return m


def _disc(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


# ---------------------------------------------------------------- curves

def trace(mask, seed_c, seed_rank, max_gap=60, tol=None, avoid=None):
    """Follow a line. Returns col -> (centre, top, bottom, clean). A run touching `avoid`
    (the area of the markers) is unclean and does not steer the extrapolation."""
    W = mask.shape[1]
    rs = _runs(mask[:, seed_c])
    if len(rs) <= seed_rank:
        raise ValueError(f"seed column {seed_c}: only {len(rs)} runs, wanted run {seed_rank}")
    s, e = rs[seed_rank]
    width = e - s + 1
    path = {seed_c: ((s + e + 1) / 2, s, e, True)}
    for step in (1, -1):
        hist = [(seed_c, (s + e + 1) / 2)]
        c, gap = seed_c + step, 0
        while 0 <= c < W and gap <= max_gap:
            rec = hist[-12:]
            slope = (rec[-1][1] - rec[0][1]) / (rec[-1][0] - rec[0][0]) if len(rec) > 1 else 0.0
            pred = hist[-1][1] + slope * (c - hist[-1][0])
            cand = _runs(mask[:, c])
            if cand:
                def dist(x):
                    return 0.0 if x[0] <= pred <= x[1] + 1 else min(abs(x[0] - pred), abs(x[1] + 1 - pred))
                a, b = min(cand, key=dist)
                lim = (tol if tol is not None else 3 * width) + abs(slope) * (gap + 1)
                if dist((a, b)) <= lim:
                    th = b - a + 1
                    clean = th <= 1.6 * width + 2 + abs(slope) * 1.0
                    if avoid is not None and avoid[a:b + 1, c].any():
                        clean = False
                    path[c] =((a + b + 1) / 2, a, b, clean)
                    if clean:
                        hist.append((c, (a + b + 1) / 2))
                    gap = 0
                    c += step
                    continue
            gap += 1
            c += step
    return path, width


def fill_small_holes(m, max_side):
    """Fill holes whose bounding box is at most max_side on both sides (marker interiors),
    not the long regions enclosed between two curves."""
    holes = ndimage.binary_fill_holes(m) & ~m
    hl, hn = ndimage.label(holes)
    if not hn:
        return m
    small = np.zeros(hn + 1, bool)
    for i, sl in enumerate(ndimage.find_objects(hl), start=1):
        small[i] = (sl[0].stop - sl[0].start) <= max_side and (sl[1].stop - sl[1].start) <= max_side
    return m | small[hl]


def marker_mask(m, open_px, max_side):
    """Solid markers of a mask: small holes filled, then thin lines opened away."""
    return ndimage.binary_opening(fill_small_holes(m, max_side), structure=_disc(open_px))


def read_curve(img, at, xlabels, ylabels, xscale, yscale, color, seed_x, seed_rank=0,
               open_px=0, margin=None, unclean_ok=False, remove_markers=0):
    """With remove_markers = r, the area of solid markers (see marker_mask, opening radius r,
    grown by 8 px to cover their points) is avoided: runs there are unclean, do not steer the
    trace and are not read."""
    cal = calibrate(img, xlabels, ylabels, xscale, yscale)
    xa, ya = cal["x"], cal["y"]
    inside = interior(cal, margin)
    mask = prepared(cal["masks"][color], inside, open_px)
    avoid = None
    if remove_markers:
        avoid = ndimage.binary_dilation(marker_mask(mask, remove_markers, 31), structure=_disc(8))
    ink = cal["masks"]["ink"] & inside
    seed_c = int(np.floor(xa.to_pixel(seed_x)))
    path, width = trace(mask, seed_c, seed_rank, avoid=avoid)
    # the line width: median thickness of clean runs (vertical thickness grows with slope)
    xmis, ymis = max(xa.residual_px, 0.5), max(ya.residual_px, 0.5)
    k = int(np.ceil(xmis))
    out = []
    for x in at:
        cc = xa.to_pixel(x)
        c = int(np.floor(cc))
        if c not in path:
            out.append({"x": x, "y": None, "note": "the traced line does not reach this x"})
            continue
        centre, top, bot, clean = path[c]
        if not clean and not unclean_ok:
            out.append({"x": x, "y": None, "note": "the line merges with other ink here (crossing or label)"})
            continue
        near = [path[j] for j in range(c - k, c + k + 1) if j in path]
        top = min(p[1] for p in near)
        bot = max(p[2] for p in near)
        note = f"x misfit {xa.residual_px:.2f} px, y misfit {ya.residual_px:.2f} px; ink rows {top}-{bot}"
        th = path[c][2] - path[c][1] + 1
        if th < 0.8 * width:
            # partly hidden under another curve: the interval spans the whole stack of ink
            for a, b in _runs(ink[:, c]):
                if a <= path[c][1] and b >= path[c][2]:
                    top, bot = min(top, a), max(bot, b)
            note += "; partly hidden under another line, interval spans the stack of ink"
        if not clean:
            note += "; thicker than the line here (crossing), interval spans the ink"
        y = ya.to_value(centre)
        v1 = ya.to_value(top - ymis)
        v2 = ya.to_value(bot + 1 + ymis)
        out.append({"x": x, "y": float(y), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(cc), float(centre)], "px_lo": float(top), "px_hi": float(bot + 1),
                    "note": note})
    return out


# ---------------------------------------------------------------- markers

def markers(img, xlabels, ylabels, xscale, yscale, color, open_px, min_area, max_area=None, margin=None,
            fill=True, box=(0, 10**6), ratio=(0.0, 1.01), close_px=0):
    """All markers of a colour: list of dicts (x, y, interval, px), left to right.
    Only components whose bounding box side is within `box` (px) and whose fill ratio
    (area over box area) is within `ratio` are kept: this tells marker shapes apart
    (circle about 0.78, triangle about 0.6, star smaller) and drops label glyphs."""
    cal = calibrate(img, xlabels, ylabels, xscale, yscale)
    xa, ya = cal["x"], cal["y"]
    inside = interior(cal, margin)
    m = cal["masks"][color] & inside
    if close_px:  # bridge a thin line of another colour drawn across a marker
        m = ndimage.binary_closing(m, structure=_disc(close_px)) & inside
    if fill:  # fill only small holes (marker interiors), not regions enclosed by curves
        m = fill_small_holes(m, min(max(box), 60))
    m = ndimage.binary_opening(m, structure=_disc(open_px))
    lab, n = ndimage.label(m)
    objs = ndimage.find_objects(lab)
    xmis, ymis = max(xa.residual_px, 0.5), max(ya.residual_px, 0.5)
    out = []
    for i, sl in enumerate(objs, start=1):
        area = int((lab[sl] == i).sum())
        if area < min_area or (max_area is not None and area > max_area):
            continue
        r0, r1 = sl[0].start, sl[0].stop
        c0, c1 = sl[1].start, sl[1].stop
        bx = box if len(box) == 4 else (box[0], box[1], box[0], box[1])  # (wmin, wmax, hmin, hmax)
        if not (bx[0] <= c1 - c0 <= bx[1] and bx[2] <= r1 - r0 <= bx[3]):
            continue
        if not (ratio[0] <= area / ((c1 - c0) * (r1 - r0)) <= ratio[1]):
            continue
        rc, cc = (r0 + r1) / 2, (c0 + c1) / 2
        cy, cx = ndimage.center_of_mass(lab[sl] == i)
        cy += r0 + 0.5
        dy = abs(cy - rc)
        half = ymis + 2 + dy
        y = ya.to_value(rc)
        v1, v2 = ya.to_value(rc - half), ya.to_value(rc + half)
        out.append({"x": float(xa.to_value(cc)), "y": float(y), "lo": float(min(v1, v2)),
                    "hi": float(max(v1, v2)), "px": [float(cc), float(rc)],
                    "px_lo": float(rc - half), "px_hi": float(rc + half),
                    "note": f"marker box {c1 - c0}x{r1 - r0} px, area {area}; x misfit "
                            f"{xa.residual_px:.2f} px, y misfit {ya.residual_px:.2f} px",
                    "_w": c1 - c0, "_h": r1 - r0})
    out.sort(key=lambda d: d["px"][0])
    return out


def clean(rows):
    return [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]


def read_curve_p(image, at, p):
    return read_curve(image, at, p["xlabels"], p["ylabels"], p["xscale"], p["yscale"], p["color"], p["seed_x"],
                      p.get("seed_rank", 0), p.get("open_px", 0), p.get("margin"), False,
                      p.get("remove_markers", 0))


def read_markers_p(image, p):
    rows = markers(image, p["xlabels"], p["ylabels"], p["xscale"], p["yscale"], p["color"], p["open_px"],
                   p["min_area"], p.get("max_area"), p.get("margin"), True, tuple(p["box"]), tuple(p["ratio"])
                   if "ratio" in p else (0.0, 1.01), p.get("close_px", 0))
    if p.get("legend"):
        # the legend's sample marker has the legend text (black) beside it on the same row
        black = masks(image)["black"]
        keep = []
        for r in rows:
            c, rr = int(r["px"][0]), int(r["px"][1])
            if black[max(rr - 20, 0):rr + 20, c + 100:c + 400].sum() > 200:
                continue
            keep.append(r)
        rows = keep
    return clean(rows)
