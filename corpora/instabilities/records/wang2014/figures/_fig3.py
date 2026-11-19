"""Fig. 3 (PDF p. 2): measured adhesion energy Gamma (N/m) against film shear modulus mu_f (kPa),
three prestretches (blue circles lambda_p = 1, red triangles 2, green squares 3), with error bars.

Calibration (shared code in _wang.py): the black frame; x ticks 50, 100, 150 inward from the bottom
frame, 0 and 200 at the frame lines; y ticks 1 to 6 inward from the left frame, 0 at the bottom
frame line. The legend box and the inset sketch (whose cyan fill is near the blue) are blanked.

Markers overlap (green drawn over red over blue), so each is found by template matching: the
template is the outline of the same marker in the legend (its colour's pixels there); its
correlation with the colour mask over the plot is computed and every local maximum (within half a
marker of no better one) whose overlap is at least `min_frac` of the template is a marker; its
centre is the value.

Error bars: the caps are short horizontal runs of the colour (about 32 px), centred on the marker
column; a cap row has at least CAP_MIN pixels of the colour within half a marker width of the
column but more than STEM_HALF px from it (the middle of a cap is often under another series'
stem, and a stem alone has none there). The farthest cap above the marker and the farthest
below (within `reach` px, outside the marker itself) are the bar ends. A cap hidden behind a marker
or another series is not found; the bar then is mirrored from the other end and the note says so.
bar_lo_outer/bar_hi_outer widen the ends by half the cap thickness, the calibration misfit and 2 px.

Interval of the value: +- (misfit + 3 px + spread), where spread is the half-height in rows over
which the overlap at the marker column stays within 90% of its best; for the triangles plus h/6,
since the plotted point may be the triangle's box centre (taken) or its centroid. Markers need an
overlap of at least MIN_FRAC: green squares are drawn last and whole, the red triangles partly and
the blue circles mostly hidden behind them.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage, signal

SPEC = {"x": {"lo": 0, "hi": 200, "ticks": [50, 100, 150]},
        "y": {"lo": 0, "ticks": [1, 2, 3, 4, 5, 6]}}
LEGEND = (2300, 200, 3010, 1070)   # crop pixels (x0, y0, x1, y1)
INSET = (820, 740, 2200, 1140)
TEMPLATE_BOX = {"blue": (2400, 290, 2560, 430), "red": (2400, 560, 2560, 700), "green": (2400, 840, 2560, 970)}
CAP_T = 14  # cap line thickness, px
STEM_HALF = 10  # columns within this of the marker column are the stem (any series'), not a cap
CAP_MIN = 10  # a cap row has at least this many pixels of the colour outside the stem
CAP_HALF = 18  # caps are about 32 px wide; neighbouring columns of points are only ~37 px apart
MIN_FRAC = {"green": 0.7, "red": 0.5, "blue": 0.35}  # green is drawn on top; blue mostly hidden
ANCHOR = {"red": 1 / 6}  # a triangle's anchor may be its box centre or its centroid (h/6 lower)


def _shared():
    spec = importlib.util.spec_from_file_location("wang2014_wang", Path(__file__).with_name("_wang.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mask(image, colour):
    a = np.asarray(image)[..., :3].astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if colour == "blue":
        return (b - r > 120) & (b - g > 110)
    if colour == "red":
        return (r - g > 100) & (r - b > 100)
    return (g - r > 80) & (g - b > 80)


def read_series(image, colour, min_frac=None, reach=1400):
    min_frac = MIN_FRAC[colour] if min_frac is None else min_frac
    W = _shared()
    cal = W.calibrate(image, SPEC)
    X, Y, fr = cal["x"], cal["y"], cal["frame"]
    mis = max(X.misfit, Y.misfit)
    full = mask(image, colour)
    x0, y0, x1, y1 = TEMPLATE_BOX[colour]
    tpl = full[y0:y1, x0:x1]
    ys, xs = np.nonzero(tpl)
    tpl = tpl[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(float)
    th, tw = tpl.shape
    m = full.copy()
    for bx0, by0, bx1, by1 in (LEGEND, INSET):
        m[by0:by1, bx0:bx1] = False
    l, r = int(fr["left"][1]) + 2, int(fr["right"][0]) - 2
    t, b = int(fr["top"][1]) + 2, int(fr["bottom"][0]) - 2
    keep = np.zeros_like(m)
    keep[t:b, l:r] = m[t:b, l:r]
    m = keep
    # score[i, j] = overlap of the template with its top-left corner at (i, j)
    score = signal.fftconvolve(m.astype(float), tpl[::-1, ::-1], mode="valid")
    total = tpl.sum()
    peak = ndimage.maximum_filter(score, size=(th // 2 * 2 + 1, tw // 2 * 2 + 1))
    cand = np.argwhere((score >= peak - 1e-6) & (score >= min_frac * total))
    taken = []
    for i, j in sorted(cand.tolist(), key=lambda ij: -score[ij[0], ij[1]]):
        if any(abs(i - a) < th / 2 and abs(j - c) < tw / 2 for a, c in taken):
            continue
        taken.append((i, j))
    out = []
    for i, j in taken:
        best = score[i, j]
        cx, cy = j + tw / 2, i + th / 2
        colscore = score[:, j]
        rows = np.flatnonzero(colscore >= 0.9 * best)
        rows = rows[np.abs(rows - i) < th]
        spread = (rows.max() - rows.min()) / 2 if len(rows) else 0.0
        e = mis + 3 + spread
        e += ANCHOR.get(colour, 0.0) * th
        cc = int(round(cx))
        half = CAP_HALF
        side = np.concatenate([m[:, cc - half:cc - STEM_HALF], m[:, cc + STEM_HALF + 1:cc + half + 1]], axis=1)
        caprows = [rr for rr in range(max(t, int(cy) - reach), min(b, int(cy) + reach))
                   if side[rr].sum() >= CAP_MIN and not (i - 4 <= rr <= i + th + 4)]
        above = [rr for rr in caprows if rr < cy]
        below = [rr for rr in caprows if rr > cy]
        note = f"template overlap {best / total:.2f}; calibration misfit {mis:.1f} px"
        rec = {"x": float(X.val(cx)), "y": float(Y.val(cy)), "lo": float(Y.val(cy + e)), "hi": float(Y.val(cy - e)),
               "px": [float(cx), float(cy)], "px_lo": float(cy - e), "px_hi": float(cy + e)}
        top = min(above) + CAP_T / 2 if above else None
        bot = max(below) - CAP_T / 2 if below else None
        if top is None and bot is None:
            note += "; no error-bar cap found (hidden behind other markers or bars)"
        else:
            if top is None:
                top = 2 * cy - bot
                note += "; upper cap hidden, mirrored from the lower"
            if bot is None:
                bot = 2 * cy - top
                note += "; lower cap hidden, mirrored from the upper"
            w = CAP_T / 2 + mis + 2
            rec.update({"bar_lo": float(Y.val(bot)), "bar_hi": float(Y.val(top)),
                        "bar_lo_outer": float(Y.val(bot + w)), "bar_hi_outer": float(Y.val(top - w))})
        rec["note"] = note
        out.append(rec)
    out.sort(key=lambda d: d["x"])
    return out
