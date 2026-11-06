"""Shared reading code for Fig. 6 (p. 4), adapted from Murgo et al. [39].

Top: ascending aortic pressure of a type A and a type C beat; black line and grey line (one is
measured, the other derived from measured flow with the three-element windkessel; see figures.md).
Bottom: averaged input impedance modulus and phase of type A and type C beats: data points drawn
as dark-grey crosses (vertical and horizontal bars), joined by a black line, and the three-element
windkessel impedance as a light-grey line.

The figure is vector art with four inks: black (about 16 of 255: axes, ticks, the black lines),
dark grey (about 48: the crosses), light grey (about 168: the grey lines) and paper (248).

Calibration, all from the image:
  pressure panels: the y axis ticks (7 evenly spaced, matched to 120, 110, ..., 60 mmHg; the
    type A panel labels 120, 100, 80, 60 and the type C panel has the same ticks without labels)
    and the x ticks (11 evenly spaced, matched to 0, 0.1, ..., 1.0 s; labels 0, 0.2, ..., 1.0).
  impedance panels: y ticks matched to 200, 100, 0 (type A modulus), 100, 50, 0 (type C modulus)
    and 50, 0, -50 (phase); x ticks of each panel's own axis matched to 0, 5, 10 Hz. Only the
    phase axes carry frequency labels; each modulus axis has its own three ticks at the same
    spacing, the first on its y axis, so they are matched to 0, 5, 10 too (in the type C column
    the two panels' axes are offset by about 0.3 Hz, and the crosses follow each panel's own axis).
"""

import itertools

import numpy as np
from scipy import ndimage


# ---------------------------------------------------------------- helpers

def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    return a, b, float(np.max(np.abs((v - a) / b - p)))


def _pick_regular(cands, labels):
    n = len(labels)
    best = None
    for sub in itertools.combinations(sorted(cands), n):
        d = np.diff(sub)
        score = float(np.ptp(d)) / float(np.mean(d))
        if best is None or score < best[0]:
            best = (score, sub)
    if best is None:
        raise ValueError(f"found {len(cands)} tick candidates, need {n}")
    return list(zip(best[1], labels))


def inks(image):
    g = image[..., :3].astype(float).mean(axis=2)
    black = g < 32
    cross = (g >= 32) & (g < 80)
    light = (g > 130) & (g < 210)
    return g, black, cross, light


