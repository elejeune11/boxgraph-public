"""Shared reading code for Fig. 5 (p. 5): p_lc vs q_c points at four P_lc in one dog.

Axes: calibrated from the inward tick marks (frame and tick code shared with Fig. 6): x ticks
matched to the printed labels 0.5, 1.0, 1.5 (bottom axis), y ticks to 10 ... 50 (left axis, of
which 20 and 40 are labelled).

Markers: the fitted lines are removed by a morphological opening wider than a line and narrower
than a marker; what is left are markers (and, where lines cross, short thick stubs, which are
smaller than any marker and dropped). Letters and digits are found as small isolated components
with little ink in their box. The legend markers are the ones with text just to their right;
from top to bottom they are, as printed: filled square (P_lc = 65 mm Hg), filled down-pointing
triangle (90), filled circle (125), filled up-pointing triangle (155). Each legend marker cut
from the page is the template for its kind: every data marker is matched against the four
templates (normalised correlation of ink/paper, at three scales) and takes the kind and centre of
the best match. Two overlapping markers (one blob of twice a marker's area) give two matches.
"""

import importlib.util
import os

import numpy as np
from scipy import ndimage
from scipy.signal import fftconvolve

_spec = importlib.util.spec_from_file_location(
    "fig6_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig6_common.py"))
F6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F6)

OPEN = 9                     # px at 600 dpi: lines are 4-6 px wide, markers 20-38 px
KINDS = ["square", "down_triangle", "circle", "up_triangle"]   # legend order, top to bottom
SCALES = [1.0, 1.15, 1.3]
CORNER = 0.57                # squares 0.63-0.94, circles 0.16-0.53 (second fullest box corner)
MIN_SCORE = 0.55             # a marker matches its template at 0.59-0.92; line crossings at 0.48


def calibrate(d):
    return F6.calibrate(d, x_labels=[0.5, 1.0, 1.5], x_step=1 / 4,
                        y_labels=[10, 20, 30, 40, 50], y_step=1 / 6)


def _scores(D, tpl):
    """Normalised correlation map of the +/-1 image D with the +/-1 template (centre-aligned)."""
    return fftconvolve(D, tpl[::-1, ::-1], mode="same") / tpl.size


