"""Fig. 5e (PDF p. 10): the five black bars (mean recoil velocity) and their error bars (SD).

Calibration, all from the image:
  frame: the longest dark lines on each side;
  y: the inward tick marks on the left frame line, matched top to bottom to the printed labels
     3, 2.5, 2, 1.5, 1, 0.5, with the bottom frame line carrying 0 (fitted; misfit reported);
  x: the bars stand on the labelled positions -16, -8, 0, 8, 16 (left to right); each bar is
     read as its category, so x needs no pixel calibration.
Bars: the black fill standing on the bottom frame line. A bar's top is the topmost black pixel of
the run of black (or of the coloured circles drawn over it) that rises from the bottom frame,
column by column across the bar away from its middle (where the error bar rises); the median.
Error bars: the thin black line rising from the bar's top along its middle; circles drawn over it
are bridged; its upper end is the middle of the cap (rows where black spans more than three line
widths). The lower half lies inside the black bar and cannot be seen: it is taken as the mirror
of the upper half about the bar's top, and the reading says so.
95% interval of a bar top: 2 px plus the calibration misfit; error bar ends: 3 px plus misfit.
"""
import numpy as np

Y_LABELS = [3.0, 2.5, 2.0, 1.5, 1.0, 0.5]   # matched: the y tick labels, top to bottom
BOTTOM = 0.0                                # matched: the label at the bottom frame line
X_LABELS = [-16.0, -8.0, 0.0, 8.0, 16.0]    # matched: the bar labels, left to right


def _runs(v):
    idx = np.where(v)[0]
    if not len(idx):
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i != p + 1:
            out.append((s, p))
            s = i
        p = i
    out.append((s, p))
    return out


def _frame(blk):
    H, W = blk.shape
    colrun = np.array([max([b - a + 1 for a, b in _runs(blk[:, c])] or [0]) for c in range(W)])
    rowrun = np.array([max([b - a + 1 for a, b in _runs(blk[r])] or [0]) for r in range(H)])
    cols = np.where(colrun > 0.6 * colrun.max())[0]
    rows = np.where(rowrun > 0.6 * rowrun.max())[0]
    left = [c for c in cols if c < W / 2]
    right = [c for c in cols if c > W / 2]
    top = [r for r in rows if r < H / 2]
    bottom = [r for r in rows if r > H / 2]
    # the frame lines are the outermost contiguous groups (the long significance brackets inside the
    # plot are horizontal lines too, and are not the frame)
    top = [r for r in top if r <= min(top) + 15]
    bottom = [r for r in bottom if r >= max(bottom) - 15]
    return (min(left), max(left)), (min(right), max(right)), (min(top), max(top)), (min(bottom), max(bottom))


def read(image, at):
    f = image.astype(float)
    g = f.mean(axis=2)
    sat = f.max(axis=2) - f.min(axis=2)
    blk = (g < 110) & (sat < 40)
    col_ = (sat > 80)                                # the coloured circles
    (l0, l1), (r0, r1), (t0, t1), (b0, b1) = _frame(blk)
    # y ticks: short black runs starting at the left frame line's inner edge
    ticks = []
    cur = []
    for r in range(t1 + 3, b0 - 3):
        n = 0
        while n < 120 and blk[r, l1 + 1 + n]:
            n += 1
        if 15 <= n < 100:
            cur.append(r)
        elif cur:
            ticks.append((cur[0] + cur[-1]) / 2.0)
            cur = []
    marks = list(zip(ticks, Y_LABELS)) + [((b0 + b1) / 2.0, BOTTOM)]
    if len(ticks) != len(Y_LABELS):
        raise ValueError(f"found {len(ticks)} y ticks for {len(Y_LABELS)} labels")
    P = np.array([m[0] for m in marks])
    V = np.array([m[1] for m in marks])
    b, a = np.polyfit(P, V, 1)
    mis = float(np.max(np.abs(P - (V - a) / b)))
    val = lambda r: a + b * r
    # bars: black columns standing on the bottom frame, taller than a tick
    base = b0 - 2
    tall = np.array([blk[base - 150:base, c].all() for c in range(blk.shape[1])])
    tall[:l1 + 3] = False
    tall[r0 - 2:] = False
    bars = [(s, e) for s, e in _runs(tall) if e - s > 60]
    if len(bars) != len(X_LABELS):
        raise ValueError(f"found {len(bars)} bars for {len(X_LABELS)} labels")
    out = []
    wanted = [float(x) for x in at] if at else X_LABELS
    for (s, e), xv in zip(bars, X_LABELS):
        if xv not in wanted:
            continue
        c = (s + e) / 2.0
        w = (e - s) / 2.0
        tops = []
        for cc in list(range(int(c - 0.8 * w), int(c - 0.25 * w))) + list(range(int(c + 0.25 * w), int(c + 0.8 * w))):
            r = base
            last_black = None
            miss = 0
            # a circle's antialiased edge over the black bar is neither black nor saturated: gaps of
            # up to 4 rows are bridged
            while r > t1 and miss <= 4:
                if blk[r, cc] or col_[r, cc]:
                    miss = 0
                    if blk[r, cc]:
                        last_black = r
                else:
                    miss += 1
                r -= 1
            if last_black is not None:
                tops.append(last_black)
        top = float(np.median(tops))
        e_px = 2.0 + max(mis, 0.5)
        y = val(top)
        rec = {"x": xv, "y": float(y), "lo": float(min(val(top + e_px), val(top - e_px))),
               "hi": float(max(val(top + e_px), val(top - e_px))), "px": [float(c), top],
               "note": f"bar top over {len(tops)} columns; y {len(marks)} marks misfit {mis:.2f} px"}
        # the error bar: black along the bar's middle above its top, circles bridged
        band = blk[:, int(c) - 3:int(c) + 4].any(axis=1)
        over = col_[:, int(c) - 3:int(c) + 4].any(axis=1)
        r = int(top) - 1
        last = None
        miss = 0
        while r > t1 and miss <= 4:   # antialiased rows (circle edges) bridged, as for the bar top
            if band[r]:
                last = r
                miss = 0
            elif over[r]:
                miss = 0
            else:
                miss += 1
            r -= 1
        if last is not None and top - last > 6:
            widths = blk[:, int(c) - 40:int(c) + 41].sum(axis=1)
            lw = float(np.median([widths[k] for k in range(last + 15, int(top) - 5)] or [6.0]))
            cap = [k for k in range(last, last + 20) if widths[k] > 3 * max(lw, 3.0)]
            end = float(np.mean(cap)) if cap else last + lw / 2.0
            half = top - end
            eb = 3.0 + max(mis, 0.5)
            rec.update({"bar_hi": float(val(end)), "bar_lo": float(val(top + half)),
                        "bar_hi_outer": float(val(end - eb)), "bar_lo_outer": float(val(top + half + eb)),
                        "px_lo": end, "px_hi": top + half})
            rec["note"] += ("; error bar up to the cap at row %.0f; its lower half is hidden inside the bar: "
                            "taken as the mirror of the upper half" % end)
        else:
            rec["note"] += "; no error bar seen above the bar's top"
        out.append(rec)
    return out
