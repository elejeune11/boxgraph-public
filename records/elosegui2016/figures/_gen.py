"""Generic reading code for the plotted measurements of Elosegui-Artola et al. 2016 (second pass): points with
s.e.m. bars, bar charts and the Fig. 3a curve. Everything is found in the image; the only numbers typed in
are the printed tick labels each reader passes, the panel's legend region (in data units, so that legend
markers are not taken for data) and, for grouped bar charts, the printed group labels.

Method
- axes (`calibrate`): the y axis is the column with the longest run of dark pixels, the x axis the row (in
  the lower part) with the longest run. Tick marks are short dark marks just outside (or, failing that,
  just inside) each axis; they are matched in order to the printed labels and fitted by a straight line
  (x in log10 where the axis is logarithmic). The rms misfit (px) is reported and enters every interval.
- markers (`read_series`): pixels of the series' colour inside the plot box; open markers have their holes
  filled; a small opening removes anti-aliased edges and the thinnest lines. The marker size is the median
  box of the blobs whose fill fraction matches the marker's shape (disc, square, diamond, triangle up or
  down). Markers are found by matching a filled template of that shape (92% of the size): the score is the
  fraction of the template's pixels that are of the colour; peaks at least 0.6 marker apart scoring >= 0.93
  are whole markers, 0.6-0.93 markers partly covered by another series. A whole marker's value is the
  template's centroid (for a triangle the centroid, not the box centre, is where the bar is centred, as the
  bars show). A partly covered marker's value is the midpoint of its two bar caps (s.e.m. bars are
  symmetric), or it is not read.
- error bars: from the marker's edge the stem (series colour within +-`stem` px of the centre column) is
  followed up and down, bridging gaps up to one marker size (a bar drawn behind another marker); a cap is
  a band of rows where the colour spans between `cap_min` and `cap_max` px across the stem. The bar end is
  the middle of the outermost cap. A missing cap (hidden behind another marker) is taken as the mirror of
  the other end; a bar with no cap outside the marker is reported as at most the marker.
- intervals: centre +-(1 px + 2 x misfit) (+ the half-difference to the bar midpoint when the two
  disagree by more than 3 px); bar ends widened by 2 px + 2 x misfit.
"""
import numpy as np
from scipy import ndimage


# ---------------------------------------------------------------- masks
def hsv(img):
    rgb = img[..., :3].astype(float) / 255.0
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    d = mx - mn + 1e-9
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0)
    return h, s, mx


def mask_of(img, colour):
    """colour: 'red', 'blue', 'green', 'lightblue', 'pink', 'black', 'dark', 'grey' or a hue in degrees."""
    rgb = img[..., :3].astype(float)
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    if colour == "black":
        return (mx < 80) & (mx - mn < 40)
    if colour == "dark":       # axes and ticks (dark grey axes included)
        return (mx < 130) & (mx - mn < 45)
    if colour == "grey":
        return (mx > 150) & (mx < 225) & (mx - mn < 25)
    h, s, v = hsv(img)
    hues = {"red": (0, 22, 0.45), "blue": (226, 22, 0.35), "green": (120, 35, 0.35),
            "lightblue": (205, 15, 0.30), "pink": (2, 20, 0.22)}
    hue, width, smin = hues[colour] if isinstance(colour, str) else (colour, 22, 0.35)
    dh = np.abs((h - hue + 180) % 360 - 180)
    m = (dh < width) & (s > smin) & (v > 0.25)
    if colour == "pink":       # the light red of Supplementary Fig. 1b, not the saturated red
        m &= s < 0.6
    if colour == "red":
        m &= s >= 0.6
    return m


def runs(v):
    m = np.concatenate([[False], v, [False]]).astype(int)
    d = np.diff(m)
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1))


def groups(idx, gap=2):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return out


