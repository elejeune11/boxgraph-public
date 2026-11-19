"""Fig. 5D (PDF p. 7), lower right: anti-SHH staining intensity in the 5 um x 5 um box below the E15 fold
base (yellow bar, x = 1) and below the tip (pink bar, x = 2), mean +- 1 SD error bars. Embedded raster of
about 300 dpi rendered at 1200 dpi.

Calibration (y): grey level g = brightest channel. The y axis is the grey vertical line (g < 200) with the
longest run; ticks are the row groups where the 4 px just left of it are ink. They are matched, top to
bottom, to the printed labels 6, 4, 2 and the x axis 0; a line is fitted and its rms misfit (px) widens every
interval.

Bars: colour masks (yellow: R > 200, G > 200, B < 120; pink: R > 170, 60 < G < 170, B > 110, R - G > 50).
A bar's columns are those where its mask fills the row 8 px above the x axis; its top edge is the median,
over the columns at 15-35% and 65-85% of its width, of the first masked row from the top (minus 0.5 px);
+-4 px (the raster block) plus the misfit is its interval.

Error bars: thin dark lines (g < 120) over the bar's middle half. The stem is the column with most dark
pixels; the upper and lower ends are the topmost and bottommost dark rows within +-8 px of it (the caps),
read at the cap centre (2 px inside the end) with +-(4 px + misfit). Both ends are visible on both bars; the
note gives the error bar's midpoint against the bar top (an SD bar is centred on the mean), and the mean's
interval is widened to include that midpoint.
"""

import numpy as np


def _groups(idx, gap=1):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(int(i))
        else:
            out.append([int(i)])
    return out


def _longest(v):
    best = cur = 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def read(image, at):
    im = np.asarray(image)[..., :3].astype(int)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    g = im.max(axis=2)
    H, W = g.shape
    ink = g < 200
    vr = np.array([_longest(ink[:, c]) for c in range(W)])
    c0 = int(np.argmax(vr))
    while vr[c0 - 1] > 0.5 * vr[c0]:
        c0 -= 1
    rows = [r for r in range(H) if ink[r, c0 - 4:c0].all()]
    ticks = [(t[0] + t[-1]) / 2.0 for t in _groups(rows) if len(t) <= 16]
    labels = [6, 4, 2, 0]
    if len(ticks) != 4:
        raise RuntimeError(f"expected 4 ticks, found {ticks}")
    b, a = np.polyfit(ticks, labels, 1)
    mis = max(float(np.sqrt(np.mean(((np.array(labels) - (a + b * np.array(ticks))) / b) ** 2))), 0.5)
    val = lambda r: float(a + b * r)   # noqa: E731
    span = lambda r, t: sorted([val(r - t - mis), val(r + t + mis)])   # noqa: E731
    xrow = int(round(ticks[-1]))
    masks = {1.0: (R > 200) & (G > 200) & (B < 120),
             2.0: (R > 170) & (G > 60) & (G < 170) & (B > 110) & (R - G > 50)}
    out = []
    for xv in at:
        x = float(xv)
        m = masks[x]
        cols = np.where(m[xrow - 8])[0]
        grp = max(_groups(list(cols)), key=len)
        l, r = grp[0], grp[-1]
        w = r - l + 1
        side = [c for c in range(l, r + 1) if 0.15 <= (c - l) / w <= 0.35 or 0.65 <= (c - l) / w <= 0.85]
        tops = [np.where(m[:xrow, c])[0].min() - 0.5 for c in side]
        top = float(np.median(tops))
        dark = g[:xrow, l + w // 4: r - w // 4 + 1] < 120
        sc = l + w // 4 + int(np.argmax(dark.sum(axis=0)))
        dr = np.where((g[:xrow, sc - 8:sc + 9] < 120).any(axis=1))[0]
        up, dn = float(dr.min() + 2), float(dr.max() - 2)
        mid = (up + dn) / 2.0
        lo, hi = span(top, 4.0)
        mlo, mhi = span(mid, 2.0)
        out.append({"x": x, "y": val(top), "lo": min(lo, mlo), "hi": max(hi, mhi), "px": [float((l + r) / 2), top],
                    "bar_lo": val(dn), "bar_hi": val(up), "bar_lo_outer": span(dn, 4.0)[0],
                    "bar_hi_outer": span(up, 4.0)[1], "px_lo": up, "px_hi": dn,
                    "note": f"bar columns {l}-{r}, top edge row {top:.1f}; error bar rows {dr.min()}-{dr.max()} at "
                            f"column {sc}, midpoint {mid:.1f} ({mid - top:+.1f} px from the top); misfit {mis:.2f} px"})
    return out
