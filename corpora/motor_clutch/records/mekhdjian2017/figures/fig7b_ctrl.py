# settings for reading fig7b_ctrl
Y_LABELS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
X_LABELS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
X_LOG = False
MODE = 'lines'
COLOR = (0, 150, 70)
TOL = 110
HALF = 8
RANK = 0
GAP = 8
MINH = 3
GROUP = 4
INK = 215
DARK = 70
SCALE = 8.0
# Reading of one panel of the paper's figures, written from the record's templates: the y axis and bar
# reader below is shared by every bar chart and box plot of this record (a box plot adds its own read()
# at the end); the settings above say which panel and which bars or boxes.
# Everything comes from the image except the y tick labels matched to the tick marks.
import numpy as np

S = SCALE  # pixels per 1/300 inch at this reading's dpi


def _runs(idx, gap=1):
    idx = np.asarray(idx)
    if len(idx) == 0:
        return []
    cuts = np.flatnonzero(np.diff(idx) > gap)
    return list(zip(np.r_[idx[0], idx[cuts + 1]], np.r_[idx[cuts], idx[-1]]))


def _longest(v, gap=0):
    v = np.asarray(v, bool).copy()
    if gap:
        idx = np.flatnonzero(v)
        for a, b in zip(idx[:-1], idx[1:]):
            if 1 < b - a <= gap + 1:
                v[a:b] = True
    d = np.diff(np.r_[0, v.astype(np.int8), 0])
    s, e = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    if len(s) == 0:
        return 0, 0, 0
    k = int(np.argmax(e - s))
    return int(e[k] - s[k]), int(s[k]), int(e[k])


def _dark(img):
    return img[..., :3].astype(int).max(axis=2) < DARK


def _ink(img):
    return (img[..., :3].astype(int).min(axis=2) < INK) | _dark(img)


