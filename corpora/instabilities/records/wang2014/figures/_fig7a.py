"""Fig. 7(a) (PDF p. 5): experimentally observed initial modes placed on the calculated phase diagram
for lambda_p = 2: x = Gamma/(mu_s H_f) (log axis), y = mu_f/mu_s. Brown stars: wrinkling; green
diamonds: creasing; magenta triangles: delaminated buckling (legend).

Calibration (shared code in _wang.py): the black frame; x decade ticks 10^-1, 10^0, 10^1 inward from
the bottom frame (minor ticks are shorter and dropped by length), 10^2 at the right frame line;
y ticks 3, 6, 9, 12 inward from the left frame, 0 and 15 at the bottom and top frame lines.

Markers: template matching as in _fig3.py. The template is the legend's marker of the same colour;
its correlation with the colour mask (inside the frame widened by 60 px, since points at
mu_f/mu_s = 15 sit on the top frame line; the legend box blanked) is computed, and every local
maximum (no better one within a third of a marker) whose overlap is at least MIN_FRAC of the
template is a marker (overlapping pairs of triangles are about half a marker apart). Two markers
closer than a third of a marker would be read as one.
The centre of the matched template's box is the value (for triangles the anchor may be the
centroid, h/6 lower, which is added to the interval). Interval: +- (misfit + 3 px + h/6 for
triangles); the x interval is given in the note.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage, signal

SPEC = {"x": {"hi": 100, "ticks": [0.1, 1, 10], "major_len": 20, "log": True},
        "y": {"lo": 0, "hi": 15, "ticks": [3, 6, 9, 12]}}
LEGEND = (1385, 150, 2685, 600)
TEMPLATE_BOX = {"brown": (1490, 185, 1610, 285), "green": (1490, 320, 1610, 435), "magenta": (1490, 455, 1610, 545)}
# brown: the stars at x ~ 0.7 sit on the red boundary line, which hides part of them; green: one
# diamond near x ~ 2.8, mu_f/mu_s ~ 0.7 is partly under the black label 'Creasing' (overlap 0.59)
MIN_FRAC = {"brown": 0.45, "green": 0.55, "magenta": 0.6}
ANCHOR = {"magenta": 1 / 6}
MARGIN = 60


def _shared():
    spec = importlib.util.spec_from_file_location("wang2014_wang", Path(__file__).with_name("_wang.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mask(image, colour):
    a = np.asarray(image)[..., :3].astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if colour == "brown":
        return (r - b > 50) & (r - g > 40) & (r < 215) & (g > 15)
    if colour == "green":
        return (g - r > 80) & (g - b > 80)
    return (r - g > 80) & (b - g > 80)


def read_mode(image, colour):
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
    m = np.zeros_like(full)
    t, b = max(int(fr["top"][0]) - MARGIN, 0), int(fr["bottom"][1]) + MARGIN
    l, r = max(int(fr["left"][0]) - MARGIN, 0), int(fr["right"][1]) + MARGIN
    m[t:b, l:r] = full[t:b, l:r]
    lx0, ly0, lx1, ly1 = LEGEND
    m[ly0:ly1, lx0:lx1] = False
    score = signal.fftconvolve(m.astype(float), tpl[::-1, ::-1], mode="valid")
    total = tpl.sum()
    peak = ndimage.maximum_filter(score, size=(th // 3 * 2 + 1, tw // 3 * 2 + 1))
    cand = np.argwhere((score >= peak - 1e-6) & (score >= MIN_FRAC[colour] * total))
    taken = []
    for i, j in sorted(cand.tolist(), key=lambda ij: -score[ij[0], ij[1]]):
        if any(abs(i - a) < th / 3 and abs(j - c) < tw / 3 for a, c in taken):
            continue
        taken.append((i, j))
    out = []
    for i, j in taken:
        cx, cy = j + tw / 2, i + th / 2
        e = mis + 3 + ANCHOR.get(colour, 0.0) * th
        ex = mis + 3
        xv = float(X.val(cx))
        out.append({"x": xv, "y": float(Y.val(cy)), "lo": float(Y.val(cy + e)), "hi": float(Y.val(cy - e)),
                    "px": [float(cx), float(cy)], "px_lo": float(cy - e), "px_hi": float(cy + e),
                    "note": f"template overlap {score[i, j] / total:.2f}; x within [{X.val(cx - ex):.3g}, "
                            f"{X.val(cx + ex):.3g}]; calibration misfit {mis:.1f} px"})
    out.sort(key=lambda d: (d["x"], d["y"]))
    return out
