"""Reading code for Fig. S7 of cao2017 (PDF p. 12): normalized FA size, experimental bars (solid
grey or black, with error bars) and model bars (hatched), each outlined in black.

Everything is found in the image:
  y axis    the left spine is the longest dark vertical run in the left part of the crop; the
            ticks are the dark rows just right of it (they point into the plot box), each at
            its darkness-weighted centre (the top and bottom ticks lie on the frame lines). They are evenly spaced, labelled 0, 1, 2, 3 with
            unlabelled ticks halfway; all seven are matched in order to 3, 2.5, ..., 0. A linear
            fit gives the calibration and its misfit (largest residual, at least half a pixel).
  bars      each column of the plot box is classed by the rows just above the x axis: solid grey
            (mid grey, little variation), solid black, or hatched (alternating dark and light).
            Runs of one class wider than `min_width` are bars, left to right. A bar's top is
            found in columns away from its centre (avoiding the error bar and its caps): walking
            up from inside the bar to where the paper begins (70 light rows in a row, more than
            the white gaps of the hatching), the topmost
            dark run is the outline; its upper edge (half-way crossing) plus half the outline
            thickness is the bar's value. The outline thickness is the median length of the top
            dark run over the solid grey bars' columns.
  error     the stem above a solid bar's centre is walked upward while dark; the cap is the
            stroke at its end, at the darkness-weighted centre of the cap beside the stem. Below
            the top, on a grey bar the dark stem is walked down to its lower cap; inside a black bar
            the stem cannot be seen, and the lower end is mirrored from the upper.

Intervals (95%): half the outline's edge blur, the spread of the top over the sampled columns,
the calibration misfit, and one pixel.
"""
import numpy as np


