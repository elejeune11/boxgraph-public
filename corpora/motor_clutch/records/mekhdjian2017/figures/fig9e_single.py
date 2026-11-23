# settings for reading fig9e_single
Y_LABELS = [0, 0.4, 0.8, 1.2, 1.6]
N_BARS = 3
PICK = [0, 1, 2]
GAP = 14
MINH = 3
GROUP = 4
INK = 215
DARK = 110
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