# ---------------------------------------------------------------- axes
class Cal:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def col(self, x):
        return self.ax * (np.log10(x) if self.xlog else x) + self.bx

    def x(self, col):
        v = (col - self.bx) / self.ax
        return 10 ** v if self.xlog else v

    def row(self, y):
        return self.ay * y + self.by

    def y(self, row):
        return (row - self.by) / self.ay

    def note(self):
        return f"x ticks misfit {self.xmis:.1f} px, y ticks misfit {self.ymis:.1f} px"


def _ticks(band_masks, n):
    """Positions of short dark marks in the first band (outside, then inside) that has exactly n of them."""
    found = []
    for band in band_masks:
        idx = np.flatnonzero(band.mean(axis=1 if band.ndim == 2 else 0) > 0.5)
        t = [float(np.mean(g)) for g in groups(list(idx)) if len(g) < 30]
        found.append(t)
        if len(t) == n:
            return t
    raise RuntimeError(f"expected {n} ticks, found {found}")


def calibrate(img, xlabels, ylabels, xlog=True, tick=36, ymin_row=0, ydrop=0, axis_also=None):
    """`ydrop`: unlabelled ticks at the bottom of the y axis (below the lowest printed label), left out.
    `axis_also`: a colour drawn over the axis lines (Fig. 3a: the blue curve runs along the x axis); it
    counts as axis when the axes are found, never as a tick."""
    dk = mask_of(img, "dark")
    ax_m = dk if axis_also is None else (dk | mask_of(img, axis_also))
    h, w = dk.shape
    # y axis: the column with the longest dark run
    best = (0, 0, 0, 0)
    for c in range(w):
        for a, b in runs(dk[:, c]):
            if b - a > best[0]:
                best = (b - a, c, a, b)
    _, xa, ya0, ya1 = best
    cols = [c for c in range(max(0, xa - 15), min(w, xa + 15)) if dk[ya0 + 5:ya1 - 5, c].mean() > 0.85]
    xl, xr = min(cols), max(cols)
    # x axis: the row (below the middle of the y axis) with the longest dark run
    best = (0, 0, 0, 0)
    for r in range((ya0 + ya1) // 2, h):
        for a, b in runs(ax_m[r]):
            if b - a > best[0]:
                best = (b - a, r, a, b)
    _, yb, xb0, xb1 = best
    rows = [r for r in range(max(0, yb - 15), min(h, yb + 15)) if dk[r, xb0 + 5:xb1 - 5].mean() > 0.85]
    if not rows:   # the axis line is mostly under another colour: its visible dark part
        rows = [r for r in range(max(0, yb - 15), min(h, yb + 15)) if dk[r, xb0:xb0 + 200].mean() > 0.85]
    yt, ybot = min(rows), max(rows)
    # y ticks: left of the axis (outside), else right (inside)
    lo_r, hi_r = max(ymin_row, ya0 - 6), ybot + 6
    bands = [dk[lo_r:hi_r, max(0, xl - tick):xl - 3], dk[lo_r:hi_r, xr + 3:xr + tick]]
    ty = [t + lo_r for t in _ticks(bands, len(ylabels) + ydrop)]
    ty = sorted(ty, reverse=True)[ydrop:]
    ay, by = np.polyfit(ylabels, ty, 1)
    ymis = float(np.sqrt(np.mean((np.polyval([ay, by], ylabels) - np.array(ty)) ** 2)))
    if xlabels is None:   # a bar chart: no x scale (columns are returned as they are)
        return Cal(ax=1.0, bx=0.0, ay=ay, by=by, xmis=0.0, ymis=ymis, xlog=False, left=xr + 1, right=int(xb1),
                   top=int(max(0, min(ya0, min(ty)) - 40)), bottom=yt - 1, xticks=[], yticks=ty)
    # x ticks: below the axis (outside), else above (inside)
    lo_c, hi_c = xl - 6, xb1 + 6
    bands = [dk[ybot + 3:ybot + tick, lo_c:hi_c], dk[yt - tick:yt - 3, lo_c:hi_c]]
    bands = [b.T for b in bands]
    tx = sorted(t + lo_c for t in _ticks(bands, len(xlabels)))
    lx = np.log10(xlabels) if xlog else np.asarray(xlabels, float)
    ax, bx = np.polyfit(lx, tx, 1)
    xmis = float(np.sqrt(np.mean((np.polyval([ax, bx], lx) - np.array(tx)) ** 2)))
    # the plot box runs a little past the last tick and the end of the axes (a marker may sit on the edge)
    return Cal(ax=ax, bx=bx, ay=ay, by=by, xmis=xmis, ymis=ymis, xlog=xlog, left=xr + 1,
               right=int(min(w - 1, max(xb1, max(tx)) + 80)), top=int(max(0, min(ya0, min(ty)) - 80)),
               bottom=yt - 1, xticks=tx, yticks=ty)


def box_mask(shape, cal, exclude=()):
    """The plot interior, without the given regions (data units: (x0, x1, y0, y1))."""
    m = np.zeros(shape, bool)
    m[cal.top:cal.bottom - 2, cal.left + 3:cal.right] = True
    for x0, x1, y0, y1 in exclude:
        c0, c1 = sorted((cal.col(x0), cal.col(x1)))
        r0, r1 = sorted((cal.row(y0), cal.row(y1)))
        m[max(0, int(r0)):int(r1) + 1, max(0, int(c0)):int(c1) + 1] = False
    return m


# ---------------------------------------------------------------- markers and error bars
def _disc(r):
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    return xx ** 2 + yy ** 2 <= r ** 2


def find_markers(mask, open_r, hollow=False, min_area=None):
    m = ndimage.binary_fill_holes(mask) if hollow else mask
    core = ndimage.binary_opening(m, structure=_disc(open_r))
    lab, n = ndimage.label(core)
    min_area = min_area or int(3.0 * open_r * open_r * np.pi)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        sub = lab[sl] == i
        if sub.sum() < min_area:
            continue
        rr, cc = np.nonzero(sub)
        out.append(dict(r0=sl[0].start, r1=sl[0].stop - 1, c0=sl[1].start, c1=sl[1].stop - 1,
                        rc=float(rr.mean() + sl[0].start), cc=float(cc.mean() + sl[1].start),
                        area=int(sub.sum())))
    return out


# ---------------------------------------------------------------- shape templates
FILL = {"disc": np.pi / 4, "square": 1.0, "diamond": 0.5, "tri_up": 0.5, "tri_down": 0.5}


def template(shape, w, h):
    """A filled marker of the shape, w x h px, and the (row, col) of its centroid in the array."""
    h, w = int(round(h)), int(round(w))
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx + 0.5) / w * 2 - 1      # -1..1, left to right
    v = (yy + 0.5) / h * 2 - 1      # -1..1, top to bottom
    if shape == "disc":
        t = u ** 2 + v ** 2 <= 1
    elif shape == "square":
        t = np.ones((h, w), bool)
    elif shape == "diamond":
        t = np.abs(u) + np.abs(v) <= 1
    elif shape == "tri_up":
        t = np.abs(u) <= (v + 1) / 2
    else:   # tri_down
        t = np.abs(u) <= (1 - v) / 2
    rr, cc = np.nonzero(t)
    return t, (float(rr.mean()), float(cc.mean()))


