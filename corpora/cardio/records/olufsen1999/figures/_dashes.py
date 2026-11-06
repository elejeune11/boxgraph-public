"""Broken (dashed, dash-dot) lines in Fig. 9(B) and 9(C): the measured impedances md 0 and md 1.

Calibration is that of _common.calibrate_fig9 (decade ticks matched to 10^0, 10^1, 10^2, right
frame 10^3; y frame ends matched to the printed end labels, checked by the major tick between).

Finding the dashes, all from the image:
1. Dark pixels inside the box (the frame and its tick marks excluded by a margin).
2. The solid line is removed: a dark run of a column is solid when it can be followed, touching
   column to column, for H columns on both sides (H is longer than any dash).
3. The rest is split into connected pieces. Pieces whose area is under a few line-widths squared are
   dots (the dotted windkessel line, the dots of the dash-dot line) and are dropped; the remaining
   pieces are dashes.
4. Near the column c of each requested x, each dash within W columns is extended to c with its own
   straight-line fit (row on column); dashes whose extensions meet within a few line widths form one
   track. Tracks are sorted top to bottom and the reader asks for one by its rank (and the number of
   tracks it expects there; any other count gives no value).
5. The value is the dash centre line at c when a dash of the track covers c, else the straight line
   from the end of the dash on the left to the start of the dash on the right (the measured curves
   are drawn as straight segments between points). The 95% interval is the line half-width + 2 px +
   the calibration misfit, widened by the spread of the track's dash extensions at c.
"""
import importlib.util
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def dash_pieces(cal):
    g = cal["gray"]
    top, bot, left, right = cal["top"], cal["bot"], cal["left"], cal["right"]
    dark = g < _c.ink_threshold(cal)
    m = max(12, int(0.012 * (bot - top)))
    box = np.zeros_like(dark)
    box[top + m:bot - m, left + m:right - m] = dark[top + m:bot - m, left + m:right - m]
    # line width: median vertical run length of the dark pixels in the box
    runs = []
    for cc in range(left + m, right - m, 7):
        runs += [len(gr) for gr in _c.groups(list(np.where(box[:, cc])[0]), gap=1)]
    lw = float(np.median(runs)) if runs else 6.0
    H = int(0.03 * (right - left))
    # solid mask by tracing runs
    colruns = {}
    for cc in range(left + m, right - m):
        colruns[cc] = [(gr[0], gr[-1]) for gr in _c.groups(list(np.where(box[:, cc])[0]), gap=1)]

    def traces(run, c0, step):
        r0, r1 = run
        for cc in range(c0 + step, c0 + step * (H + 1), step):
            if cc not in colruns:
                return True  # reached the frame margin while still continuous
            nxt = [(a, b) for a, b in colruns[cc] if a <= r1 + 1 and b >= r0 - 1]
            if not nxt:
                return False
            r0, r1 = min(a for a, _ in nxt), max(b for _, b in nxt)
        return True

    rest = box.copy()
    for cc, rr in colruns.items():
        for run in rr:
            if traces(run, cc, +1) and traces(run, cc, -1):
                rest[run[0]:run[1] + 1, cc] = False
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    pieces = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        sub = lab[sl] == i
        area = int(sub.sum())
        width = sl[1].stop - sl[1].start
        if area < 2 * lw * lw or width < 2.5 * lw:
            continue
        cols = np.arange(sl[1].start, sl[1].stop)
        centre = []
        for j, cc in enumerate(cols):
            rr = np.where(sub[:, j])[0]
            if len(rr):
                centre.append((cc, sl[0].start + 0.5 * (rr.min() + rr.max())))
        centre = np.array(centre)
        a, b = np.polyfit(centre[:, 0], centre[:, 1], 1)
        pieces.append(dict(c0=int(cols[0]), c1=int(cols[-1]), centre=centre, slope=a, icpt=b))
    return pieces, lw


def read_track(cal, pieces, lw, x, rank, n_expected, W_frac=0.035, tol=4.0):
    left, right = cal["left"], cal["right"]
    W = int(W_frac * (right - left))
    c = int(round(cal["col_of"](x)))
    near = [p for p in pieces if p["c1"] >= c - W and p["c0"] <= c + W]
    for p in near:
        if p["c0"] <= c <= p["c1"]:
            k = int(np.argmin(np.abs(p["centre"][:, 0] - c)))
            p["at_c"] = float(p["centre"][k, 1])
        else:
            p["at_c"] = p["slope"] * c + p["icpt"]
    near.sort(key=lambda p: p["at_c"])
    tracks = []
    for p in near:
        if tracks and abs(p["at_c"] - tracks[-1][-1]["at_c"]) < tol * lw:
            tracks[-1].append(p)
        else:
            tracks.append([p])
    if len(tracks) != n_expected:
        return {"x": x, "y": None, "note": f"{len(tracks)} dash tracks at column {c}, expected {n_expected}"}
    tr = tracks[rank]
    cover = [p for p in tr if p["c0"] <= c <= p["c1"]]
    if cover:
        row = float(np.mean([p["at_c"] for p in cover]))
        how = "on a dash"
    else:
        lefts = [p for p in tr if p["c1"] < c]
        rights = [p for p in tr if p["c0"] > c]
        if not lefts or not rights:
            return {"x": x, "y": None, "note": f"no dash of the track on both sides of column {c}"}
        pl = max(lefts, key=lambda p: p["c1"])
        pr = min(rights, key=lambda p: p["c0"])
        r_l, r_r = float(pl["centre"][-1, 1]), float(pr["centre"][0, 1])
        row = r_l + (r_r - r_l) * (c - pl["c1"]) / (pr["c0"] - pl["c1"])
        how = f"between dashes ending at column {pl['c1']} and starting at {pr['c0']}"
    spread = max(abs(p["at_c"] - row) for p in tr)
    pad = 0.5 * lw + 2 + cal["ymis"] + spread
    ya, yb = cal["val_of"](row - pad), cal["val_of"](row + pad)
    return {"x": x, "y": cal["val_of"](row), "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, row],
            "px_lo": row - pad, "px_hi": row + pad,
            "note": f"track {rank + 1} of {n_expected} from the top, {how}; line width {lw:.0f} px, spread {spread:.1f} px"}


def read(image, at, ylog, ytop, ybot, ymid, plan, W_frac=0.035, tol=4.0):
    """plan: list of (x_lo, x_hi, rank, n_expected): which track (rank from the top among the
    n_expected dash tracks found) is the wanted curve for x in [x_lo, x_hi]; an entry may add its own
    (W_frac, tol) as a fifth and sixth element. W_frac: the window
    (fraction of the box width); tol: dashes within tol line widths at c are one track."""
    cal = _c.calibrate_fig9(image, ylog, ytop, ybot, ymid)
    pieces, lw = dash_pieces(cal)
    out = []
    for x in at:
        rule = [p for p in plan if p[0] <= x <= p[1]]
        if not rule:
            out.append({"x": x, "y": None, "note": "outside the stretches where the curve is told apart"})
            continue
        r = rule[0]
        w, t = (r[4], r[5]) if len(r) > 5 else (W_frac, tol)
        out.append(read_track(cal, pieces, lw, x, r[2], r[3], w, t))
    return out