def _axes(black, r0, r1, c0, c1, ylen=300, tick_len=(12, 60)):
    """y axis (column band), x axis (row band) and tick candidates inside a region."""
    sub = black[r0:r1, c0:c1]
    best = None
    for c in range(sub.shape[1]):
        for a, b in _runs(sub[:, c]):
            if b - a >= ylen and (best is None or b - a > best[2] - best[1]):
                best = (c, a, b)
    yc, ya, yb = best
    cols = [c for c in range(max(0, yc - 30), min(sub.shape[1], yc + 30))
            if sub[ya:yb, c].mean() > 0.9]
    yl, yr = min(cols) + c0, max(cols) + 1 + c0
    ytop, ybot = ya + r0, yb + r0
    # x axis: the longest horizontal run near the y axis' bottom (or below it)
    bestx = None
    for r in range(ya + (yb - ya) // 2, sub.shape[0]):
        for a, b in _runs(sub[r]):
            if a + c0 <= yr + 40 and b - a > 0.5 * sub.shape[1] and (bestx is None or b - a > bestx[2] - bestx[1] + 3):
                bestx = (r, a, b)
    xr = bestx[0]
    rows = [r for r in range(xr - 20, min(sub.shape[0], xr + 20))
            if sub[r, bestx[1] + 50: bestx[2] - 50].mean() > 0.95]
    xt, xb = min(rows) + r0, max(rows) + 1 + r0
    xend = bestx[2] + c0
    # y ticks: short horizontal marks left of the y axis. The axis may lean slightly (the type C
    # phase axis moves about 10 px over its length), so its left edge is followed row by row.
    yc_abs = yc + c0
    pts = []
    for r in range(r0, min(r1, xt)):
        for a, b in _runs(black[r, max(0, yc_abs - 60): yc_abs + 60]):
            if 6 <= b - a <= 22:
                pts.append((r, a + max(0, yc_abs - 60)))
    pr = np.array(pts, float)
    k, q = np.polyfit(pr[:, 0], pr[:, 1], 1)
    probe = np.zeros(black.shape[0], bool)
    for r in range(r0, min(r1, xb + 1)):
        left = int(round(k * r + q))
        probe[r] = black[r, left - 14: left - 3].all()
    yticks = [(a + b) / 2.0 for a, b in _runs(probe) if b - a < 30]
    widths = []
    for r, a in pts:
        rr = int(r)
        run = [(s, e) for s, e in _runs(black[rr, int(a): int(a) + 30])]
        if run:
            widths.append(run[0][1] - run[0][0])
    axis_half = float(np.median(widths)) / 2.0 if widths else 6.0
    axis_col_at_xaxis = k * xt + q + axis_half
    # x ticks: short vertical marks below the x axis, from the y axis rightwards
    probe = black[xb + 3: xb + 12, :].all(axis=0)
    xticks = [(a + b) / 2.0 for a, b in _runs(probe) if max(c0, yl - 10) <= a < c1 and 3 <= b - a < 30]
    if yticks:
        ytop = min(ytop, int(min(yticks)))
    return dict(yl=yl, yr=yr, ytop=ytop, ybot=ybot, xt=xt, xb=xb, xend=xend, yticks=yticks, xticks=xticks,
                axis_col_at_xaxis=axis_col_at_xaxis)


# ---------------------------------------------------------------- pressure panels

def pressure_panel(image, which):
    """Axes of one pressure panel. The y labels are printed on the type A panel only, and the type C
    panel's own ticks are not evenly spaced (its 80 and 70 mmHg ticks sit about 38 and 20 px from where
    even spacing puts them), so both panels take their pressure scale from the type A ticks; the two
    y axes span the same rows (their top and bottom ticks agree within 5 px)."""
    g, black, cross, light = inks(image)
    H, W = black.shape
    half = W // 2
    axA = _axes(black, 0, H, 0, half)
    ymarks = _pick_regular(axA["yticks"], [120, 110, 100, 90, 80, 70, 60])
    ax = axA if which == "A" else _axes(black, 0, H, half, W)
    xmarks = _pick_regular([t for t in ax["xticks"] if t > ax["yl"] - 10], [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0])
    return g, black, light, ax, ymarks, xmarks


def _curve_mask(mask, ax, keep_largest):
    m = np.zeros_like(mask)
    r0, r1 = ax["ytop"] - 10, ax["xt"] - 6
    c0, c1 = ax["yr"] + 6, ax["xend"]
    m[r0:r1, c0:c1] = mask[r0:r1, c0:c1]
    if keep_largest:
        lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
        if n:
            sizes = ndimage.sum(m, lab, range(1, n + 1))
            m = lab == (1 + int(np.argmax(sizes)))
    return m


def _read_line(m, at, xa, xb, xmis, ya, yb, ymis, label, hide_note):
    # the line's full thickness: the median of its single vertical runs (mostly flat stretches)
    full = []
    for c in range(0, m.shape[1], 4):
        rr = _runs(m[:, c])
        if len(rr) == 1:
            full.append(rr[0][1] - rr[0][0])
    typical = float(np.percentile(full, 25)) if full else 0.0
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        runs = _runs(m[:, c]) if 0 <= c < m.shape[1] else []
        note = ""
        if len(runs) == 1:
            a, b = runs[0]
            gap = 0
        else:
            found = {}
            for d in range(1, 61):
                for s in (-1, 1):
                    k = c + s * d
                    if s not in found and 0 <= k < m.shape[1]:
                        rr = _runs(m[:, k])
                        if len(rr) == 1:
                            found[s] = (d, rr[0])
            if len(runs) > 1 or len(found) < 2:
                out.append({"x": x, "y": None, "note": f"{label} not found alone at this position ({len(runs)} runs)"})
                continue
            (dl, (al, bl)), (dr, (ar, br)) = found[-1], found[1]
            wl, wr = dr / (dl + dr), dl / (dl + dr)
            a, b = wl * al + wr * ar, wl * bl + wr * br
            gap = dl + dr
            note = f"{hide_note}; interpolated over {gap} px"
        row = (a + b) / 2.0
        nb = []
        for d in (-8, 8):
            k = c + d
            if 0 <= k < m.shape[1]:
                rr = _runs(m[:, k])
                if len(rr) == 1:
                    nb.append((rr[0][0] + rr[0][1]) / 2.0)
        slope = max([abs(v - row) / 8.0 for v in nb], default=0.0)
        e = 3.0 + ymis + xmis * slope + (0.5 * gap * slope if gap else 0.0) + (0.1 * gap if gap else 0.0)
        if not gap and (b - a) < typical - 2:
            # thinner than the full line: partly covered by the other line, so the centre may be off
            # by up to half the missing thickness
            e += (typical - (b - a)) / 2.0
            note = f"line thinner than its full {typical:.0f} px, partly covered; interval widened"
        out.append({"x": x, "y": ya + yb * row, "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
                    "px": [col, row], "px_lo": row - e, "px_hi": row + e,
                    "note": (note + f"; line {b - a:.0f} px tall here").strip("; ")})
    return out


def read_pressure(image, at, which, line):
    g, black, light, ax, ymarks, xmarks = pressure_panel(image, which)
    ya, yb, ymis = _fit(ymarks)
    xa, xb, xmis = _fit(xmarks)
    if line == "black":
        # the black ink inside the plot is the line and the panel title ("Type A"/"Type C"); the title
        # lies wholly above the 110 mmHg tick, the line wholly below it
        m = _curve_mask(black, ax, keep_largest=False)
        r110 = (110 - ya) / yb
        lab, n = ndimage.label(m, structure=np.ones((3, 3), bool))
        for i, sl in enumerate(ndimage.find_objects(lab), start=1):
            if sl[0].stop < r110 or (lab[sl] == i).sum() < 200:
                m[sl][lab[sl] == i] = False
        return _read_line(m, at, xa, xb, xmis, ya, yb, ymis, "black line", "black line not single here")
    m = _curve_mask(ndimage.binary_opening(light, structure=np.ones((7, 7), bool)), ax, keep_largest=False)
    return _read_line(m, at, xa, xb, xmis, ya, yb, ymis, "grey line", "grey line hidden under the black line")


# ---------------------------------------------------------------- impedance panels

YLABELS = {("A", "mod"): [200, 100, 0], ("C", "mod"): [100, 50, 0], ("A", "ph"): [50, 0, -50], ("C", "ph"): [50, 0, -50]}


def impedance_panel(image, which, panel):
    g, black, cross, light = inks(image)
    H, W = black.shape
    # the panels are split just below the modulus panel's x axis: the first row of mostly black ink
    long_rows = np.flatnonzero(black.sum(axis=1) > 0.5 * W)
    split = int(long_rows[0]) + 200
    r0, r1 = (0, split) if panel == "mod" else (split, H)
    ax = _axes(black, r0, r1, 0, W, ylen=300, tick_len=(22, 60))
    ymarks = _pick_regular(ax["yticks"], YLABELS[(which, panel)])
    if panel == "mod":
        # the modulus axis has ticks at 0 (on the y axis), 5 and 10
        xmarks = _pick_regular(ax["xticks"], [0, 5, 10])
    else:
        # the phase axis has ticks at 5 and 10 only; its y axis stands at 0 Hz (the label 0 is under
        # it), taken where the y axis line, extended, meets the x axis
        ticks = [t for t in ax["xticks"] if t > ax["axis_col_at_xaxis"] + 100]
        xmarks = [(ax["axis_col_at_xaxis"], 0)] + _pick_regular(ticks, [5, 10])
    return g, black, cross, light, ax, ymarks, xmarks


def read_model(image, at, which, panel):
    g, black, cross, light, ax, ymarks, xmarks = impedance_panel(image, which, panel)
    ya, yb, ymis = _fit(ymarks)
    xa, xb, xmis = _fit(xmarks)
    m = _curve_mask(ndimage.binary_opening(light, structure=np.ones((7, 7), bool)), ax, keep_largest=False)
    if panel == "ph":
        # the light-grey line starts on the y axis and runs below the axis' bottom tick; keep the band
        m[: ax["ytop"] - 10] = False
    return _read_line(m, at, xa, xb, xmis, ya, yb, ymis, "grey line", "grey line hidden under the black line or a cross")


def crosses(image, which, panel):
    g, black, cross, light, ax, ymarks, xmarks = impedance_panel(image, which, panel)
    r0, r1 = ax["ytop"] - 40, ax["xt"] - 4
    c0, c1 = ax["yr"] + 4, ax["xend"] + 60
    m = np.zeros_like(cross)
    m[r0:r1, c0:c1] = cross[r0:r1, c0:c1]
    # crosses are drawn on top of both lines, so each is whole: a horizontal bar (about 16 px thick)
    # and a vertical stem (about 14 px wide) through it
    horiz = ndimage.binary_opening(m, structure=np.ones((3, 22), bool))
    vert = ndimage.binary_opening(m, structure=np.ones((24, 3), bool))
    bars = []
    lab, n = ndimage.label(horiz)
    for sl in ndimage.find_objects(lab):
        top, bot, left, right = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if bot - top <= 30:
            bars.append(dict(top=top, bot=bot, left=left, right=right, r=(top + bot) / 2.0))
    stems = []
    lab, n = ndimage.label(vert)
    for sl in ndimage.find_objects(lab):
        if sl[1].stop - sl[1].start <= 30:
            stems.append(dict(c=(sl[1].start + sl[1].stop) / 2.0, top=sl[0].start, bot=sl[0].stop))
    # a stem cut in pieces by the light-grey line drawn over it is one stem
    stems.sort(key=lambda s: (s["c"], s["top"]))
    ms = []
    for s in stems:
        for t in ms:
            if abs(t["c"] - s["c"]) <= 8 and s["top"] - t["bot"] < 80 and t["top"] - s["bot"] < 80:
                t["top"], t["bot"] = min(t["top"], s["top"]), max(t["bot"], s["bot"])
                break
        else:
            ms.append(dict(s))
    found, used = [], set()
    for s in ms:
        # its bar: pieces crossing it or near it on its rows (the light-grey line, drawn over the
        # crosses, can hide part of a bar); the bar's row is the longest piece's
        hits = [i for i, b in enumerate(bars) if b["left"] - 40 <= s["c"] <= b["right"] + 40 and s["top"] - 6 <= b["r"] <= s["bot"] + 6]
        if hits:
            used.update(hits)
            bs = [bars[i] for i in hits]
            b = max(bs, key=lambda b: b["right"] - b["left"])
            found.append(dict(c=s["c"], r=b["r"], th=b["bot"] - b["top"], left=min(x["left"] for x in bs),
                              right=max(x["right"] for x in bs), top=min(s["top"], b["top"]), bot=max(s["bot"], b["bot"]),
                              kind="cross"))
        else:
            found.append(dict(c=s["c"], r=None, th=0, left=s["c"] - 7, right=s["c"] + 7, top=s["top"], bot=s["bot"], kind="stem only"))
    for i, b in enumerate(bars):
        if i in used:
            continue
        # a stem too short for the opening: cross ink just above or below the bar
        top, bot, left, right = b["top"], b["bot"], b["left"], b["right"]
        prot = m[max(0, top - 4), left:right] | m[min(m.shape[0] - 1, bot + 3), left:right]
        runs = [(a + left, e + left) for a, e in _runs(prot) if 4 <= e - a <= 30]
        if runs:
            a, e = max(runs, key=lambda r: r[1] - r[0])
            band = m[:, a:e].any(axis=1)
            st, sb = top, bot
            while st > 0 and band[st - 1]:
                st -= 1
            while sb < len(band) and band[sb]:
                sb += 1
            found.append(dict(c=(a + e) / 2.0, r=b["r"], th=bot - top, left=left, right=right, top=st, bot=sb, kind="cross"))
        else:
            found.append(dict(c=(left + right) / 2.0, r=b["r"], th=bot - top, left=left, right=right, top=top, bot=bot, kind="bar only"))
    # one cross found twice (a stem piece and a bar piece side by side): merge
    found.sort(key=lambda f: f["c"])
    merged = []
    for f in found:
        for t in merged:
            if abs(t["c"] - f["c"]) <= 14 and f["top"] <= t["bot"] + 10 and t["top"] <= f["bot"] + 10:
                stem = t if t["kind"] != "bar only" else f
                bar = t if t["r"] is not None and t["kind"] != "stem only" else (f if f["r"] is not None else None)
                t.update(c=stem["c"], top=min(t["top"], f["top"]), bot=max(t["bot"], f["bot"]),
                         left=min(t["left"], f["left"]), right=max(t["right"], f["right"]))
                if bar is not None:
                    t.update(r=bar["r"], th=bar["th"], kind="cross")
                break
        else:
            merged.append(dict(f))
    # a stem with no bar found by the opening: look for a short bar (rows where the ink is wider than the stem)
    for f in merged:
        if f["kind"] != "stem only":
            continue
        c = int(round(f["c"]))
        w = m[f["top"]: f["bot"], c - 40: c + 41].sum(axis=1)
        sw = float(np.median(w))
        rows = np.flatnonzero(w >= sw + 8)
        if len(rows):
            runs = _runs(np.isin(np.arange(len(w)), rows))
            a, e = max(runs, key=lambda r: r[1] - r[0])
            cols = np.flatnonzero(m[f["top"] + a: f["top"] + e, c - 40: c + 41].any(axis=0))
            f.update(r=f["top"] + (a + e) / 2.0, th=e - a, left=c - 40 + int(cols.min()), right=c - 40 + int(cols.max()) + 1,
                     kind="cross")
    return g, black, ax, ymarks, xmarks, merged


def read_points(image, which, panel):
    g, black, ax, ymarks, xmarks, found = crosses(image, which, panel)
    ya, yb, ymis = _fit(ymarks)
    xa, xb, xmis = _fit(xmarks)
    # a lone dash with no vertical bar lying within another cross's horizontal extent (one such in
    # the type C modulus panel, below the end of the black line) is not taken as a data point
    crosses_ = [f for f in found if f["kind"] == "cross"]
    found = [f for f in found if not (f["kind"] == "bar only" and any(
        c["left"] - 5 <= f["left"] and f["right"] <= c["right"] + 5 for c in crosses_))]
    out = []
    for f in sorted(found, key=lambda f: f["c"]):
        xl, xr = xa + xb * f["left"], xa + xb * f["right"]
        if f["kind"] == "cross":
            row = f["r"]
            e = 2.0 + ymis + f["th"] / 4.0
            note = f"cross; horizontal bar from {xl:.2f} to {xr:.2f} Hz"
            top, bot = f["top"], f["bot"]
        elif f["kind"] == "bar only":
            row = f["r"]
            e = 2.0 + ymis + f["th"] / 4.0
            top, bot = f["top"], f["bot"]
            note = (f"no vertical bar visible beyond the horizontal bar (from {xl:.2f} to {xr:.2f} Hz): the error bar "
                    "is reported as at most the bar's thickness; x taken at the bar's middle")
        else:
            row = (f["top"] + f["bot"]) / 2.0
            e = 2.0 + ymis + (f["bot"] - f["top"]) / 4.0
            top, bot = f["top"], f["bot"]
            note = "vertical bar with no horizontal bar: the point is taken at the bar's middle"
        # the light-grey line is drawn over the crosses: where it covers an end of the vertical bar,
        # the end may lie anywhere under it; where it covers the horizontal bar, the bar's row is
        # known only to the covered band
        light = (g > 130) & (g < 210)
        c = int(round(f["c"]))
        colL = light[:, c - 2: c + 3].any(axis=1)
        out_top, out_bot = top - 3 - ymis, bot + 3 + ymis
        hidden = []
        if colL[max(0, top - 4): top + 1].any():
            k = top - 4
            while k > 0 and colL[k]:
                k -= 1
            out_top = k - ymis
            hidden.append("upper end")
        if colL[bot - 1: bot + 4].any():
            k = bot + 3
            while k < len(colL) - 1 and colL[k]:
                k += 1
            out_bot = k + ymis
            hidden.append("lower end")
        if f["kind"] != "stem only" and colL[int(row - f["th"]): int(row + f["th"]) + 1].any() and f["th"] < 14:
            e += 8.0
            hidden.append("part of the horizontal bar")
        if hidden:
            note += "; the grey line covers the " + " and the ".join(hidden)
        out.append({"x": xa + xb * f["c"], "y": ya + yb * row,
                    "lo": ya + yb * (row + e), "hi": ya + yb * (row - e),
                    "px": [f["c"], row], "px_lo": row - e, "px_hi": row + e,
                    "bar_lo": ya + yb * bot, "bar_hi": ya + yb * top,
                    "bar_lo_outer": ya + yb * out_bot, "bar_hi_outer": ya + yb * out_top,
                    "note": note})
    return out
