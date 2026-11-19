"""Shared reading code for the bar charts of shyer2015 (spreadsheet style: filled bars without outline, in
black or greys, a grey y axis with tick marks pointing left, black SD error bars with short caps). Every
figure is an embedded raster of about 300 dpi, rendered at the crop and dpi given in figures.yaml, so edges
are blocky (about 4 px at 1200 dpi).

Grey level: g = the brightest channel of a pixel (0 black, 255 paper).

Calibration (y): the y axis is the leftmost column group whose longest vertical run of g < 200 (or the
caller's axis_ink, for pale grey axes) exceeds
AXIS_FRAC of the image height. Ticks are the row groups where the 4 px just left of the axis are ink and the ink run leftwards from the axis is 4-40 px long (a tick label further left is separated
by paper); row groups less than 30 px apart are one tick. Their centres, top to bottom, are matched to the tick values the caller gives (labels as
printed; where a panel's ticks carry no labels the caller says which values they stand for), a straight
line value = a + b*row is fitted, and its rms misfit (px, at least 0.5) widens every interval. The x axis
is the long horizontal ink line nearest the row of value 0.

Bars: on the row BASE_UP px above the x axis, columns right of the axis with g < 235 are split into runs of
like grey (a jump of more than 25 grey levels starts a new run; runs narrower than MIN_W px are antialiased
borders and are dropped; a black run (g < 30) narrower than 40 px inside a grey bar is an error bar and is
skipped, joining the grey on both sides). The runs, left to right, are the bars: bar 1, 2, ...

Bar value: the fill grey is the median of the bar's base row. In the columns at 15-35% and 65-85% of the
bar's width (away from the error bar), going up from the base, the top edge is the first row whose grey
differs from the fill by more than half the fill's contrast with the paper; the value is read at that
edge (minus 0.5 px), the median over those columns. The interval is +-(EDGE_TOL px: the raster's block
size) plus the misfit.

Error bars: the stem is the dark column group (g < STEM) in the middle half of the bar just above its top.
Walking up it, the upper end is the topmost group of cap rows (rows where the dark run through the stem is
at least 6 px wider than the stem); its centre is the end, its half thickness plus EDGE_TOL the precision.
Below the top the stem is followed only where the fill is lighter than the stem (fill grey >= 40, with the
threshold min(STEM, fill - 15)): the lowest group of cap rows is the lower end. A lower end not found (hidden in a black bar) is taken as the
mirror of the upper about the bar top, and the note says so. Where both ends are found, the mean's
interval is widened to include the bar's midpoint (an SD bar is symmetric about the mean). A bar too small
to show a stem has its error bar inside the black dash at its top: the dash's extent is reported as the
bar (at most the marker) and the note says so.
"""

import numpy as np

AXIS_FRAC = 0.45
BASE_UP = 6
MIN_W = 20
EDGE_TOL = 4.0
STEM = 60


def gray(image):
    return np.asarray(image)[..., :3].astype(int).max(axis=2)


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


class Axis:
    def __init__(self, rows, labels):
        self.rows = np.asarray(rows, float)
        self.labels = np.asarray(labels, float)
        b, a = np.polyfit(self.rows, self.labels, 1)
        self.a, self.b = float(a), float(b)
        res = self.labels - (self.a + self.b * self.rows)
        self.misfit = max(float(np.sqrt(np.mean((res / self.b) ** 2))), 0.5)

    def val(self, row):
        return float(self.a + self.b * row)

    def row(self, val):
        return (val - self.a) / self.b

    def span(self, row, tol):
        t = tol + self.misfit
        v1, v2 = self.val(row - t), self.val(row + t)
        return min(v1, v2), max(v1, v2)