def markers(image):
    g = image.astype(float).mean(axis=2)
    d = g < (np.percentile(g, 60) + np.percentile(g, 0.5)) / 2
    cal = calibrate(d)
    fr = cal["frame"]
    # inside the frame, 6 px clear of its lines (the scanned lines are up to 10 px thick)
    r0, r1 = fr["top"][1] + 6, fr["bottom"][0] - 6
    c0, c1 = fr["left"][1] + 6, fr["right"][0] - 6
    inside = np.zeros_like(d)
    inside[r0:r1, c0:c1] = d[r0:r1, c0:c1]
    orig, _ = ndimage.label(inside)
    op = ndimage.binary_opening(inside, structure=np.ones((OPEN, OPEN), bool))
    text = []
    for j, sl in enumerate(ndimage.find_objects(orig), 1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        mine = orig[sl] == j
        ink = mine.sum()
        solid = (op[sl] & mine).sum() / max(ink, 1)   # share of the ink in strokes wider than OPEN
        if h <= 70 and w <= 70 and ink > 60 and ink / (h * w) < 0.6 and solid < 0.6:
            text.append(((sl[0].start + sl[0].stop) / 2, sl[1].start, j))
    text_ids = {j for _, _, j in text}
    lab, _ = ndimage.label(op)
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == i
        if np.bincount(orig[sl][m]).argmax() in text_ids:
            continue
        sub = ndimage.binary_fill_holes(m)
        h, w = sub.shape
        # ink in each corner of the box, outside the inscribed ellipse: near 1 for a square, low for
        # a circle. A line crossing a marker fills or clips one corner, so the second fullest is used.
        yy, xx = np.mgrid[:h, :w]
        out_ell = ((yy + 0.5 - h / 2) / (h / 2)) ** 2 + ((xx + 0.5 - w / 2) / (w / 2)) ** 2 > 1
        quads = [out_ell & (yy < h / 2) & (xx < w / 2), out_ell & (yy < h / 2) & (xx >= w / 2),
                 out_ell & (yy >= h / 2) & (xx < w / 2), out_ell & (yy >= h / 2) & (xx >= w / 2)]
        fills = sorted(float(sub[q].mean()) if q.any() else 0.0 for q in quads)
        corner = fills[2]
        comps.append({"sl": sl, "area": int(sub.sum()), "h": h, "w": w, "fill": corner,
                      "rc": (sl[0].start + sl[0].stop) / 2, "cc": (sl[1].start + sl[1].stop) / 2,
                      "edge": [s for s, hit in (("bottom", sl[0].stop >= r1 - 1), ("right", sl[1].stop >= c1 - 1),
                                                ("top", sl[0].start <= r0 + 1), ("left", sl[1].start <= c0 + 1)) if hit]})
    cand = [k for k in comps
            if any(abs(tr - k["rc"]) < 30 and 0 < tc - k["sl"][1].stop < 120 for tr, tc, _ in text)]
    # the legend markers stand in one column; letters with text beside them do not
    legend = max(([q for q in cand if abs(q["cc"] - k["cc"]) < 15] for k in cand), key=len, default=[])
    legend.sort(key=lambda k: k["rc"])
    if len(legend) != len(KINDS):
        raise ValueError(f"found {len(legend)} legend markers, expected {len(KINDS)}")
    D = np.where(inside, 1.0, -1.0)
    maps = {}
    sizes = {}
    for kind, k in zip(KINDS, legend):
        sl = k["sl"]
        crop = d[sl[0].start - 4:sl[0].stop + 4, sl[1].start - 4:sl[1].stop + 4]
        sizes[kind] = (k["h"], k["w"])
        for s in SCALES:
            t = ndimage.zoom(crop.astype(float), s, order=1) > 0.5
            maps[(kind, s)] = _scores(D, np.where(t, 1.0, -1.0))
    leg_ids = {id(k) for k in legend}
    # the legend block: its markers, the heading above them and the labels to their right
    lb_r0 = legend[0]["sl"][0].start - 200
    lb_r1 = legend[-1]["sl"][0].stop + 40
    lb_c0 = min(k["sl"][1].start for k in legend) - 150   # the heading starts left of the markers
    in_legend = [k for k in comps if lb_r0 <= k["rc"] <= lb_r1 and k["cc"] >= lb_c0]
    leg_ids |= {id(k) for k in in_legend}
    big = max(k["area"] for k in legend)
    small = min(k["area"] for k in legend)
    w_small = min(k["w"] for k in legend)
    out = []
    for k in comps:
        if id(k) in leg_ids:
            continue
        if k["edge"]:
            if "top" in k["edge"] or "left" in k["edge"] or k["w"] < 0.75 * w_small or k["h"] < 8:
                continue  # tick marks drawn inward from the frame, narrower than any marker
        elif k["area"] < 0.5 * small:
            continue  # specks
        # one blob much larger than the largest legend marker is two overlapping markers
        n = 2 if (not k["edge"] and k["area"] > 1.4 * big) else 1
        sl = k["sl"]
        wr0, wr1 = max(sl[0].start - 8, 0), sl[0].stop + 8
        wc0, wc1 = max(sl[1].start - 8, 0), sl[1].stop + 8
        taken = np.zeros((wr1 - wr0, wc1 - wc0), bool)
        for _ in range(n):
            best = None
            per_kind = {}
            for (kind, s), S in maps.items():
                win = np.where(taken, -np.inf, S[wr0:wr1, wc0:wc1])
                idx = np.unravel_index(int(np.argmax(win)), win.shape)
                v = float(win[idx])
                per_kind[kind] = max(per_kind.get(kind, -np.inf), v)
                if best is None or v > best[0]:
                    best = (v, kind, s, idx)
            v, kind, s, (ri, ci) = best
            if v < MIN_SCORE:
                break  # no marker here: lines merging where they cross, or no second marker
            others = sorted((x for kk, x in per_kind.items() if kk != kind), reverse=True)
            how = "template"
            h, w = sizes[kind]   # size of the matched template
            if n == 1 and kind in ("square", "circle"):
                # the templates tell triangles well from round markers but square from circle only
                # weakly (the scan rounds the squares); a square has ink in its box corners
                if k["edge"]:
                    # cut by the frame, its box holds frame stubs and the corners cannot be judged
                    kind = "unclassified"
                    how = "template (round); cut by the frame, square or circle not decidable"
                else:
                    kind = "square" if k["fill"] > CORNER else "circle"
                    how = f"template (round), second fullest corner {k['fill']:.2f}"
            out.append({"kind": kind, "row": wr0 + ri + 0.5, "col": wc0 + ci + 0.5, "score": v,
                        "margin": v - others[0], "scale": s, "how": how, "h": h * s, "w": w * s,
                        "top": sl[0].start, "left": sl[1].start, "edge": k["edge"], "split": n > 1})
            yy, xx = np.mgrid[:taken.shape[0], :taken.shape[1]]
            taken |= (yy - ri) ** 2 + (xx - ci) ** 2 <= (0.45 * max(h, w) * s) ** 2
    return d, cal, out


def read_kind(image, kind):
    d, cal, ms = markers(image)
    _, bx, mx = cal["x"]
    _, by, my = cal["y"]
    fr = cal["frame"]
    out = []
    for m in ms:
        if m["kind"] != kind:
            continue
        note = (f"{kind} by {m['how']} (match {m['score']:.2f}, {m['margin']:.2f} above the next kind, "
                f"scale {m['scale']}); x cal misfit {mx:.2f} px, y cal misfit {my:.2f} px")
        rc, cc = m["row"], m["col"]
        err = 2.0 + my
        if m["split"]:
            err += 3.0
            note += "; one of two overlapping markers"
        if "right" in m["edge"]:
            cc = m["left"] + m["w"] / 2
            note += "; cut by the right frame: centre half a marker from its left edge"
        if "bottom" in m["edge"]:
            rc = m["top"] + m["h"] / 2
            err = max(abs(fr["bottom"][0] - rc), m["h"] / 2) + my
            note += "; cut by the x axis line: centre half a marker below its top, interval to the axis"
        lo, hi = sorted([F6.to_y(cal, rc - err), F6.to_y(cal, rc + err)])
        out.append({"x": F6.to_x(cal, cc), "y": F6.to_y(cal, rc), "lo": lo, "hi": hi, "px": [cc, rc],
                    "px_lo": rc + err, "px_hi": rc - err, "note": note})
    return sorted(out, key=lambda o: o["x"])