def marker_size(filled, shape):
    """The marker size of a series (`filled`: its mask), or of several series drawn with one marker (a list
    of masks): see the module docstring."""
    fl = filled if isinstance(filled, list) else [filled]
    sizes = []
    for f in fl:
        lab, n = ndimage.label(f)
        for i, sl in enumerate(ndimage.find_objects(lab), start=1):
            hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            frac = (lab[sl] == i).sum() / (hh * ww)
            if hh > 15 and abs(frac - FILL[shape]) < 0.1 and 0.6 < ww / hh < 1.7:
                sizes.append((ww, hh))
    if not sizes:
        raise RuntimeError("no whole marker found to measure the marker size")
    # each blob's box is a candidate size; the one that fits the most whole markers, weighted by its area,
    # wins (a fragment fits many places but is small; a marker merged with a stem fits nowhere else)
    if shape in ("disc", "square"):   # round markers: a blob taller or wider than round has a bar on it
        sizes = [(min(s), min(s)) for s in sizes]
    big = max(s[0] * s[1] for s in sizes)
    cand = sorted({(2 * round(w / 2), 2 * round(h / 2)) for w, h in sizes if w * h >= max(200, 0.25 * big)},
                  key=lambda s: -s[0] * s[1])[:10]   # the ten largest distinct sizes, to 2 px
    best = None
    for s in cand:
        n = sum(1 for f in fl for k in match_markers(f, shape, s, part=0.93) if k["whole"])
        if best is None or n * s[0] * s[1] > best[0]:
            best = (n * s[0] * s[1], s)
    return float(best[1][0]), float(best[1][1])