def calibrate(g, labels, axis_ink=200):
    ink = g < axis_ink
    H, W = ink.shape
    vr = np.array([_longest(ink[:, c]) for c in range(W)])
    yc = _groups(np.where(vr > AXIS_FRAC * H)[0])[0]
    c0 = yc[0]
    tick_rows = []
    for r in range(H):
        if not ink[r, c0 - 4:c0].all():
            continue
        n = 0
        c = c0 - 1
        while c >= 0 and ink[r, c]:
            n += 1
            c -= 1
        if 4 <= n <= 40:
            tick_rows.append(r)
    # a pale antialiased tick can break into two row groups a few px apart: groups within 30 px are one tick
    ticks = [(gr[0] + gr[-1]) / 2.0 for gr in _groups(tick_rows, gap=30)]
    if len(ticks) != len(labels):
        raise RuntimeError(f"expected {len(labels)} y ticks, found {len(ticks)}: {ticks}")
    ax = Axis(ticks, labels)
    zero = ax.row(0.0)
    hr = np.array([_longest(ink[r, c0:]) for r in range(H)])
    xg = [gr for gr in _groups(np.where(hr > 0.4 * (W - c0))[0]) if abs((gr[0] + gr[-1]) / 2 - zero) < 20]
    x_top = xg[0][0] if xg else int(round(zero))
    return ax, yc, x_top, ticks


def find_bars(g, yc, x_top, base_up=BASE_UP):
    r = x_top - base_up
    row = g[r]
    cols = range(yc[-1] + 8, g.shape[1])
    runs = []
    for c in cols:
        v = int(row[c])
        if v >= 235:
            if runs and runs[-1]["open"]:
                runs[-1]["open"] = False
            continue
        if runs and runs[-1]["open"] and c == runs[-1]["end"] + 1 and abs(v - runs[-1]["ref"]) <= 25:
            runs[-1]["end"] = c
            runs[-1]["vals"].append(v)
        else:
            if runs:
                runs[-1]["open"] = False
            runs.append({"start": c, "end": c, "vals": [v], "ref": v, "open": True})
        runs[-1]["ref"] = int(np.median(runs[-1]["vals"][-12:]))
    runs = [x for x in runs if x["end"] - x["start"] + 1 >= MIN_W or np.median(x["vals"]) < 30]
    # a narrow black run between two runs of the same grey is an error bar: join the three
    out = []
    i = 0
    while i < len(runs):
        cur = dict(runs[i])
        while (i + 2 < len(runs) and np.median(runs[i + 1]["vals"]) < 30
               and runs[i + 1]["end"] - runs[i + 1]["start"] < 40
               and runs[i + 1]["start"] - cur["end"] <= 6 and runs[i + 2]["start"] - runs[i + 1]["end"] <= 6
               and abs(np.median(runs[i + 2]["vals"]) - np.median(cur["vals"])) <= 25
               and np.median(cur["vals"]) >= 30):
            cur["end"] = runs[i + 2]["end"]
            cur["vals"] = cur["vals"] + runs[i + 2]["vals"]
            i += 2
        out.append(cur)
        i += 1
    bars = [(x["start"], x["end"], float(np.median(x["vals"]))) for x in out if x["end"] - x["start"] + 1 >= MIN_W]
    return bars


def _dark_width(g, r, sc, thr):
    left = 0
    while sc - left - 1 >= 0 and g[r, sc - left - 1] < thr:
        left += 1
    right = 0
    while sc + right + 1 < g.shape[1] and g[r, sc + right + 1] < thr:
        right += 1
    return left + right + 1 if g[r, sc] < thr else 0


