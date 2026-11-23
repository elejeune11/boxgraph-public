"""Reading code for Fig. 3B of cao2017 (PDF p. 3): DFN normalized fibre density against cell
contraction per perimeter, square markers of one colour per network, on fit lines of the same colour.

Everything is found in the image (the frame and ticks with _panel.py's spines() and ticks()):
  x axis    the left and right frame lines stand at the printed 0.0 and 7.5 (the labels sit
            under them); the two ticks pointing into the box from the bottom frame (found as
            short dark strokes just above it) are 2.5 and 5.0. A linear fit of the four gives
            the calibration and its misfit.
  y axis    the bottom and top frame lines stand at the printed 1 and 1.3; the tick pointing
            into the box from the left frame is 1.15. The bottom frame is mostly covered by the
            blue fit line: its centre is taken half the top frame's thickness above its visible
            lower edge. A linear fit of the three.
  markers   pixels nearest in colour to the series' colour (among the panel's colours), holes
            filled (some markers carry a small black dot); markers are much thicker than the fit
            line, so where the distance to the mask's edge exceeds `core` times the largest such
            distance R, each connected core is one marker; its centre is the distance-weighted
            centroid of the core's top. A marker under the frame or another colour has a lower
            peak and is reported as partly hidden, its interval widened by R minus its peak.

Intervals (95%): 1.5 px of centring plus the calibration misfit plus any hiding.
"""
import hashlib
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

PANEL = Path(__file__).with_name("_panel.py")
PANEL_SHA256 = "57437849ee3f9c147f95fe3d37f5ce33b622f56e385bdd5b6a71794fd86c70c5"


def _panel():
    if hashlib.sha256(PANEL.read_bytes()).hexdigest() != PANEL_SHA256:
        raise RuntimeError("_panel.py changed; re-check _fig3b.py and update PANEL_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_panel", PANEL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fit(pix, vals):
    pix, vals = np.array(pix, float), np.array(vals, float)
    b, a = np.polyfit(vals, pix, 1)
    return {"a": a, "b": b, "misfit": max(float(np.max(np.abs(pix - (a + b * vals)))), 0.5), "n": len(pix)}


def calibrate(img):
    P = _panel()
    sp = P.spines(img)
    blk = P.black(img)
    H, W = blk.shape
    cl = (sp["left"]["c0"] + sp["left"]["c1"]) / 2.0 + 0.5
    cr = (sp["right"]["c0"] + sp["right"]["c1"]) / 2.0 + 0.5
    rt = (sp["top"]["r0"] + sp["top"]["r1"]) / 2.0 + 0.5
    thick = sp["top"]["r1"] - sp["top"]["r0"] + 1
    # the bottom frame is mostly covered by the blue fit line: its lower edge still shows; the frame
    # has the top frame's thickness, so its centre is half that above the lower edge
    edges = []
    for c in range(int(0.6 * W), sp["right"]["c0"] - 5):
        rows = np.where(blk[int(0.7 * H):, c])[0]
        if len(rows):
            edges.append(int(0.7 * H) + rows.max())
    rb = float(np.median(edges)) + 1.0 - thick / 2.0
    # x ticks: short dark strokes standing on the frame, inside the box, between the side frames
    band = blk[int(rb - thick / 2 - 45):int(rb - thick / 2 - 12), :]
    cols = [c for c in range(sp["left"]["c1"] + 15, sp["right"]["c0"] - 15) if band[:, c].mean() > 0.6]
    xt = [(g[0] + g[-1]) / 2.0 + 0.5 for g in P._groups(cols) if len(g) < 40]
    # y tick: inside the left frame, away from the top frame
    yt = [t for t in P.ticks(img, sp, "left", inside=True, max_len=80) if abs(t - rt) > 2 * thick]
    if len(xt) != 2 or len(yt) != 1:
        raise ValueError(f"found {len(xt)} x ticks and {len(yt)} y ticks (want 2 and 1)")
    xt, yt = sorted(xt), sorted(yt)
    xa = _fit([cl, xt[0], xt[1], cr], [0.0, 2.5, 5.0, 7.5])
    ya = _fit([rt, yt[0], rb], [1.3, 1.15, 1.0])
    return xa, ya, sp


def _val(ax, p):
    return float((p - ax["a"]) / ax["b"])


def read(image, at, color, others, core=0.6, tol=120):
    xa, ya, sp = calibrate(image)
    f = image.astype(float)
    d = np.sqrt(((f - np.array(color, float)) ** 2).sum(axis=2))
    m = d < tol
    for o in others:
        m &= d <= np.sqrt(((f - np.array(o, float)) ** 2).sum(axis=2))
    m = ndi.binary_closing(m, iterations=2)
    m = ndi.binary_fill_holes(m)
    dt = ndi.distance_transform_edt(m)
    R = float(dt.max())
    lab, n = ndi.label(dt >= core * R)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.where(lab == i)
        w = dt[rr, cc]
        peak = float(w.max())
        top = w >= peak - 2.0
        r = float((rr[top] * w[top]).sum() / w[top].sum()) + 0.5
        c = float((cc[top] * w[top]).sum() / w[top].sum()) + 0.5
        hidden = max(0.0, R - peak)
        e = 1.5 + ya["misfit"] + hidden
        y = _val(ya, r)
        v1, v2 = _val(ya, r - e), _val(ya, r + e)
        out.append({"x": _val(xa, c), "y": y, "lo": min(v1, v2), "hi": max(v1, v2), "px": [c, r],
                    "px_lo": r - e, "px_hi": r + e,
                    "note": f"marker centre (half-width {peak:.0f} of {R:.0f} px{', partly hidden' if hidden > 2 else ''}); "
                            f"x misfit {xa['misfit']:.1f} px ({xa['n']} marks), y misfit {ya['misfit']:.1f} px ({ya['n']} marks)"})
    out.sort(key=lambda r: r["x"])
    return out