def match_markers(filled, shape, size, whole=0.93, part=0.3, covered=None, one_per_x=True):
    """Template matching (see the module docstring). With `covered` (other series' markers drawn on top,
    holes filled), a template position scores on the colour or those markers (`score`), and must also
    hold at least `part` of its pixels in the colour (`own`); own >= `whole` is a whole marker. The centre
    is the template's centroid placed at the middle of the plateau of near-maximal scores around the peak;
    the plateau's half-height (px) is returned as `spread`."""
    from scipy.signal import fftconvolve
    w, h = size
    t, (oy, ox) = template(shape, 0.92 * w, 0.92 * h)
    k = t[::-1, ::-1].astype(float)
    own = fftconvolve(filled.astype(float), k, mode="valid") / t.sum()
    sc = own if covered is None else fftconvolve((filled | covered).astype(float), k, mode="valid") / t.sum()
    ok = (own >= part) & (sc >= whole)
    out = []
    taken = np.zeros(sc.shape, bool)
    key = np.where(ok, sc + 0.01 * own, -1)
    order = np.argsort(key, axis=None)[::-1]
    r_ex = int(0.8 * min(w, h))
    for idx in order:
        r, c = np.unravel_index(idx, sc.shape)
        if key[r, c] < 0:
            break
        if taken[r, c]:
            continue
        s = sc[r, c]
        r0, r1 = max(0, r - r_ex), r + r_ex + 1
        c0, c1 = max(0, c - r_ex), c + r_ex + 1
        # a whole marker is centred on the plateau of its own colour's score (covering lines and markers
        # would let it slide); a partly covered one on the plateau of the score with cover
        met = own if own[r, c] >= whole else sc
        lab, _ = ndimage.label((met[r0:r1, c0:c1] >= met[r, c] - 0.01) & ok[r0:r1, c0:c1]
                               & ~taken[r0:r1, c0:c1])
        pr, pc = np.nonzero(lab == lab[r - r0, c - c0])   # the plateau around this peak only
        rr, cc = pr.mean() + r0, pc.mean() + c0
        taken[r0:r1, c0:c1] = True
        o = float(own[r, c])
        if one_per_x and o < whole and any(abs(cc + ox - k["cc"]) < 0.5 * w for k in out):
            continue   # a partial fit in the column of a marker already found: the same point, or a fragment
        out.append(dict(rc=float(rr + oy), cc=float(cc + ox), score=float(s), own=o, whole=bool(o >= whole),
                        spread=float((pr.max() - pr.min()) / 2), r0=int(rr), r1=int(rr + t.shape[0] - 1)))
    return out


