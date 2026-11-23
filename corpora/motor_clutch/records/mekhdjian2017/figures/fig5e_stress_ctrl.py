# Reading of one series of a grouped bar chart with error bars (Fig. 5e). Generated from one template
# for the six series; the settings say which panel and which bar of each pair.
# Everything comes from the image except the y tick labels matched to the tick marks.
import numpy as np

# ---- settings for this reading -------------------------------------------------------------
Y_LABELS = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]   # y tick labels, bottom to top
N_BARS = 8              # four stiffnesses x (Ctrl, +TGFb)
SERIES = 0       # 0: the left bar of each pair (Ctrl, solid), 1: the right bar (+TGFb, hatched)
# ---------------------------------------------------------------------------------------------


def _green(img):
    r, g, b = (img[..., i].astype(int) for i in range(3))
    return (g - r > 40) & (g - b > 25)


def _black(img):
    s = img[..., :3].astype(int)
    return (s.max(axis=2) < 110) & ~_green(img)


def _dark(img):
    return img[..., :3].astype(int).sum(axis=2) < 300


def _runs(idx):
    if len(idx) == 0:
        return []
    cuts = np.flatnonzero(np.diff(idx) > 1)
    return list(zip(np.r_[idx[0], idx[cuts + 1]], np.r_[idx[cuts], idx[-1]]))


def _axes(img):
    dark = _dark(img)
    h, w = dark.shape
    col = int(np.argmax(dark[:, : int(0.35 * w)].sum(axis=0)))
    row = int(h * 0.5) + int(np.argmax(dark[int(h * 0.5):, :].sum(axis=1)))
    colw = [c for c in range(max(col - 15, 0), min(col + 15, w)) if dark[:, c].sum() > 0.6 * dark[:, col].sum()]
    roww = [q for q in range(max(row - 15, 0), min(row + 15, h)) if dark[q, :].sum() > 0.6 * dark[row, :].sum()]
    c0, c1, r0, r1 = min(colw), max(colw), min(roww), max(roww)
    strip = dark[:r1 + 1, max(c0 - 16, 0):c0 - 3].mean(axis=1)
    ty = [(a + b) / 2 for a, b in _runs(np.flatnonzero(strip > 0.6))]
    if len(ty) != len(Y_LABELS):
        raise ValueError(f"found {len(ty)} y ticks, expected {len(Y_LABELS)}")
    yv = np.array(Y_LABELS[::-1], float)
    ay = np.polyfit(ty, yv, 1)
    my = float(np.max(np.abs(np.polyval(ay, ty) - yv)))
    return dict(c0=c0, c1=c1, r0=r0, r1=r1, ay=ay, my=my)


def _up_run(mask, c, start, gap=3):
    """the top row of the run of mask in column c going up from row `start`, allowing small gaps"""
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


def read(image, at):
    A = _axes(image)
    g = _green(image)
    blk = _black(image)
    base = A["r0"] - 4
    # the bars' black side edges: columns black all the way over the 30 rows above the axis
    sides = np.flatnonzero(blk[base - 30:base, :].all(axis=0))
    sides = [(a + b) / 2 for a, b in _runs(sides[sides > A["c1"] + 3])]
    bars = [(int(sides[i]) + 1, int(sides[i + 1]) - 1) for i in range(0, len(sides) - 1, 2)]
    if len(sides) % 2 or not all(g[base - 20, (a + b) // 2 - 15:(a + b) // 2 + 15].any() for a, b in bars):
        raise ValueError(f"found {len(sides)} bar edges that do not pair into green bars")
    if len(bars) != N_BARS:
        raise ValueError(f"found {len(bars)} bars, expected {N_BARS}")
    dy = abs(A["ay"][0])
    out = []
    mine = bars[SERIES::2]
    for xs, (a, b) in zip(at, mine):
        x = float(xs)
        wd = b - a
        # top of the bar: its black top edge, in off-centre columns (the error bar is in the centre)
        tops, thick = [], []
        for c in (a + wd // 6, a + wd // 4, b - wd // 4, b - wd // 6):
            rows = np.flatnonzero(blk[:base, c])
            if len(rows):
                ra, rb = _runs(rows)[-1]       # the black edge nearest above the bar's fill
                tops.append((ra + rb) / 2)
                thick.append(rb - ra + 1)
        top = float(np.median(tops))
        t = float(np.median(thick))
        spread = (max(tops) - min(tops)) / 2 + t / 4 + 1
        y = float(np.polyval(A["ay"], top))
        # error bar: the black line in the middle of the bar, going up from the top edge to its cap
        mid = (a + b) // 2
        note = f"bar columns {a}-{b}"
        rec = {"x": x, "y": y, "lo": y - (spread * dy + A["my"]), "hi": y + (spread * dy + A["my"]),
               "px": [mid, top]}
        cand = [c for c in range(mid - wd // 6, mid + wd // 6)
                if blk[int(top - t / 2 - 4):int(top - t / 2), c].all()]
        if cand:
            ec = int(np.median(cand))
            cap = _up_run(blk, ec, int(top), gap=2)
            if cap is not None and cap < top - t:
                cap = cap + t / 2          # the centre of the cap line
                hi = float(np.polyval(A["ay"], cap))
                lo = y - (hi - y)
                pad = 3 * dy + A["my"]
                rec.update(bar_hi=hi, bar_lo=lo, bar_hi_outer=hi + pad, bar_lo_outer=lo - pad,
                           px_lo=cap, px_hi=top + (top - cap))
                note += "; lower end of the error bar hidden in the bar: taken as the mirror of the upper"
        else:
            note += "; no error bar found above the bar"
        rec["note"] = note
        out.append(rec)
    return out
