"""Shared reading code for Fig. 3, top (p. 6): carotid sinus nerve frequency (spikes/s) against
intrasinus pressure (%). In the frame: the static model sigmoid (thin continuous line), the model
under 1.5-Hz pulsation of 20 mmHg (dot-dashed), 40 mmHg (dashed) and 60 mmHg (dotted) peak to
peak, Chapleau and Abboud's static data (open circles) and pulsatile data (asterisks).

Everything is found in the image. The crop is first straightened (the scan is tilted by about
0.2 degrees). Calibration: x, the frame's left side (label 0) and the inward ticks on the bottom
side (100, 200); y, the frame's bottom side (0) and the inward ticks on the left side (20, 40).
The elements are told apart by their shape: asterisks are the only ink thicker than 2 x 22 px;
circles are rings around a hole about 80 px across; dashes survive an opening of 19 px (the
continuous line is about 15 px thick and does not); dots are small round blobs, the dot-dash
line's dots (about 300 px) larger than the dotted line's (about 180 px).
"""
import importlib.util
import math
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location(
    "_u98", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_u98.py"))
u = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(u)


def calibrate(m):
    H, W = m.shape
    v = u.long_lines(m, 1, int(0.6 * H))
    h = u.long_lines(m, 0, int(0.6 * W))
    left, right, top, bottom = v[0], v[-1], h[0], h[-1]
    xt = [c for c, n in u.tick_marks(m, bottom[:2], 0, -1, length=(8, 80)) if left[1] + 40 < c < right[0] - 40]
    yt = [r for r, n in u.tick_marks(m, left[:2], 1, +1, length=(8, 80)) if top[1] + 40 < r < bottom[0] - 40]
    if len(xt) != 2 or len(yt) != 2:
        raise ValueError(f"expected 2 inner x ticks and 2 inner y ticks, found {xt} and {yt}")
    xcal = u.Cal([((left[0] + left[1]) / 2.0, 0.0), (xt[0], 100.0), (xt[1], 200.0)])
    ycal = u.Cal([((bottom[0] + bottom[1]) / 2.0, 0.0), (yt[1], 20.0), (yt[0], 40.0)])
    box = (left[1] + 12, top[1] + 12, right[0] - 12, bottom[0] - 12)
    return xcal, ycal, box


def elements(image):
    img, angle, back = u.straighten(image)
    m0 = u.ink(img)
    xcal, ycal, (c0, r0, c1, r1) = calibrate(m0)
    m = np.zeros_like(m0)
    m[r0:r1, c0:c1] = m0[r0:r1, c0:c1]
    dt = ndimage.distance_transform_edt(m)
    # asterisks: cores of very thick ink
    lab, n = ndimage.label(dt >= 22)
    cores = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        sub = dt[sl] * (lab[sl] == i)
        rr, cc = np.nonzero(sub >= 0.8 * sub.max())
        cores.append((cc.mean() + sl[1].start + 0.5, rr.mean() + sl[0].start + 0.5, float(sub.max())))
    # an asterisk crossed by a line or a circle can show several cores: the thickest stands for it
    stars = []
    for c in sorted(cores, key=lambda c: -c[2]):
        near = [s for s in stars if math.hypot(c[0] - s["col"], c[1] - s["row"]) <= 90]
        if near:
            near[0]["merged"] = max(near[0].get("merged", 0.0), abs(c[1] - near[0]["row"]))
        else:
            stars.append(dict(col=c[0], row=c[1], merged=0.0))
    # circles: holes about 80 px across, pieces of one hole grouped
    pieces = [b for b in u.holes(m, 200, 8000) if b["w"] <= 100 and b["h"] <= 100]
    groups = []
    for b in sorted(pieces, key=lambda b: (b["c0"], b["r0"])):
        for g in groups:
            if abs(g[0]["bcol"] - b["bcol"]) < 45 and abs(g[0]["brow"] - b["brow"]) < 90:
                g.append(b)
                break
        else:
            groups.append([b])
    circles = []
    for g in groups:
        hole = np.zeros_like(m)
        for b in g:
            hole[b["r0"]:b["r1"], b["c0"]:b["c1"]] |= b["mask"]
        rows = np.flatnonzero(hole.any(axis=1))
        width = np.array([hole[r].sum() for r in rows])
        cols = np.flatnonzero(hole.any(axis=0))
        wmax = width.max()
        if wmax < 60:
            continue
        diam_rows = rows[width >= wmax - 1]
        circles.append(dict(col=(cols.min() + cols.max() + 1) / 2.0, row=float(diam_rows.mean()) + 0.5,
                            full=bool(rows.max() - rows.min() + 1 >= 0.9 * wmax),
                            rspread=float(diam_rows.max() - diam_rows.min()) / 2.0))
    # without the markers
    m2 = m.copy()
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    for s in stars:
        m2[(xx - s["col"]) ** 2 + (yy - s["row"]) ** 2 <= 75 ** 2] = False
    for c in circles:
        m2[(xx - c["col"]) ** 2 + (yy - c["row"]) ** 2 <= 58 ** 2] = False
    # the continuous line is the only long piece of ink; dashes are short pieces, dots small ones
    # (markers cut the continuous line into pieces: a short piece whose middle lies on the line
    # joining the long pieces on either side of it, within 20 px, belongs to it too)
    parts = u.blobs(m2)
    long_ = [b for b in parts if b["w"] > 250]
    anchors = sorted((c + 0.5, float(np.mean(np.flatnonzero(b["mask"][:, c - b["c0"]]))) + b["r0"] + 0.5)
                     for b in long_ for c in (b["c0"] + 2, b["c1"] - 3))
    solid = np.zeros_like(m2)
    dashes = []
    for b in parts:
        on_line = False
        if b not in long_ and b["area"] >= 800 and anchors:
            left = [a for a in anchors if a[0] < b["col"]]
            right = [a for a in anchors if a[0] > b["col"]]
            if left and right:
                (ca, ra), (cb, rb) = left[-1], right[0]
                pred = ra + (rb - ra) * (b["col"] - ca) / (cb - ca)
                on_line = abs(b["row"] - pred) < 20 and cb - ca < 400
        if b in long_ or on_line:
            solid[b["r0"]:b["r1"], b["c0"]:b["c1"]] |= b["mask"]
        elif b["area"] >= 800 and max(b["w"], b["h"]) <= 200:
            dashes.append(b)
    dashes_mask = np.zeros_like(m2)
    for b in dashes:
        dashes_mask[b["r0"]:b["r1"], b["c0"]:b["c1"]] |= b["mask"]
    small = [b for b in parts if 100 <= b["area"] < 450 and b["h"] <= 30 and b["w"] <= 30 and b["fill"] > 0.5]
    # the two kinds of dots: split at the widest gap in their sizes
    areas = sorted(b["area"] for b in small)
    gaps = [(areas[i + 1] - areas[i], i) for i in range(len(areas) - 1)]
    g, i = max(gaps)
    cut = (areas[i] + areas[i + 1]) / 2.0
    dots_small = [b for b in small if b["area"] < cut]
    dots_big = [b for b in small if b["area"] >= cut]
    return dict(img=img, back=back, xcal=xcal, ycal=ycal, m=m, stars=stars, circles=circles, solid=solid,
                dashes=dashes, dots_small=dots_small, dots_big=dots_big, dashes_mask=dashes_mask,
                cut=cut, angle=angle)


def calnote(e):
    return (f"tilt {e['angle']:.2f} deg straightened; calibration misfit x {e['xcal'].misfit:.1f} px, "
            f"y {e['ycal'].misfit:.1f} px")


def read_solid(image, at):
    e = elements(image)
    out = u.read_line(e["solid"], e["xcal"], e["ycal"], at)
    for d in out:
        d["note"] = (d.get("note", "") + " " + calnote(e)).strip()
    return u.unrotate(out, e["back"])


def read_points(image, kind):
    e = elements(image)
    xcal, ycal = e["xcal"], e["ycal"]
    out = []
    if kind == "circles":
        for c in sorted(e["circles"], key=lambda c: c["col"]):
            err = 2.0 + c["rspread"] + ycal.err
            note = "circle centre from its hole's widest row" + ("" if c["full"] else "; part of the hole is covered by a line")
            out.append(u.point(xcal, ycal, c["col"], c["row"], err, note + "; " + calnote(e)))
    else:
        for s in sorted(e["stars"], key=lambda s: s["col"]):
            note = "asterisk centre: the thickest ink where its strokes cross"
            err = 5.0 + ycal.err
            if s["merged"]:
                note += ("; another thick crossing (a line or circle over an arm) lies "
                         f"{s['merged']:.0f} px away in height: the interval covers it")
                err += s["merged"]
            out.append(u.point(xcal, ycal, s["col"], s["row"], err, note + "; " + calnote(e)))
    return u.unrotate(out, e["back"])


def _chain(pts, step=(40, 260), rise=45):
    """The dots of one dotted line, in order: the longest chain of dots each 40-260 px (a marker
    can hide a few) to the
    right of the one before and within 45 px of its height (isolated tick marks and stray dots
    are left out)."""
    pts = sorted(pts)
    n = len(pts)
    best = [1] * n
    prev = [-1] * n
    for j in range(n):
        for i in range(j):
            dc, dr = pts[j][0] - pts[i][0], abs(pts[j][1] - pts[i][1])
            if step[0] <= dc <= step[1] and dr <= rise * dc / 75.0 and best[i] + 1 > best[j]:
                best[j], prev[j] = best[i] + 1, i
    if not n:
        return []
    k = int(np.argmax(best))
    out = []
    while k >= 0:
        out.append(pts[k])
        k = prev[k]
    return out[::-1]


def _interp(pts, col, maxgap):
    left = [p for p in pts if p[0] <= col]
    right = [p for p in pts if p[0] > col]
    if not left or not right:
        return None
    a, b = left[-1], right[0]
    if b[0] - a[0] > maxgap:
        return None
    return a[1] + (b[1] - a[1]) * (col - a[0]) / (b[0] - a[0]), b[0] - a[0], abs(b[1] - a[1])


def read_dotted(image, at):
    e = elements(image)
    xcal, ycal = e["xcal"], e["ycal"]
    pts = _chain([(b["col"], b["row"]) for b in e["dots_small"]])
    out = []
    for x in at:
        col = xcal.px(x)
        r = _interp(pts, col, 120)
        if r is None:
            out.append({"x": x, "y": None, "px": [col, 0.0], "note": "no dots of the dotted line on both sides"})
            continue
        row, span, rise = r
        err = 8.0 + 0.1 * rise + ycal.err   # dot size, straight-line interpolation between dots, calibration
        out.append(u.point(xcal, ycal, col, row, err,
                           f"between two dots {span:.0f} px apart; " + calnote(e)))
        out[-1]["x"] = x
    return u.unrotate(out, e["back"])


def _dash_axis(b):
    rr, cc = np.nonzero(b["mask"])
    rr = rr + b["r0"] + 0.5
    cc = cc + b["c0"] + 0.5
    cm, rm = cc.mean(), rr.mean()
    cov = np.cov(np.vstack([cc - cm, rr - rm]))
    w, vec = np.linalg.eigh(cov)
    d = vec[:, -1]
    if d[0] < 0:
        d = -d
    t = (cc - cm) * d[0] + (rr - rm) * d[1]
    return (cm, rm), d, t.min(), t.max()


def classify_dashes(e):
    """Dashes of the dot-dashed line have one of its dots just beyond an end, on the dash's
    own line; dashes of the dashed line have none."""
    out = []
    for b in e["dashes"]:
        (cm, rm), d, t0, t1 = _dash_axis(b)
        has_dot = False
        for q in e["dots_big"]:
            t = (q["col"] - cm) * d[0] + (q["row"] - rm) * d[1]
            off = abs(-(q["col"] - cm) * d[1] + (q["row"] - rm) * d[0])
            if off < 12 and (t1 + 8 < t < t1 + 75 or t0 - 75 < t < t0 - 8):
                has_dot = True
        out.append(dict(b=b, kind="dotdash" if has_dot else "dashed",
                        ends=((cm + t0 * d[0], rm + t0 * d[1]), (cm + t1 * d[0], rm + t1 * d[1]))))
    return out


def read_dashes(image, at, kind):
    e = elements(image)
    xcal, ycal = e["xcal"], e["ycal"]
    ds = [d for d in classify_dashes(e) if d["kind"] == kind]
    # the line as a sequence of points: each dash's two ends (and, for the dot-dash, its dots)
    pts = [p for d in ds for p in d["ends"]]
    if kind == "dotdash":
        pts += [(q["col"], q["row"]) for q in e["dots_big"]]
    pts = sorted(pts)
    out = []
    for x in at:
        col = xcal.px(x)
        cover = [d for d in ds if d["b"]["c0"] + 3 <= col < d["b"]["c1"] - 3]
        if len(cover) == 1:
            b = cover[0]["b"]
            cc = int(math.floor(col)) - b["c0"]
            rr = np.flatnonzero(b["mask"][:, cc])
            centre = (rr.min() + rr.max() + 1) / 2.0 + b["r0"]
            half = (rr.max() + 1 - rr.min()) / 2.0
            err = half / 2.0 + 1.0 + ycal.err   # the dash's centre line, at most a quarter of its height off
            out.append(u.point(xcal, ycal, col, centre, err, "on a dash; " + calnote(e)))
        elif not cover:
            r = _interp(pts, col, 140)
            if r is None:
                out.append({"x": x, "y": None, "px": [col, 0.0], "note": "in a gap of the line too wide to bridge"})
                continue
            row, span, rise = r
            err = 10.0 + 0.1 * rise + ycal.err
            out.append(u.point(xcal, ycal, col, row, err,
                               f"in a gap of the line, between ends {span:.0f} px apart; " + calnote(e)))
        else:
            out.append({"x": x, "y": None, "px": [col, 0.0],
                        "note": f"{len(cover)} dashes of this kind cover this column: not told apart"})
            continue
        out[-1]["x"] = x
    return u.unrotate(out, e["back"])