def _cap_end(mask, col, start, step, stop, stem, cap_min, cap_max, max_gap, stemmask=None, inner=None):
    """Follow the stem (in `stemmask`, default `mask`) from `start` in direction `step`; return the middle
    row of the outermost cap (in `mask`). `inner(r)`: the marker's own width at row r; within the marker a
    cap counts only where it sticks out beyond it by more than 6 px."""
    stemmask = mask if stemmask is None else stemmask
    inner = inner or (lambda r: 0)
    c = int(round(col))
    h, w = mask.shape
    r, gap = start, 0
    caps, band = [], []
    while 0 <= r < h and (r - stop) * step <= 0:
        win = mask[r, max(0, c - stem):c + stem + 1]
        if stemmask[r, max(0, c - stem):c + stem + 1].any():
            gap = 0
        if win.any():
            j = max(0, c - stem) + int(np.flatnonzero(win)[0])
            a = j
            while a - 1 >= 0 and mask[r, a - 1]:
                a -= 1
            b = j
            while b + 1 < w and mask[r, b + 1]:
                b += 1
            span = b - a + 1
            if (cap_min <= span <= cap_max and a < c - stem / 2 and b > c + stem / 2 and span > inner(r) + 6
                    and abs(r - start) > stem + 4):   # at the centre: a horizontal (x) error bar, not a cap
                band.append(r)
            else:
                if band:
                    caps.append(band)
                band = []
        else:
            if band:
                caps.append(band)
            band = []
            if not stemmask[r, max(0, c - stem):c + stem + 1].any():
                gap += 1
                if gap > max_gap:
                    break
        r += step
    if band:
        caps.append(band)
    caps = [b for b in caps if len(b) <= 25]
    return float(np.mean(caps[-1])) if caps else None


