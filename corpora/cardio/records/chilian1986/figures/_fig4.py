"""Shared reading code for Fig. 4 (PDF p. 7): two bar charts, control (filled bar) and
papaverine (open bar), each bar with an upper error bar. Left panel: myocardial perfusion
(ticks 0, 100, ..., 400); right panel: coronary resistance (ticks 0, 0.2, ..., 1.0).

The figure is a clean black-and-white print: ink is darker than 128.

Calibration, from the image:
- the y axis is the longest vertical run of ink (the leftmost column whose ink count is at least
  90% of the maximum); the x axis is the longest horizontal row of ink below it;
- the ticks point right, into the plot: rows where a band 15-60 px right of the y axis is all ink.
  Grouped into runs, their centres (from the x axis upwards; the x axis itself is the 0 tick) are
  matched in order to the printed labels `labels`. A straight line is fitted; the largest misfit
  (in px) widens every interval.

Bars: on the row 60 px above the x axis, the ink runs between the y axis and the right end of
the x axis are the bar sides. A run wider than 60 px is a filled bar; two narrow runs next to
each other are the sides of an open bar. Bars are numbered from the left (1 = control,
2 = papaverine, as the axis labels under them read).

A bar's value is its top edge, found in the columns at 10% and 90% of the bar's width (away from
the error bar cap): for an open bar, the centre of the topmost run of ink (the top line);
for a filled bar, the top of the ink run plus half the line width (the outline is drawn
centred on the value, like the open bar's top line). The line width is that of the open bar's
side. Interval: half the line width + 2 px + misfit, and the difference between the two
columns.

The error bar is the vertical stem rising from the bar's top near its centre: its upper end is the
centre of the cap (the topmost ink in the stem's column). The lower half of the error bar is
hidden inside the bar and is taken as the mirror of the upper about the bar's value.
"""

import numpy as np

INK = 128


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def calibrate(image, labels):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < INK
    H, W = ink.shape
    cs = ink.sum(axis=0)
    long_cols = np.flatnonzero(cs >= 0.9 * cs.max())
    ya0, ya1 = _runs(np.isin(np.arange(W), long_cols))[0]  # y axis columns [ya0, ya1)
    rs = ink[:, ya1:].sum(axis=1)
    long_rows = np.flatnonzero(rs >= 0.9 * rs.max())
    xa0, xa1 = _runs(np.isin(np.arange(H), long_rows))[-1]  # x axis rows [xa0, xa1)
    xa_end = ya1 + max(e for s, e in _runs(ink[(xa0 + xa1) // 2, ya1:]))
    band = ink[:, ya1 + 15: ya1 + 60].all(axis=1)
    ticks = sorted(((a + b - 1) / 2.0 for a, b in _runs(band) if b - a < 40), reverse=True)
    if len(ticks) != len(labels):
        raise RuntimeError(f"expected {len(labels)} ticks, found {len(ticks)}: {ticks}")
    p = np.array(ticks)
    v = np.array(labels, float)
    b, a = np.polyfit(p, v, 1)  # value = a + b * row
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    row = xa0 - 60
    # runs touching the start of the row are the y axis line itself (a little thicker near the bottom)
    sides = [(s + ya1 + 5, e + ya1 + 5) for s, e in _runs(ink[row, ya1 + 5: xa_end - 5]) if s > 0]
    bars, lw, i = [], None, 0
    while i < len(sides):
        s, e = sides[i]
        if e - s > 60:
            bars.append((s, e, "filled"))
            i += 1
        else:
            s2, e2 = sides[i + 1]
            bars.append((s, e2, "open"))
            lw = e - s
            i += 2
    return dict(ink=ink, a=a, b=b, mis=mis, bars=bars, lw=lw, top=min(ticks), xa0=xa0, ticks=ticks)


def _val(cal, row):
    return cal["a"] + cal["b"] * row


def read_bar(image, at, labels):
    cal = calibrate(image, labels)
    ink, lw = cal["ink"], cal["lw"]
    out = []
    for x in at:
        k = int(round(x)) - 1
        c0, c1, kind = cal["bars"][k]
        w = c1 - c0
        tops = []
        for f in (0.10, 0.90):
            c = int(round(c0 + f * w))
            col = ink[int(cal["top"]) - 60: cal["xa0"] - 30, c]
            r0, r1 = _runs(col)[0]
            r0 += int(cal["top"]) - 60
            r1 += int(cal["top"]) - 60
            tops.append((r0 + r1 - 1) / 2.0 if kind == "open" else r0 + lw / 2.0)
        top = float(np.mean(tops))
        tol = lw / 2.0 + 2 + cal["mis"] + abs(tops[0] - tops[1]) / 2.0
        y = _val(cal, top)
        lo, hi = sorted((_val(cal, top + tol), _val(cal, top - tol)))
        # the error bar stem: the ink column nearest the centre that rises above the top edge
        cc = (c0 + c1) // 2
        probe = int(top - lw - 15)
        cols = [c for c in range(cc - 60, cc + 61) if ink[probe, c]]
        if not cols:
            out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(cc), top],
                        "note": f"bar {k + 1} ({kind}): no error bar found above the bar"})
            continue
        sc = int(round(np.mean(cols)))
        stem = ink[: probe + 1, sc]
        # walk up the stem from the probe while ink continues (gaps up to 2 px)
        r, gap = probe, 0
        while r > 0 and gap <= 2:
            r -= 1
            gap = 0 if stem[r] else gap + 1
        cap_top = r + gap + 1
        # cap thickness: the ink run in a column beside the stem at the cap
        cap = [(s, e) for s, e in _runs(ink[:, sc + int(lw) + 6]) if s <= cap_top + lw and e >= cap_top]
        cap_bot = cap[0][1] if cap else cap_top + lw
        cap_c = (cap_top + cap_bot - 1) / 2.0
        ctol = (cap_bot - cap_top) / 2.0 + 2 + cal["mis"]
        hi_end = _val(cal, cap_c)
        lo_end = 2 * y - hi_end
        hi_out = _val(cal, cap_c - ctol)
        lo_out = 2 * _val(cal, top + tol) - hi_out
        out.append({
            "x": x, "y": y, "lo": lo, "hi": hi, "px": [float(sc), top],
            "bar_lo": min(lo_end, hi_end), "bar_hi": max(lo_end, hi_end),
            "bar_lo_outer": min(lo_out, lo_end), "bar_hi_outer": max(hi_out, hi_end),
            "px_lo": cap_c, "px_hi": 2 * top - cap_c,
            "note": (f"bar {k + 1} ({kind}); cap centre at row {cap_c:.1f}; the lower half of the error bar is "
                     f"hidden inside the bar and taken as the mirror of the upper; "
                     f"{len(cal['ticks'])} ticks, misfit {cal['mis']:.2f} px"),
        })
    return out
