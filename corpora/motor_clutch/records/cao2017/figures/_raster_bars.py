"""Shared code for the raster bar charts of cao2017 (Fig. 5D, adapted from ref. 16, and Fig. S7).

Everything is found in the image:
  y axis    the left spine is the longest vertical run of non-white, unsaturated pixels in
            the left part of the crop; the tick marks are the dark rows a little left of it
            (a column between the labels and the spine). Each tick's row is the darkness-
            weighted centre of its run. The ticks are matched in order to the printed labels
            the stub gives (the only paper values used); a linear fit gives the calibration
            and its misfit (largest residual, at least half a pixel).
  bars      on a row just above the x axis, the runs of bar-coloured pixels wider than
            `min_width` are the bars, left to right. A bar's top is where, in columns between
            its centre and its edges (the error bar stem is avoided), the profile from the
            paper colour to the bar colour crosses half way (interpolated). The bar colour is
            read from the bar itself.
  error     the stem above a bar's centre is walked upward while it is darker than half way
            between paper and stem; the cap is the horizontal stroke at its end, and its row
            is the darkness-weighted centre of the cap a little beside the stem. The lower end
            is inside the bar (not drawn or not visible): it is mirrored from the upper.

Intervals (95%): the bar top's edge blur (half the rows over which the profile goes from 10%
to 90% of the way), the spread of the top over the sampled columns, the calibration misfit,
and one pixel.
"""
import numpy as np


def gray(img):
    return img.astype(float).mean(axis=2)