def read_series(img, cal, colour, open_r, shape, stem=5, cap_min=None, cap_max=None, hollow=False, exclude=(),
                x_of=None, cover=None, note="", size=None, part=0.3, one_per_x=True, bars=True):
    """Markers of one series with their error bars. `x_of(col)`: the x value of a marker column (default:
    the calibrated axis). `cover`: masks of other colours drawn on top (a marker or a bar stem may lie
    behind them)."""
    inside = box_mask(img.shape[:2], cal, exclude)
    m = mask_of(img, colour) & inside
    filled = ndimage.binary_fill_holes(m) if hollow else m
    filled = ndimage.binary_opening(filled, structure=_disc(open_r))
    ws, hs = size or marker_size(filled, shape)
    covered = None
    if cover is not None:
        covered = ndimage.binary_dilation(ndimage.binary_fill_holes(cover & inside), iterations=2)
    marks = match_markers(filled, shape, (ws, hs), part=part, covered=covered, one_per_x=one_per_x)
    cap_min = cap_min or 3 * stem
    cap_max = cap_max or 1.4 * ws
    stemmask = m if cover is None else (m | (cover & inside))
    capmask = ndimage.binary_fill_holes(m) if hollow else m
    full, (oyf, _) = template(shape, ws, hs)
    widths = full.sum(axis=1)
    widen = 2 + 2 * cal.ymis
    out = []
    for k in sorted(marks, key=lambda k: k["cc"]):
        col, whole = k["cc"], k["whole"]
        snapped = False
        if not whole:
            # a partly covered marker fits many columns: take its own bar stem's column, the column within
            # half a marker with the longest vertical run of the colour just above or below the marker
            L = {}
            for c in range(max(0, int(col - 0.25 * ws)), min(m.shape[1], int(col + 0.25 * ws) + 1)):
                L[c] = 0
                for a, b in ((int(k["r0"] - 1.3 * hs), k["r0"]), (k["r1"], int(k["r1"] + 1.3 * hs))):
                    seg = m[max(0, a):max(0, b), c]
                    L[c] = max([L[c]] + [e - s + 1 for s, e in runs(seg)])
            c0 = max(L, key=L.get) if L else None
            if c0 is not None and L[c0] >= 15:
                col = float(np.mean([c for c in L if abs(c - c0) <= stem and L[c] >= 0.8 * L[c0]]))
                snapped = True
        hh = hs
        top_row = k["rc"] - oyf

        def inner(r, top_row=top_row):
            i = int(round(r - top_row))
            return int(widths[i]) if 0 <= i < len(widths) else 0

        start = int(round(k["rc"]))
        top = bot = None
        if bars:
            top = _cap_end(capmask, col, start, -1, cal.top, stem, cap_min, cap_max, int(1.3 * hs), stemmask,
                           inner)
            bot = _cap_end(capmask, col, start, +1, cal.bottom - 3, stem, cap_min, cap_max, int(1.3 * hs),
                           stemmask, inner)
        x = float(x_of(col)) if x_of else float(cal.x(col))
        notes = [f"{shape} marker {ws:.0f}x{hs:.0f} px, {k['own']:.0%} of it visible", cal.note()]
        if note:
            notes.append(note)
        if snapped:
            notes.append("column taken from the marker's own bar stem")
        if whole:
            r0 = k["rc"]
            half = 1 + 2 * cal.ymis
            if top is not None and bot is not None:
                mid = (top + bot) / 2
                if abs(mid - r0) > 3:
                    half += abs(mid - r0) / 2
                    notes.append(f"bar midpoint {abs(mid - r0):.0f} px from the centroid, half of it added")
        elif top is not None and bot is not None:
            r0 = (top + bot) / 2
            half = 2 + 2 * cal.ymis
            notes.append("marker partly covered by another series: value is the midpoint of its bar caps")
        else:
            if k["own"] < 0.5:
                continue   # less than half visible and no two caps: where it sits is not well determined
            r0 = k["rc"]
            half = 1 + 2 * cal.ymis + k["spread"] + (1 - k["own"]) * hs / 4
            notes.append(f"marker partly covered by another series: value is where its visible part fits the "
                         f"marker shape, +-{k['spread']:.0f} px over the positions that fit as well, plus "
                         f"(1 - visible fraction) x a quarter of the marker height")
        y = cal.y(r0)
        rec = {"x": x, "y": float(y), "lo": float(min(cal.y(r0 - half), cal.y(r0 + half))),
               "hi": float(max(cal.y(r0 - half), cal.y(r0 + half))), "px": [float(col), float(r0)]}
        if not bars:
            notes.append("a single cell's value, no error bar")
        elif top is None and bot is None:
            hb = hh / 2
            rec.update(bar_hi=float(cal.y(r0 - hb)), bar_lo=float(cal.y(r0 + hb)),
                       bar_hi_outer=float(cal.y(r0 - hb - widen)), bar_lo_outer=float(cal.y(r0 + hb + widen)))
            notes.append("error bar hidden inside the marker, reported as at most the marker")
        else:
            if top is None:
                top = 2 * r0 - bot
                notes.append("upper bar cap hidden, taken as the mirror of the lower")
            if bot is None:
                bot = 2 * r0 - top
                notes.append("lower bar cap hidden, taken as the mirror of the upper")
            rec.update(bar_hi=float(cal.y(top)), bar_lo=float(cal.y(bot)),
                       bar_hi_outer=float(cal.y(top - widen)), bar_lo_outer=float(cal.y(bot + widen)),
                       px_lo=float(top), px_hi=float(bot))
        rec["note"] = "; ".join(notes)
        rec["_own"] = k["own"]
        out.append(rec)
    if one_per_x:   # two fits in one column are one point: keep the more visible
        keep = []
        for rec in sorted(out, key=lambda r: -r["_own"]):
            if all(abs(rec["px"][0] - o["px"][0]) > 0.6 * ws for o in keep):
                keep.append(rec)
        out = sorted(keep, key=lambda r: r["px"][0])
    for rec in out:
        del rec["_own"]
    return out