def _axes(img):
    dk = _dark(img)
    h, w = dk.shape
    # the y axis: the column with the longest dark vertical run in the left part of the crop
    band = int(1.5 * S)   # a slightly tilted scan: an axis column with its neighbours
    runs = [_longest(dk[:, c:c + band].any(axis=1), int(2 * S)) for c in range(int(0.6 * w))]
    L = max(r[0] for r in runs)
    cols = [c for c, r in enumerate(runs) if r[0] > 0.8 * L]
    cols = [c for c in cols if c - cols[0] <= 12 * S]
    r_top, r_bot = min(runs[c][1] for c in cols), max(runs[c][2] for c in cols)
    c0, c1 = min(cols) + band - 1, max(cols)
    # the x axis: the row with the longest dark horizontal run near the bottom of the y axis
    rr = range(max(r_bot - int(40 * S), 0), min(r_bot + int(15 * S), h))

    def from_axis(r):
        # length of the dark run (gaps up to 2S bridged) that starts at the y axis and runs right
        v = dk[r, c0:]
        first = np.flatnonzero(v[:int(20 * S)])    # a marker sitting on the origin may hide the start
        if len(first) == 0:
            return 0
        v = v[first[0]:]
        n, miss = 0, 0
        for k, d in enumerate(v):
            if d:
                n, miss = k + 1, 0
            else:
                miss += 1
                if miss > 2 * S:
                    break
        return n
    hl = {r: from_axis(r) for r in rr}
    M = max(hl.values())
    rm = max(hl, key=hl.get)
    r0 = r1 = rm
    while r0 - 1 in hl and hl[r0 - 1] > 0.8 * M:
        r0 -= 1
    while r1 + 1 in hl and hl[r1 + 1] > 0.8 * M:
        r1 += 1
    # the axis line's own left and right edges in each row (a scanned axis can lean by a few pixels)
    lo_c, hi_c = max(c0 - int(4 * S), 0), min(c1 + int(4 * S), w - 1)
    left, right = {}, {}
    for r in range(h):
        d = np.flatnonzero(dk[r, lo_c:hi_c + 1])
        if len(d):
            k = d[np.argmin(np.abs(d + lo_c - (c0 + c1) / 2))] + lo_c
            a = k
            while a - 1 >= 0 and dk[r, a - 1] and k - a < 8 * S:
                a -= 1
            b = k
            while b + 1 < w and dk[r, b + 1] and b - k < 8 * S:
                b += 1
            left[r], right[r] = a, b
    win = int(15 * S)

    def usual(edges, r):
        v = [edges[q] for q in range(r - win, r + win + 1) if q in edges]
        return float(np.median(v))
    # tick marks: rows where the axis line juts out to the left (outside) by at least 2S
    ticks = [r for r in range(max(r_top - int(3 * S), 0), min(r1 + 2, h)) if r in left and left[r] <= usual(left, r) - 1.2 * S]
    ty = [(a + b) / 2 for a, b in _runs(ticks) if b - a <= 7 * S]
    how = "tick marks"
    # tick marks inside the plot, right of the y axis: used when there are more of them than outside
    ticks = [r for r in range(max(r_top - int(3 * S), 0), r0 - int(1 * S)) if r in right and right[r] >= usual(right, r) + 1.2 * S]
    t_in = [(a + b) / 2 for a, b in _runs(ticks) if b - a <= 7 * S]
    if len(t_in) > len(ty):
        ty, how = t_in, "inside tick marks"
    if len(ty) >= 4:
        sp = float(np.median(np.diff(ty)))
        if ty[1] - ty[0] < 0.6 * sp:
            ty = ty[1:]     # the end of the axis line (a hook at its top), not a tick
    if len(ty) < 2:
        how = "label centres"
        # an axis without tick marks: each label is centred on its value; use the labels' vertical centres
        band = dk[:, max(c0 - int(18 * S), 0):c0 - int(1.5 * S)].any(axis=1)
        ty = [(a + b) / 2 for a, b in _runs(np.flatnonzero(band), gap=2) if b - a > 3 * S]
    if len(ty) == len(Y_LABELS) + 1 and r0 - 3 * S <= ty[-1] <= r1 + 3 * S:
        ty = ty[:-1]     # the x axis line itself, below the lowest printed label
    if len(ty) < len(Y_LABELS) and len(ty) >= 3:
        sp = float(np.median(np.diff(ty)))
        full = [ty[0]]
        for t in ty[1:]:
            k = int(round((t - full[-1]) / sp))
            if 2 <= k <= 3 and abs(t - full[-1] - k * sp) < 0.15 * sp:
                # ticks of an evenly spaced row not found (hidden by a label or a line): fill them in
                full += [full[-1] + (t - full[-1]) * j / k for j in range(1, k)]
            full.append(t)
        ty = full
        ax = (r0 + r1) / 2
        if len(ty) == len(Y_LABELS) - 1 and abs(ax - ty[-1] - sp) < 0.1 * sp:
            # the lowest tick merged with the x axis line: take the axis row when it lies one spacing below
            ty.append(ax)
        if len(ty) != len(Y_LABELS):
            pass
        else:
            how += ", missing ones filled in at the even spacing"
    if len(ty) == 2 * len(Y_LABELS) - 1:
        ty = ty[::2]     # unlabelled minor ticks between the labelled ones
    if len(ty) != len(Y_LABELS):
        raise ValueError(f"found {len(ty)} y ticks at rows {ty}, expected {len(Y_LABELS)}; x axis rows {r0}-{r1}")
    yv = np.array(Y_LABELS[::-1], float)
    ay = np.polyfit(ty, yv, 1)
    my = float(np.max(np.abs(np.polyval(ay, ty) - yv)))
    return dict(c0=c0, c1=c1, r0=r0, r1=r1, ay=ay, my=my, ty=ty, how=how, r_top=r_top)


def _up(mask, c, start, gap):
    """the top row of the run of mask in column c going up from row `start`, bridging gaps up to `gap`"""
    top, miss, r = None, 0, start
    while r >= 0:
        if mask[r, c]:
            top, miss = r, 0
        else:
            miss += 1
            if miss > gap:
                break
        r -= 1
    return top