def sat(img):
    f = img.astype(float)
    return f.max(axis=2) - f.min(axis=2)


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def left_spine(img, spec):
    g = gray(img)
    ink = (g < spec.get("ink", 215)) & (sat(img) < 40)
    H, W = g.shape
    best = (0, 0, 0, 0)
    for c in range(int(spec.get("spine_search", 0.4) * W)):
        on = np.where(ink[:, c])[0]
        for grp in _groups(on, gap=2):
            n = grp[-1] - grp[0] + 1
            if n > best[0]:
                best = (n, c, grp[0], grp[-1])
    n, c, r0, r1 = best
    cols = [cc for cc in range(max(c - 15, 0), c + 15)
            if ink[r0 + n // 4:r1 - n // 4, cc].mean() > 0.9]
    return min(cols), max(cols), r0, r1


def y_axis(img, spec):
    g = gray(img)
    c0, c1, r0, r1 = left_spine(img, spec)
    col = c0 - spec.get("tick_probe", 18)
    dark = 255.0 - g[:, col - 2:col + 3].mean(axis=1)
    on = np.where(dark > spec.get("tick_dark", 40))[0]
    ticks = []
    for grp in _groups(on, gap=2):
        if len(grp) > 40:
            continue
        lo, hi = grp[0] - 3, grp[-1] + 4
        w = dark[lo:hi]
        ticks.append(float((np.arange(lo, hi) * w).sum() / w.sum()) + 0.5)
    labels = np.array(spec["y_labels"], float)
    if len(ticks) != len(labels):
        raise ValueError(f"found {len(ticks)} ticks for {len(labels)} labels")
    b, a = np.polyfit(labels, ticks, 1)
    misfit = max(float(np.max(np.abs(np.array(ticks) - (a + b * labels)))), 0.5)
    return {"a": a, "b": b, "misfit": misfit, "ticks": ticks, "spine": (c0, c1, r0, r1)}


def to_val(ax, p):
    return float((p - ax["a"]) / ax["b"])


def _crossing(prof, level, start):
    """From row `start` (inside the bar) upward, the first row where the profile passes `level`
    (from the bar's side to the paper's side), interpolated; rows are pixel centres + 0.5."""
    for r in range(start, 0, -1):
        a, b = prof[r - 1], prof[r]
        if (a - level) * (b - level) <= 0 and a != b:
            return (r - 1) + (a - level) / (a - b) + 0.5
    return None


def read_bars(img, at, spec):
    ax = y_axis(img, spec)
    g = gray(img)
    H, W = g.shape
    c0s, c1s, sr0, sr1 = ax["spine"]
    base = ax["a"] + ax["b"] * min(spec["y_labels"])       # the row of the lowest tick (0)
    probe = int(base - spec.get("base_probe", 25))
    lo_g, hi_g = spec["bar_gray"]                           # range of grey levels of the bars read
    row = g[probe]
    is_bar = (row >= lo_g) & (row <= hi_g) & (sat(img)[probe] < 40)
    is_bar[:c1s + 6] = False
    for a_, b_ in spec.get("skip_cols", []):
        is_bar[a_:b_] = False
    runs = [grp for grp in _groups(np.where(is_bar)[0], gap=3) if len(grp) >= spec.get("min_width", 60)]
    cats = spec["categories"]
    if len(runs) != len(cats):
        return [{"x": float(v), "y": None, "note": f"found {len(runs)} bars for {len(cats)} categories"} for v in cats]
    out = []
    for grp, x in zip(runs, cats):
        a_, b_ = int(grp[0]), int(grp[-1])
        w = b_ - a_ + 1
        cc = 0.5 * (a_ + b_) + 0.5
        bar_level = float(np.median(g[probe - 40:probe, a_ + w // 4:b_ - w // 4]))
        paper = 255.0
        level = 0.5 * (paper + bar_level)
        cols = list(range(a_ + w // 6, a_ + 2 * w // 5)) + list(range(b_ - 2 * w // 5 + 1, b_ - w // 6 + 1))
        tops, blurs = [], []
        for c in cols:
            prof = g[:, c]
            # from inside the bar upward: where the bar ends
            t = _crossing(prof, level, probe)
            if t is None:
                continue
            t10 = _crossing(prof, paper - 0.1 * (paper - bar_level), probe)
            t90 = _crossing(prof, paper - 0.9 * (paper - bar_level), probe)
            tops.append(t)
            if t10 is not None and t90 is not None:
                blurs.append(abs(t90 - t10))
        top = float(np.median(tops))
        spread = float(np.percentile(tops, 95) - np.percentile(tops, 5))
        blur = float(np.median(blurs)) if blurs else 4.0
        e = 0.5 * blur + 0.5 * spread + ax["misfit"] + 1.0
        y = to_val(ax, top)
        v1, v2 = to_val(ax, top - e), to_val(ax, top + e)
        rec = {"x": float(x), "y": y, "lo": min(v1, v2), "hi": max(v1, v2), "px": [cc, top],
               "note": f"bar top (half-way crossing), {w} px wide, edge blur {blur:.1f} px, spread {spread:.1f} px; "
                       f"y misfit {ax['misfit']:.1f} px ({len(ax['ticks'])} ticks)"}
        # the error bar above the bar's centre
        ci = int(round(cc))
        stem = 255.0 - g[:, ci - 3:ci + 4].min(axis=1)
        thr = spec.get("stem_dark", 60)
        r = int(top) - 4
        last, gap = None, 0
        while r > 0 and gap <= 8:
            if stem[r] > thr:
                last, gap = r, 0
            else:
                gap += 1
            r -= 1
        if last is not None and top - last > 15:
            side = g[last - 25:last + 25, ci + 10:ci + 18].mean(axis=1)
            d = np.clip(255.0 - side - 20, 0, None)
            cap = float((np.arange(last - 25, last + 25) * d).sum() / d.sum()) + 0.5 if d.sum() > 0 else float(last)
            hi_v = to_val(ax, cap)
            lo_v = 2 * y - hi_v
            pp = (2.5 + ax["misfit"]) / abs(ax["b"])
            rec.update({"bar_lo": lo_v, "bar_hi": hi_v, "bar_lo_outer": lo_v - pp, "bar_hi_outer": hi_v + pp,
                        "px_lo": cap, "px_hi": 2 * top - cap})
            rec["note"] += "; upper error bar end at the cap's centre; lower end inside the bar, mirrored"
        else:
            rec["note"] += "; no error bar found above the bar"
        out.append(rec)
    return out