def read_bar(ax, g, bar, x_top, k, x, base_up=BASE_UP):
    l, r, fill = bar
    w = r - l + 1
    base = x_top - base_up
    half = abs(255 - fill) / 2.0
    cols = [c for c in range(l, r + 1) if 0.15 <= (c - l) / w <= 0.35 or 0.65 <= (c - l) / w <= 0.85]
    tops = []
    for c in cols:
        rr = base
        while rr > 0 and abs(int(g[rr, c]) - fill) <= half:
            rr -= 1
        tops.append(rr + 0.5)
    top = float(np.median(tops))
    y = ax.val(top)
    lo, hi = ax.span(top, EDGE_TOL)
    note = f"bar {k} (columns {l}-{r}, fill grey {fill:.0f}): top edge at row {top:.1f}; misfit {ax.misfit:.2f} px"
    out = {"x": x, "y": y, "lo": lo, "hi": hi, "px": [float((l + r) / 2.0), top]}
    itop = int(round(top))
    mid0, mid1 = l + w // 4, r - w // 4
    # the stem: dark columns in the middle half just above the top
    dark_cols = [c for c in range(mid0, mid1 + 1) if (g[max(itop - 10, 0):itop - 3, c] < STEM).all()]
    if not dark_cols:
        blob = [rr for rr in range(max(itop - 16, 0), min(itop + 16, base)) if (g[rr, mid0:mid1 + 1] < 30).sum() >= 6]
        if blob:
            b0, b1 = blob[0], blob[-1]
            out.update({"bar_lo": ax.val(b1), "bar_hi": ax.val(b0),
                        "bar_lo_outer": min(ax.span(b1, EDGE_TOL)), "bar_hi_outer": max(ax.span(b0, EDGE_TOL)),
                        "px_lo": float(b0), "px_hi": float(b1)})
            out["note"] = note + (f"; no stem: the error bar is inside the black dash at the bar top (rows {b0}-{b1}), "
                                  "reported as at most the dash")
        else:
            out["note"] = note + "; no error bar found"
        return out
    grp = max(_groups(dark_cols), key=len)
    sc = int(round(np.mean(grp)))
    stem_w = len(grp)
    rr = itop - 3
    while rr > 0 and (g[rr, sc - 3:sc + 4] < STEM).any():
        rr -= 1
    up_end = rr + 1
    caps = [q for q in range(up_end, itop - 2) if _dark_width(g, q, sc, STEM) >= stem_w + 6]
    cg = _groups(caps)
    if cg:
        c_hi = (cg[0][0] + cg[0][-1]) / 2.0
        th_hi = (cg[0][-1] - cg[0][0] + 1) / 2.0
        note += f"; upper cap rows {cg[0][0]}-{cg[0][-1]}"
    else:
        c_hi, th_hi = float(up_end), 1.0
        note += f"; no cap found, upper end at the stem's end, row {up_end}"
    hi_end = ax.val(c_hi)
    hi_out = max(ax.span(c_hi, th_hi + EDGE_TOL))
    found_lo = False
    if fill >= 40:
        thr = min(STEM, fill - 15)
        rr = itop + 3
        while rr < base and (g[rr, sc - 3:sc + 4] < thr).any():
            rr += 1
        lo_end_row = rr - 1
        lcaps = [q for q in range(itop + 3, lo_end_row + 1) if _dark_width(g, q, sc, thr) >= stem_w + 6]
        lg = _groups(lcaps)
        if lg and lo_end_row > itop + 3:
            c_lo = (lg[-1][0] + lg[-1][-1]) / 2.0
            th_lo = (lg[-1][-1] - lg[-1][0] + 1) / 2.0
            found_lo = True
            note += f"; lower cap rows {lg[-1][0]}-{lg[-1][-1]}"
    if found_lo:
        lo_end = ax.val(c_lo)
        lo_out = min(ax.span(c_lo, th_lo + EDGE_TOL))
        mid = (c_hi + c_lo) / 2.0
        note += f"; error bar midpoint row {mid:.1f}, {mid - top:+.1f} px from the top edge"
        out["lo"] = min(lo, min(ax.span(mid, 2.0)))
        out["hi"] = max(hi, max(ax.span(mid, 2.0)))
    else:
        c_lo = 2 * top - c_hi
        lo_end = 2 * y - hi_end
        lo_out = 2 * y - hi_out
        note += "; lower end hidden in the bar, taken as the mirror of the upper about the top"
    out.update({"bar_lo": lo_end, "bar_hi": hi_end, "bar_lo_outer": min(lo_out, lo_end),
                "bar_hi_outer": max(hi_out, hi_end), "px_lo": c_hi, "px_hi": c_lo, "note": note})
    return out


def read(image, at, labels, order, expect=None, axis_ink=200, base_up=BASE_UP):
    """labels: tick values top to bottom; order: {x value: bar number from the left}; expect: number of bars;
    axis_ink: the grey level below which a pixel counts as axis or tick ink (raised for pale axes);
    base_up: how far above the x axis the bars are found (raised where a pale axis blurs further up)."""
    g = gray(image)
    ax, yc, x_top, ticks = calibrate(g, labels, axis_ink)
    bars = find_bars(g, yc, x_top, base_up)
    if expect is not None and len(bars) != expect:
        raise RuntimeError(f"expected {expect} bars, found {len(bars)}: {bars}")
    out = []
    for xv in at:
        x = float(xv)
        k = order[x]
        out.append(read_bar(ax, g, bars[k - 1], x_top, k, x, base_up))
    return out