def _bars(img, A):
    ink = _ink(img)
    dk = _dark(img)
    base = A["r0"] - 1
    h, w = ink.shape
    span = slice(A["c1"] + int(2 * S), w)
    while base > 0 and dk[base, span].mean() > 0.8:     # the rest of a thick x axis line
        base -= 1
    tops = {}
    for c in range(A["c1"] + 2, w):
        t = _up(ink, c, base, int(GAP * S))
        if t is not None and base - t >= MINH * S:
            tops[c] = t
    groups = _runs(sorted(tops), gap=int(GROUP * S))   # a dotted fill leaves empty columns between its dots
    groups = [(a, b) for a, b in groups if b - a >= 6 * S]
    widths = [b - a + 1 for a, b in groups]
    single = sum(widths) / N_BARS
    bars = []
    for (a, b), wd in zip(groups, widths):
        k = max(1, int(round(wd / single)))
        for i in range(k):
            bars.append((int(a + i * wd / k), int(a + (i + 1) * wd / k) - 1))
    if len(bars) != N_BARS:
        raise ValueError(f"found {len(bars)} bars {bars}, expected {N_BARS}")
    return bars, tops


def read(image, at):
    A = _axes(image)
    dk = _dark(image)
    bars, tops = _bars(image, A)
    dy = abs(A["ay"][0])
    out = []
    for xs, i in zip(at, PICK):
        a, b = bars[i]
        wd = b - a
        cols = [c for c in list(range(a + wd // 8, a + wd // 3)) + list(range(b - wd // 3, b - wd // 8)) if c in tops]
        tl = [tops[c] for c in cols]
        top = float(np.median(tl))
        thick = []
        for c in cols:
            t = tops[c]
            k = 0
            while k < 1.5 * S and not dk[t + k, c]:
                k += 1
            n = 0
            while k < 1.5 * S and n < 4 * S and dk[t + k + n, c]:
                n += 1
            thick.append(n + k if n else 0)
        t = float(np.median(thick))
        edge = top + (t - 1) / 2 if t > 0 else top
        spread = (np.percentile(tl, 90) - np.percentile(tl, 10)) / 2 + max(t, 1) / 2 + 1
        y = float(np.polyval(A["ay"], edge))
        mid = (a + b) // 2
        rec = {"x": float(xs), "y": y, "lo": y - (spread * dy + A["my"]), "hi": y + (spread * dy + A["my"]),
               "px": [mid, edge]}
        note = f"y axis fitted to {len(A['ty'])} {A['how']} (misfit {A['my']:.3g}); bar {i + 1} from the left, columns {a}-{b}; top edge {'line' if t else 'of the fill'} at row {edge:.0f}"
        # error bar: a dark vertical line rising from the bar's top near its centre
        t0 = int(top) - 1
        ref = min(_up(dk, c, t0 + 1, 2) or t0 for c in (a + wd // 6, b - wd // 6))   # the top edge beside the stem
        ext = {c: _up(dk, c, t0 + 1, 2) for c in range(mid - wd // 4, mid + wd // 4)}
        hits = [c for c, e in ext.items() if e is not None and e < ref - 1.2 * S]
        if hits:
            ec = int(np.median(hits))
            cap = _up(dk, ec, t0 + 1, 2)
            # the cap: its thickness in a column beside the stem
            cc = ec + int(3 * S)
            n = 0
            while dk[cap + n, cc] and n < 20 * S:
                n += 1
            capc = cap + max(n - 1, 0) / 2
            hi = float(np.polyval(A["ay"], capc))
            lo = y - (hi - y)
            pad = 1.5 * S * dy + A["my"]
            rec.update(bar_hi=hi, bar_lo=lo, bar_hi_outer=hi + pad, bar_lo_outer=lo - pad,
                       px_lo=capc, px_hi=edge + (edge - capc))
            note += "; error bar's lower end hidden in the bar: taken as the mirror of the upper"
        else:
            note += "; no error bar visible above the bar"
        rec["note"] = note
        out.append(rec)
    return out


# ---- x axis, and plotted points or lines of one colour ----------------------------------------------

def _col(img, rgb, tol):
    d = img[..., :3].astype(int) - np.array(rgb)[None, None, :]
    return np.sqrt((d ** 2).sum(axis=2)) < tol


def _xaxis(img, A):
    """Tick marks on the x axis, matched to X_LABELS (left to right); returns the fit column -> value."""
    dk = _dark(img)
    h, w = dk.shape
    r0, r1 = A["r0"], A["r1"]
    top, bot = {}, {}
    for c in range(A["c1"] + 1, w):
        d = np.flatnonzero(dk[max(r0 - int(4 * S), 0):min(r1 + int(4 * S), h), c])
        if len(d) == 0:
            continue
        k = int(np.round(np.median(d))) + max(r0 - int(4 * S), 0)
        a = k
        while a - 1 >= 0 and dk[a - 1, c] and k - a < 8 * S:
            a -= 1
        b = k
        while b + 1 < h and dk[b + 1, c] and b - k < 8 * S:
            b += 1
        top[c], bot[c] = a, b
    ut, ub = float(np.median(list(top.values()))), float(np.median(list(bot.values())))
    out = [c for c in bot if bot[c] >= ub + 2 * S]
    inn = [c for c in top if top[c] <= ut - 2 * S]
    tx_out = [(a + b) / 2 for a, b in _runs(sorted(out)) if b - a <= 6 * S]
    tx_in = [(a + b) / 2 for a, b in _runs(sorted(inn)) if b - a <= 6 * S]
    tx, how = (tx_out, "tick marks") if len(tx_out) >= len(tx_in) else (tx_in, "inside tick marks")
    if len(tx) < 2:
        # tick marks drawn just below the axis line, not touching it
        band = dk[r1 + int(2 * S):r1 + int(14 * S), :]
        cols = [c for c in range(A["c1"] + int(3 * S), w) if band[:, c].any()]
        tx = [(a + b) / 2 for a, b in _runs(cols) if b - a <= 5 * S]
        how = "tick marks below the axis line"
    n = len(X_LABELS)
    if len(tx) >= 2:
        sp = float(np.median(np.diff(tx)))
        yc = (A["c0"] + A["c1"]) / 2
        if len(tx) not in (n, 2 * n - 1) and abs(tx[0] - sp - yc) < 0.1 * sp:
            tx = [yc] + tx      # the first tick is the y axis itself
        full = [tx[0]]
        for t in tx[1:]:
            k = int(round((t - full[-1]) / sp))
            if 2 <= k <= 8 and abs(t - full[-1] - k * sp) < 0.15 * sp:
                # ticks of an evenly spaced row hidden (by data drawn on the axis): fill them in
                full += [full[-1] + (t - full[-1]) * j / k for j in range(1, k)]
                how += ", hidden ones filled in at the even spacing"
            full.append(t)
        tx = full
    if len(tx) == 2 * n - 1:
        tx = tx[::2]     # unlabelled minor ticks between the labelled ones
    if len(tx) != n:
        raise ValueError(f"found {len(tx)} x ticks at columns {tx}, expected {n}")
    xv = np.array([np.log10(v) if X_LOG else v for v in X_LABELS], float)
    ax = np.polyfit(tx, xv, 1)
    mx = float(np.max(np.abs(np.polyval(ax, tx) - xv)))
    return ax, mx, len(tx), how


def _col_of(ax, x):
    v = np.log10(x) if X_LOG else x
    return (v - ax[1]) / ax[0]


def read(image, at):
    A = _axes(image)
    ax, mx, nx, xhow = _xaxis(image, A)
    m = _col(image, COLOR, TOL)
    dk = _dark(image)
    dy = abs(A["ay"][0])
    cal = (f"y axis fitted to {len(A['ty'])} {A['how']} (misfit {A['my']:.3g}), x axis to {nx} {xhow} "
           f"(misfit {mx:.3g}{' in log10' if X_LOG else ''})")
    out = []
    prev = None
    for xs in at:
        x = float(xs)
        c = int(round(_col_of(ax, x)))
        R = int(HALF * S)
        win = m[:A["r0"] - 1, max(c - R, 0):c + R + 1].copy()
        win[:max(A["r_top"] - int(2 * S), 0)] = False     # nothing above the top of the y axis (titles)
        if MODE == "points":
            cnt = win.sum(axis=1)
            if cnt.max() == 0:
                out.append({"x": x, "y": None, "note": f"no point of the colour near column {c}"})
                continue
            rows = np.flatnonzero(cnt >= 0.5 * cnt.max())
            groups = _runs(rows, gap=int(1 * S))
            if prev is None:
                a, b = max(groups, key=lambda g: cnt[g[0]:g[1] + 1].sum())
            else:   # the point of this series nearest the previous one (not a legend marker of the colour)
                big = max(cnt[g[0]:g[1] + 1].sum() for g in groups)
                cand = [g for g in groups if cnt[g[0]:g[1] + 1].sum() >= 0.5 * big]
                a, b = min(cand, key=lambda g: abs((g[0] + g[1]) / 2 - prev))
            prev = (a + b) / 2
            rr = np.arange(a, b + 1)
            cen = float((rr * cnt[a:b + 1]).sum() / cnt[a:b + 1].sum())
            y = float(np.polyval(A["ay"], cen))
            e = ((b - a) / 4 + 1) * dy + A["my"]
            rec = {"x": x, "y": y, "lo": y - e, "hi": y + e, "px": [c, cen],
                   "note": cal + f"; marker at column {c}, rows {a}-{b}"}
            # error bar: a dark vertical line leaving the marker upward and downward
            cols = [k for k in range(c - int(2 * S), c + int(2 * S) + 1)
                    if dk[max(a - int(4 * S), 0):a - int(1 * S), k].sum() >= 2 * S]
            if cols:
                k = int(np.median(cols))
                up = _up(dk, k, a - 1, int(2 * S))
                r, miss, down = b + 1, 0, None
                while r < A["r0"] - 1:
                    if dk[r, k]:
                        down, miss = r, 0
                    else:
                        miss += 1
                        if miss > 2 * S:
                            break
                    r += 1
                if up is not None and up < a - 2 * S:
                    hi = float(np.polyval(A["ay"], up + 1 * S))
                    if down is not None and down > b + 2 * S:
                        lo = float(np.polyval(A["ay"], down - 1 * S))
                        rec["note"] += "; both ends of the error bar read"
                    else:
                        lo = y - (hi - y)
                        rec["note"] += "; lower end of the error bar hidden: taken as the mirror of the upper"
                    pad = 1.5 * S * dy + A["my"]
                    rec.update(bar_hi=hi, bar_lo=lo, bar_hi_outer=hi + pad, bar_lo_outer=lo - pad,
                               px_lo=up + 1 * S, px_hi=float(np.interp(lo, [y, hi], [cen, up + 1 * S])))
            else:
                rec["note"] += "; no error bar visible outside the marker"
            out.append(rec)
        else:
            # lines: in each column of the window, the runs of the colour from the bottom; take the RANKth
            cents = []
            rank = RANK[f"{float(xs):g}"] if isinstance(RANK, dict) else RANK   # 0: lowest line, -1: highest
            for k in range(win.shape[1]):
                runs = _runs(np.flatnonzero(win[:, k]), gap=int(1 * S))[::-1]   # bottom first
                if len(runs) > max(rank, -rank - 1):
                    a, b = runs[rank]
                    cents.append(((a + b) / 2, a, b))
            if not cents:
                out.append({"x": x, "y": None, "note": f"no line of the colour at column {c}"})
                continue
            cen = float(np.median([t[0] for t in cents]))
            a = float(np.median([t[1] for t in cents]))
            b = float(np.median([t[2] for t in cents]))
            y = float(np.polyval(A["ay"], cen))
            e = ((b - a) / 2 + 1) * dy + A["my"]
            out.append({"x": x, "y": y, "lo": y - e, "hi": y + e, "px": [c, cen],
                        "note": cal + f"; the {'highest' if rank == -1 else 'lowest' if rank == 0 else f'line {rank + 1} from the bottom'} line of its colour, columns {c - R}-{c + R}, rows {a:.0f}-{b:.0f}"})
    return out