# ---------------------------------------------------------------- a line, read column by column
def read_line_at(img, cal, colour, at, exclude=(), half_window=3):
    """A single line of one colour, read at the x positions `at`: in the columns within +-half_window of
    each position, the line's pixels (the run of the colour nearest the top: the curve, not anything drawn
    along the x axis below it) span rows a..b; the value is their middle and the 95% interval covers the
    whole span (a steep line crosses a column in a tall run), plus 2 px + 2 x the y misfit."""
    inside = box_mask(img.shape[:2], cal, exclude)
    m = mask_of(img, colour) & inside
    out = []
    for x in at:
        c = int(round(cal.col(x)))
        rs = []
        for cc in range(c - half_window, c + half_window + 1):
            col_runs = runs(m[:, cc])
            if col_runs:
                rs.append(col_runs[0])
        if not rs:
            out.append({"x": float(x), "y": None, "note": "no line in these columns"})
            continue
        a = float(np.median([r[0] for r in rs]))
        b = float(np.median([r[1] for r in rs]))
        mid = (a + b) / 2
        half = (b - a) / 2 + 2 + 2 * cal.ymis
        y = cal.y(mid)
        out.append({"x": float(x), "y": float(y), "lo": float(min(cal.y(mid - half), cal.y(mid + half))),
                    "hi": float(max(cal.y(mid - half), cal.y(mid + half))), "px": [float(c), mid],
                    "px_lo": a, "px_hi": b,
                    "note": f"line spans rows {a:.0f}-{b:.0f} here (its thickness, more where steep); {cal.note()}"})
    return out


# ---------------------------------------------------------------- bar charts
def read_bar_tops(img, cal, colour, min_width=20, stem=5, exclude=(), cap_max=None, bar_colour="black"):
    """Bars of one colour: each bar's value is its top edge (median over its columns): where the bar has a
    dark outline, the middle of the outline's top line. Its error bar (drawn in `bar_colour`) is the stem
    above the top; the lower half is inside the bar, taken as the mirror of the upper."""
    inside = box_mask(img.shape[:2], cal, exclude)
    m = mask_of(img, colour) & inside
    dk = mask_of(img, bar_colour) & inside
    body = ndimage.binary_opening(m, structure=np.ones((1, 2 * stem + 3), bool))
    body = ndimage.binary_opening(body, structure=np.ones((2 * stem + 3, 1), bool))
    lab, n = ndimage.label(body)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        sub = lab[sl] == i
        w = sl[1].stop - sl[1].start
        if w < min_width or sl[0].stop < cal.bottom - 15:
            continue   # a bar stands on the x axis
        col = (sl[1].start + sl[1].stop - 1) / 2
        cols = [c for c in range(sl[1].start + w // 5, sl[1].stop - w // 5) if abs(c - col) > 2 * stem]
        tops = [sl[0].start + int(np.flatnonzero(sub[:, c - sl[1].start])[0]) for c in cols]
        top = float(np.median(tops))
        note = f"bar {w} px wide, top edge"
        outline = 0.0
        if colour != bar_colour:
            # a dark outline just above the fill: its middle row is the edge
            th = []
            for c, t in zip(cols, tops):
                r = t - 1
                while r > 0 and t - r <= 3 and not dk[r, c]:
                    r -= 1
                n = 0
                while r - n > 0 and dk[r - n, c]:
                    n += 1
                if n:
                    th.append((r - (n - 1) / 2, n))
            if len(th) > 0.5 * len(cols):
                top = float(np.median([a for a, _ in th]))
                outline = float(np.median([n for _, n in th]))
                note += f" (middle of its {outline:.0f} px outline)"
        cap = _cap_end(dk, col, int(round(top)), -1, cal.top, stem, 3 * stem, cap_max or 0.8 * w, 30)
        half = 1 + 2 * cal.ymis + outline / 2
        widen = 2 + 2 * cal.ymis
        rec = {"col": col, "y": float(cal.y(top)), "lo": float(cal.y(top + half)), "hi": float(cal.y(top - half)),
               "px": [float(col), top], "note": note + "; " + cal.note()}
        if cap is not None:
            rec.update(bar_hi=float(cal.y(cap)), bar_lo=float(cal.y(2 * top - cap)),
                       bar_hi_outer=float(cal.y(cap - widen)), bar_lo_outer=float(cal.y(2 * top - cap + widen)),
                       px_lo=float(cap), px_hi=float(2 * top - cap))
            rec["note"] += "; lower bar end hidden in the bar, taken as the mirror of the upper"
        else:
            rec["note"] += "; no error bar found above the bar"
        out.append(rec)
    return sorted(out, key=lambda r: r["col"])