def _gray(img):
    return img.astype(float).mean(axis=2)


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def _axis(g):
    H, W = g.shape
    dark = g < 100
    best = (0, 0, 0, 0)
    for c in range(int(0.3 * W)):
        for grp in _groups(np.where(dark[:, c])[0], gap=2):
            n = grp[-1] - grp[0] + 1
            if n > best[0]:
                best = (n, c, grp[0], grp[-1])
    n, c, r0, r1 = best
    cols = [cc for cc in range(max(c - 25, 0), c + 25) if dark[r0 + n // 4:r1 - n // 4, cc].mean() > 0.9]
    c0, c1 = min(cols), max(cols)
    probe = c1 + 12  # the ticks point into the plot box
    d = 255.0 - g[:, probe - 2:probe + 3].mean(axis=1)
    ticks = []
    for grp in _groups(np.where(d > 60)[0], gap=2):
        if len(grp) > 40:
            continue
        lo, hi = grp[0] - 3, grp[-1] + 4
        w = d[lo:hi]
        ticks.append(float((np.arange(lo, hi) * w).sum() / w.sum()) + 0.5)
    labels = np.array([3, 2.5, 2, 1.5, 1, 0.5, 0], float)
    if len(ticks) != len(labels):
        raise ValueError(f"found {len(ticks)} ticks for {len(labels)} labels")
    b, a = np.polyfit(labels, ticks, 1)
    misfit = max(float(np.max(np.abs(np.array(ticks) - (a + b * labels)))), 0.5)
    return {"a": a, "b": b, "misfit": misfit, "ticks": ticks, "c1": c1, "base": a}


def _val(ax, p):
    return float((p - ax["a"]) / ax["b"])


def _classes(g, ax):
    base = int(round(ax["base"]))
    win = g[base - 260:base - 30]
    mean, std = win.mean(axis=0), win.std(axis=0)
    cls = np.full(g.shape[1], "", dtype=object)
    cls[(std > 40)] = "hatch"
    cls[(std <= 25) & (mean < 90)] = "black"
    cls[(std <= 25) & (mean >= 140) & (mean <= 215)] = "grey"
    cls[:ax["c1"] + 5] = ""
    return cls


def _bars(g, ax, kinds, min_width):
    cls = _classes(g, ax)
    out = []
    for k in kinds:
        for grp in _groups(np.where(cls == k)[0], gap=4):
            if len(grp) >= min_width:
                out.append((int(grp[0]), int(grp[-1]), k))
    out.sort()
    return out


def _top(g, c, start):
    """Upper edge (half-way crossing) and length of the topmost dark run below the paper, in column c."""
    col = g[:, c]
    r, light = start, 0
    last_dark = None
    while r > 0:
        if col[r] > 200:
            light += 1
            if light >= 70:
                break
        else:
            light = 0
            if col[r] < 100:
                last_dark = r
        r -= 1
    if last_dark is None:
        return None
    k = last_dark
    while col[k] < 128 and k < len(col) - 1:
        k += 1
    length = k - last_dark
    a, b = col[last_dark - 1], col[last_dark]
    edge = (last_dark - 1) + (a - 128.0) / (a - b) + 0.5 if a != b else float(last_dark)
    r10 = next((i for i in range(last_dark - 6, last_dark + 6) if col[i] < 255 - 0.1 * (255 - col[last_dark + 1])), last_dark)
    r90 = next((i for i in range(last_dark - 6, last_dark + 6) if col[i] < 255 - 0.9 * (255 - col[last_dark + 1])), last_dark)
    return edge, length, abs(r90 - r10)


def read(image, at, kinds, error_bars):
    g = _gray(image)
    ax = _axis(g)
    base = int(round(ax["base"]))
    bars = _bars(g, ax, kinds, 120)
    # outline thickness from the solid grey bars (their top dark run is the outline alone)
    thick = []
    for a_, b_, k in _bars(g, ax, ["grey"], 120):
        w = b_ - a_ + 1
        for c in list(range(a_ + w // 10, a_ + 3 * w // 10)) + list(range(b_ - 3 * w // 10, b_ - w // 10)):
            t = _top(g, c, base - 40)
            if t:
                thick.append(t[1])
    t_out = float(np.median(thick))
    out = []
    for i, (a_, b_, k) in enumerate(bars):
        w = b_ - a_ + 1
        cc = 0.5 * (a_ + b_) + 0.5
        cols = list(range(a_ + w // 10, a_ + 3 * w // 10)) + list(range(b_ - 3 * w // 10, b_ - w // 10))
        res = [t for t in (_top(g, c, base - 40) for c in cols) if t]
        edges = np.array([t[0] for t in res])
        blur = float(np.median([t[2] for t in res]))
        edge = float(np.median(edges))
        top = edge + 0.5 * t_out
        spread = float(np.percentile(edges, 95) - np.percentile(edges, 5))
        e = 0.5 * blur + 0.5 * spread + ax["misfit"] + 1.0
        y = _val(ax, top)
        v1, v2 = _val(ax, top - e), _val(ax, top + e)
        rec = {"x": float(i + 1), "y": y, "lo": min(v1, v2), "hi": max(v1, v2), "px": [cc, top],
               "note": f"{k} bar, {w} px wide: outline centre (edge + {0.5 * t_out:.1f} px), spread {spread:.1f} px; "
                       f"y misfit {ax['misfit']:.1f} px ({len(ax['ticks'])} ticks)"}
        if error_bars:
            ci = int(round(cc))
            stem = g[:, ci - 3:ci + 4].min(axis=1)
            r, last, gap = int(edge) - 3, None, 0
            while r > 0 and gap <= 6:
                if stem[r] < 110:
                    last, gap = r, 0
                else:
                    gap += 1
                r -= 1

            def cap_row(near):
                side = 255.0 - g[near - 20:near + 20, ci + 14:ci + 24].mean(axis=1)
                d = np.clip(side - 40, 0, None)
                return float((np.arange(near - 20, near + 20) * d).sum() / d.sum()) + 0.5 if d.sum() else float(near)

            if last is not None and edge - last > 15:
                up = cap_row(last + 4)
                note = "; upper error bar end at its cap"
                if k == "grey":
                    r, low, gap = int(edge + t_out) + 3, None, 0
                    while r < base - 3 and gap <= 6:
                        if stem[r] < 110:
                            low, gap = r, 0
                        else:
                            gap += 1
                        r += 1
                    dn = cap_row(low - 4) if low is not None else 2 * top - up
                    note += "; lower end at its cap, drawn over the grey bar" if low is not None else "; lower end not found: mirrored"
                else:
                    dn = 2 * top - up
                    note += "; lower end hidden in the black bar: mirrored from the upper"
                hi_v, lo_v = _val(ax, up), _val(ax, dn)
                pp = (2.5 + ax["misfit"]) / abs(ax["b"])
                rec.update({"bar_lo": lo_v, "bar_hi": hi_v, "bar_lo_outer": lo_v - pp, "bar_hi_outer": hi_v + pp,
                            "px_lo": up, "px_hi": dn})
                rec["note"] += note
            else:
                rec["note"] += "; no error bar found above the bar"
        out.append(rec)
    return out
