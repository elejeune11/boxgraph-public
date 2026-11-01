"""Shared reading code for the data figures of Elosegui-Artola et al. 2014 (vector plots).

Each reading file (figures/<reading id>.py) holds a CONFIG dict and calls one reader below. The
reading file pins this file's SHA-256, since the build caches a reading by the bytes of the reading
file only. Everything is found in the image; what is typed in is the printed tick labels (matched
in order to the tick marks found), the series colours, and which gel or group each found marker or
bar is (by its order from the left).

Calibration
- y axis: the leftmost long dark vertical line. Its ticks are dark stubs just left of it, matched
  bottom to top to the printed labels and fitted by a straight line; misfit = RMS residual (px).
- x axis with ticks (`xticks`): the bottom axis is the longest dark row in the lower part; ticks
  are dark stubs just below it, matched left to right to the labels (log10 or linear fit).
- x axis without ticks (`xlabels_only`, Figs. 3 and 4): the only marks are the printed labels. Each
  label's centre column is taken as its position and fitted on a log10 scale; the misfit is large
  (the labels are not evenly spaced), and it is carried into the reading's interval.

Markers (`read_markers`)
- T: the series colour; O (occluder): other series colours, dark ink and the white inside of open
  circles; B: everything else. r: the marker radius, the largest inscribed radius of T.
- filled markers: the disk of radius r with at most 4% B and at least 15% T, and whose inner disk
  (0.5 r) is at least half T; its centre is where T + 0.5 O - 3 B is largest; the interval of the
  centre is every row (same column) where a disk still passes, plus 1 px and twice the y misfit.
- open markers: a ring (0.7 r to r) at least 60% T, with its inner disk (0.5 r) at most 25% T.
- the k-th marker from the left is the k-th gel in CONFIG['present']; gels not present are
  reported as not readable (hidden behind another marker).
- error bars: along the stem column from the marker edge, up and down, through T (and O, which may
  be drawn over the stem). The bar ends at the first cap (a horizontal T run at least 2.5 stem
  widths wide across the stem) or where T stops; the end is half a line width inside the outer
  edge. A stem that never leaves the marker is reported as at most the marker. A stem ending in O
  is hidden there: its end is taken as the mirror of the other end, and the outer interval spans
  both. The outer interval adds 1.5 px and twice the y misfit to each end.
Bars (`read_bars`)
- bars are columns of the fill colour standing on the x axis; each bar's top is the top outline
  (dark) above the fill in the bar's centre column; the value is at the outline's centre. The
  error bar is the dark stem above the top, ending in a cap, read as for markers (upper end only;
  the lower half is hidden by the bar and is taken as the mirror of the upper, as SEM bars are
  symmetric).
Curves (`read_curve`)
- the curve colour mask, with markers and their error bars removed (columns where the curve mask
  has more than one run or a run thicker than 1.6 line widths are not used). At each x, the
  curve row is the centre of the run nearest the previous column's row; where the column is not
  clean, it is interpolated (in pixels) from clean columns on both sides, and the interval covers
  the clean rows within the gap. The interval adds half a line width and twice the y misfit; with
  `xlabels_only` it also spans the curve over x +- the x misfit.
- `at_markers`: read the curve at the columns of the markers of another series (same panel), so
  that a model line and the measured points are compared at the same gel.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve


# ---------------------------------------------------------------- masks
def _f(img):
    return np.asarray(img)[..., :3].astype(float)


def dark(img, thr=110, sat=60):
    f = _f(img)
    mx, mn = f.max(2), f.min(2)
    return (mx < thr) & (mx - mn < sat)


def colour(img, rgb, tol=60):
    f = _f(img)
    return np.sqrt(((f - np.array(rgb, float)) ** 2).sum(2)) < tol


def _k(v):
    """A key for a gel or group: numbers by value (the build passes x positions as numbers)."""
    try:
        return f"{float(v):g}"
    except (TypeError, ValueError):
        return str(v)


def _runs(v):
    m = np.concatenate([[False], np.asarray(v, bool), [False]]).astype(int)
    d = np.diff(m)
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1))


def _centres(idx, gap=2):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return [float(np.mean(g)) for g in out]


# ---------------------------------------------------------------- calibration
class Axis:
    def __init__(self, pos, labels, scale="linear"):
        self.pos = np.array(pos, float)
        self.labels = [float(v) for v in labels]
        self.scale = scale
        t = self._t(np.array(self.labels))
        if len(pos) < 2:
            raise RuntimeError("fewer than two marks")
        self.a, self.b = np.polyfit(t, self.pos, 1)
        res = self.pos - np.polyval([self.a, self.b], t)
        self.misfit = float(np.sqrt(np.mean(res ** 2))) if len(pos) > 2 else 0.5
        self.resid = [float(r) for r in res]

    def _t(self, v):
        return np.log10(v) if self.scale == "log10" else v

    def px(self, value):
        return float(self.a * self._t(np.array(value, float)) + self.b)

    def value(self, p):
        t = (p - self.b) / self.a
        return float(10 ** t if self.scale == "log10" else t)


def _left_axis(dk, min_frac=0.3, skip=0):
    h, w = dk.shape
    best = np.zeros(w, int)
    for c in range(w):
        rs = _runs(dk[:, c])
        if rs:
            best[c] = max(b - a + 1 for a, b in rs)
    cols = list(np.flatnonzero(best >= min_frac * h))
    groups = []
    for c in cols:
        if groups and c - groups[-1][-1] <= 2:
            groups[-1].append(c)
        else:
            groups.append([c])
    g = groups[skip]
    c = g[len(g) // 2]
    # the axis line may be interrupted where a coloured line or marker crosses it: its extent is
    # from the first to the last of its long dark runs
    rs = [r for r in _runs(dk[:, c]) if r[1] - r[0] >= 20]
    longest = max(rs, key=lambda r: r[1] - r[0])
    near = [r for r in rs if r[0] - 60 <= longest[1] and r[1] + 60 >= longest[0]] or [longest]
    # grow while the next run starts within 60 px of the current extent
    r0, r1 = longest
    changed = True
    while changed:
        changed = False
        for a, b in rs:
            if (a <= r1 + 60 and b > r1) or (b >= r0 - 60 and a < r0):
                r0, r1 = min(r0, a), max(r1, b)
                changed = True
    del near
    return g[0], g[-1], r0, r1


def calibrate(img, cfg):
    """cfg: ylabels (bottom up), probe (tick probe, px), xmode ('ticks' | 'labels' | None),
    xlabels (left to right), xscale."""
    dk = dark(img, cfg.get("dark_thr", 110))
    if cfg.get("yrows"):
        # several panels stacked in one crop: this panel's y axis lies within these rows
        ya, yb = cfg["yrows"]
        band = np.zeros_like(dk)
        band[ya:yb] = dk[ya:yb]
        c0, c1, r0, r1 = _left_axis(band, cfg.get("vmin_frac", 0.3) * (yb - ya) / dk.shape[0], cfg.get("vskip", 0))
    else:
        c0, c1, r0, r1 = _left_axis(dk, cfg.get("vmin_frac", 0.3), cfg.get("vskip", 0))
    p0, p1 = cfg.get("probe", (4, 14))
    band = dk[:, max(0, c0 - p1):c0 - p0]
    rows = [r for r in np.flatnonzero(band.mean(1) >= 0.85) if r0 - 10 <= r <= r1 + 10]
    t = _centres(rows)
    labels = cfg["ylabels"]
    if len(t) != len(labels):
        raise RuntimeError(f"y axis: {len(t)} ticks for {len(labels)} labels: {[round(v) for v in t]}")
    cal = {"dk": dk, "left": (c0, c1, r0, r1)}
    cal["y"] = Axis(sorted(t, reverse=True), labels, cfg.get("yscale", "linear"))
    xm = cfg.get("xmode")
    if xm == "ticks":
        h = dk.shape[0]
        lo = h // 3
        cov = dk[lo:, c1 + 2:].sum(1)
        top = int(np.argmax(cov)) + lo
        rr = [r for r in range(top - 15, top + 15) if dk[r, c1 + 2:].sum() > 0.6 * cov.max()]
        top, bot = min(rr), max(rr)
        below = dk[bot + p0 + 1:bot + p1 + 1, :].mean(0) >= 0.85
        xt = _centres([c for c in np.flatnonzero(below) if c >= c0 - 4])
        if len(xt) != len(cfg["xlabels"]):
            raise RuntimeError(f"x axis: {len(xt)} ticks for {len(cfg['xlabels'])} labels: {[round(v) for v in xt]}")
        cal["x"] = Axis(xt, cfg["xlabels"], cfg.get("xscale", "linear"))
        cal["xaxis_row"] = (top + bot) / 2
    elif xm == "labels":
        # text below the foot of the y axis: dark components, grouped into labels by proximity
        y0 = r1 + cfg.get("label_gap", 15)
        y1 = y0 + cfg.get("label_height", 160)
        if cfg.get("xlabel_rows"):  # the shared x labels under the bottom panel of a stack
            y0, y1 = cfg["xlabel_rows"]
        sub = dk[y0:y1, :]
        cols = np.flatnonzero(sub.any(0))
        groups = []
        for c in cols:
            if groups and c - groups[-1][-1] <= cfg.get("label_join", 40):
                groups[-1].append(c)
            else:
                groups.append([c])
        cen = [(g[0] + g[-1]) / 2 for g in groups if g[-1] - g[0] > 10]
        if len(cen) != len(cfg["xlabels"]):
            raise RuntimeError(f"x labels: found {len(cen)} label groups for {len(cfg['xlabels'])}: {cen}")
        cal["x"] = Axis(cen, cfg["xlabels"], cfg.get("xscale", "log10"))
        cal["x_from_labels"] = True
    return cal


def cal_note(cal):
    s = f"y ticks misfit {cal['y'].misfit:.1f} px"
    if "x" in cal:
        s += f", x {'label centres' if cal.get('x_from_labels') else 'ticks'} misfit {cal['x'].misfit:.1f} px"
    return s


# ---------------------------------------------------------------- disks
def _disk(r):
    k = int(np.ceil(r))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    return (xx ** 2 + yy ** 2 <= r * r).astype(float)


def _ring(r0, r1):
    k = int(np.ceil(r1))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    d2 = xx ** 2 + yy ** 2
    return ((d2 <= r1 * r1) & (d2 >= r0 * r0)).astype(float)


def _frac(mask, kern):
    return fftconvolve(mask.astype(float), kern, mode="same") / kern.sum()


def _plot_box(cal, img):
    c0, c1, r0, r1 = cal["left"]
    return c1 + 3, img.shape[1], r0, r1 + 3


def find_markers(img, cal, cfg):
    """Markers of the series, left to right: [(col, row, row_lo, row_hi, r)]."""
    T = colour(img, cfg["color"], cfg.get("tol", 60))
    others = np.zeros_like(T)
    for c in cfg.get("others", []):
        others |= colour(img, c, cfg.get("tol", 60))
    others |= cal["dk"]
    allc = T.copy()
    for c in cfg.get("same_family", []):
        allc |= colour(img, c, cfg.get("tol", 60))
    x0, x1, y0, y1 = _plot_box(cal, img)
    box = np.zeros_like(T)
    bx = cfg.get("box")
    if bx:
        box[bx[1]:bx[3], bx[0]:bx[2]] = True
    else:
        box[y0:y1, x0:x1] = True
    if cfg.get("r"):
        r = float(cfg["r"])
    else:
        # the marker size, from this series or (when its markers are mostly hidden) a sister series
        # drawn with the same marker in the same panel
        RT = colour(img, cfg["r_from"], cfg.get("tol", 60)) if cfg.get("r_from") else T
        filled = ndi.binary_fill_holes(RT) & box
        edt = ndi.distance_transform_edt(filled)
        lab, n = ndi.label(filled)
        mx = np.array(ndi.maximum(edt, lab, range(1, n + 1))) if n else np.array([4.0])
        mx = mx[mx >= 0.6 * mx.max()]
        r = float(np.median(mx))  # the typical marker; a few are merged with caps or other marks
    # the white inside of open circles: small holes enclosed by the series' colours
    holes = ndi.binary_fill_holes(allc) & ~allc
    lab, n = ndi.label(holes)
    if n:
        sizes = ndi.sum(holes, lab, range(1, n + 1))
        small = np.zeros(n + 1, bool)
        small[1:] = sizes <= 1.2 * np.pi * r * r
        holes = small[lab]
    O = others | holes
    open_ = cfg.get("open", False)
    if open_:
        fr = _frac(T, _ring(0.72 * r, 0.98 * r))
        fi = _frac(T, _disk(0.5 * r))
        fw = _frac(~T & ~others, _disk(0.5 * r))  # white inside (a line may cross it)
        # the ring must be drawn all round: each quadrant of it at least 40% T
        k = int(np.ceil(0.98 * r))
        quads = []
        ring = _ring(0.72 * r, 0.98 * r)
        yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
        for sy, sx in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            q = ring * ((np.sign(yy) == sy) & (np.sign(xx) == sx))
            quads.append(_frac(T, q))
        fq = np.minimum.reduce(quads)
        cand = ((fr >= cfg.get("ring_min", 0.6)) & (fq >= cfg.get("quad_min", 0.4)) & (fw >= cfg.get("white_min", 0.2))
                & (fi <= cfg.get("inner_max", 0.4)) & box)
        score = fr - fi
        blo = None
    else:
        k = _disk(r - 0.5)
        fT, fO = _frac(T, k), _frac(O, k)
        fB = 1 - fT - fO
        # the inner disk is mostly the series' colour; for a series drawn under another one
        # (`under`), mostly the colour or the other marks over it (not the white of an open circle)
        fi = _frac((T | others) if cfg.get("under") else T, _disk(0.5 * r))
        cand = (fB <= 0.04) & (fT >= 0.15) & (fi >= cfg.get("inner_min", 0.5)) & box
        score = fT + 0.5 * fO - 3 * fB
    lab, n = ndi.label(cand)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        j = int(np.argmax(score[rr, cc]))
        r_c, c_c = int(rr[j]), int(cc[j])
        col_rows = rr[cc == c_c]
        out.append((float(c_c), float(r_c), float(col_rows.min()), float(col_rows.max()), r))
    # candidates closer than r are one marker: the best-scoring centre, the rows of both as its interval
    out.sort()
    merged = []
    for m in out:
        hit = next((i for i, p in enumerate(merged) if abs(m[0] - p[0]) < 1.5 * r and abs(m[1] - p[1]) < 1.5 * r),
                   None)
        if hit is not None:
            p = merged[hit]
            best = m if score[int(m[1]), int(m[0])] > score[int(p[1]), int(p[0])] else p
            merged[hit] = (best[0], best[1], min(m[2], p[2]), max(m[3], p[3]), r)
            continue
        merged.append(m)
    merged.sort(key=lambda m: m[0])
    return merged, T, O, r


def _line_width(T):
    """The width of the series' thin lines (error-bar stems and caps): the most common run length
    of 2-30 px, across rows and columns."""
    cnt = np.zeros(31, int)
    for M in (T, T.T):
        for line in M[::3]:
            for a, b in _runs(line):
                n = b - a + 1
                if 2 <= n <= 30:
                    cnt[n] += 1
    return float(np.argmax(cnt)) if cnt.sum() else 5.0


def _stem_width(T, rows, c):
    ws = []
    for r in rows:
        for a, b in _runs(T[r, max(0, c - 30):c + 31]):
            if a <= 30 <= b:
                ws.append(b - a + 1)
    return float(np.median(ws)) if ws else 4.0


def _follow(T, O, c, cy, rad, step, w, limit=2000):
    """From the marker centre row cy along column c (+-1), in direction step: the outer edge row of
    the stem, whether it ended at a cap, whether it ended inside an occluder, and the cap's centre
    row. A cap is a horizontal T run across the stem at least 2.5 line widths wide and wider than
    the marker's own chord at that row (so the marker is not taken for a cap)."""
    h, wd = T.shape
    last_t = None
    gap = 0
    capped = False
    cap_rows = []
    d = int(w + 3)
    r = int(round(cy)) + step * d
    while 0 <= r < h and d < limit:
        seg_t = T[r, max(0, c - 1):c + 2].any()
        seg_o = O[r, max(0, c - 1):c + 2].any()
        if seg_t:
            last_t = r
            gap = 0
            run = [ab for ab in _runs(T[r, max(0, c - 150):c + 151]) if ab[0] <= 151 and ab[1] >= 149]
            ln = (run[0][1] - run[0][0] + 1) if run else 0
            # a cap is centred on the stem; a line of the same colour crossing it is not
            sym = bool(run) and abs((150 - run[0][0]) - (run[0][1] - 150)) <= max(w + 2, 0.25 * ln)
            if sym:
                # and not a sloping line of the same colour crossing the stem: such a line has its
                # colour above one arm and below the other (a cap next to a circle or another cap
                # has it on the same side of both arms, or nowhere)
                off = int(w + 2)
                a = int(0.35 * ln)

                def t(rr, cc):
                    return 0 <= rr < h and 0 <= cc < wd and bool(T[rr, cc])
                ul, ur, dl, dr = t(r - off, c - a), t(r - off, c + a), t(r + off, c - a), t(r + off, c + a)
                if (ul and dr and not ur and not dl) or (ur and dl and not ul and not dr):
                    sym = False
            chord = 2 * np.sqrt(max(rad * rad - d * d, 0.0))
            # caps are looked for only from the marker's edge outwards (inside it, the horizontal
            # error bar crosses the stem)
            if d >= rad - w and ln >= 2.5 * w and ln > chord + 2 * w and sym and 1.2 * rad <= ln <= 3.5 * rad:
                cap_rows.append(r)
                capped = True
            elif capped:
                break
        elif seg_o:
            gap = 0
            if capped:
                break
        else:
            gap += 1
            if gap > 2:
                break
        r += step
        d += 1
    ended_in_o = (last_t is not None and not capped and 0 <= last_t + step < h
                  and O[last_t + step, max(0, c - 1):c + 2].any())
    cap_c = float(np.mean(cap_rows)) if cap_rows else None
    return last_t, capped, ended_in_o, cap_c


def error_bar(T, O, col, row, r, ax, misfit, up=True, down=True, lw=None):
    """Ends of the vertical error bar of a marker at (col, row) with radius r, as values."""
    c = int(round(col))
    probe = int(row - r - 4)
    # stem column: T column nearest c just outside the marker, above or below
    best = None
    for pr in (probe, int(row + r + 4)):
        if 0 <= pr < T.shape[0]:
            cs = [cc for cc in range(c - int(r / 2), c + int(r / 2) + 1) if T[pr, cc]]
            if cs:
                best = int(round(np.mean(cs)))
                break
    if best is None:
        best = c  # no stem outside the marker: look for caps at its edge from the centre column
    w = float(lw) if lw else _line_width(T)
    ends = {}
    for name, step, ok in (("hi", -1, up), ("lo", +1, down)):
        if not ok:
            continue
        last, capped, in_o, cap_c = _follow(T, O, best, row, r, step, w)
        if capped:
            ends[name] = ("cap", cap_c)
        elif last is None or abs(last - row) <= r + 1:
            ends[name] = ("inside", row + step * r)
        elif in_o:
            ends[name] = ("hidden", last)
        else:
            ends[name] = ("end", last - step * w / 2)
    return ends, w, best


def bar_values(ends, row, r, ax, misfit):
    """Convert error-bar ends (rows) to bar_lo, bar_hi and outer interval, with notes."""
    notes = []
    pad = 1.5 + 2 * misfit
    hi = ends.get("hi")
    lo = ends.get("lo")
    if hi and lo and hi[0] == "inside" and lo[0] == "inside":
        notes.append("error bar hidden in the marker: at most the marker")
        rows_hi, rows_lo = row - r, row + r
        return ax.value(rows_lo), ax.value(rows_hi), ax.value(rows_lo + pad), ax.value(rows_hi - pad), notes, rows_hi, rows_lo
    def side(e, other, sgn):
        if e is None or e[0] == "hidden" or e[0] == "inside":
            if other and other[0] in ("cap", "end"):
                mir = 2 * row - other[1]
                if e is not None and e[0] == "hidden":
                    notes.append(f"{'upper' if sgn < 0 else 'lower'} end hidden behind another mark: mirror of the other end")
                    span = (min(mir, e[1]), max(mir, e[1]))
                else:
                    notes.append(f"{'upper' if sgn < 0 else 'lower'} end inside the marker: mirror of the other end")
                    span = (min(mir, row + sgn * r), max(mir, row + sgn * r))
                return mir, span
            return row + sgn * r, (row + sgn * r, row + sgn * r)
        return e[1], (e[1], e[1])
    hrow, hspan = side(hi, lo, -1)
    lrow, lspan = side(lo, hi, +1)
    b_hi, b_lo = ax.value(hrow), ax.value(lrow)
    o_hi = ax.value(min(hspan) - pad)
    o_lo = ax.value(max(lspan) + pad)
    return b_lo, b_hi, o_lo, o_hi, notes, hrow, lrow


def read_markers(image, at, cfg):
    img = np.asarray(image)
    cal = calibrate(img, cfg)
    ax = cal["y"]
    m = ax.misfit
    found, T, O, r = find_markers(img, cal, cfg)
    present = [_k(p) for p in cfg["present"]]
    if len(found) != len(present):
        raise RuntimeError(f"found {len(found)} markers, expected {len(present)}: "
                           f"{[(round(f[0]), round(f[1])) for f in found]}")
    by_gel = dict(zip(present, found))
    out = []
    for a in at:
        key = _k(a)
        x = float(a)
        if key not in by_gel:
            out.append({"x": x, "y": None, "note": cfg.get("missing_note", {}).get(key, "no marker of this series is visible here (hidden behind another marker)")})
            continue
        col, row, rlo, rhi, rr = by_gel[key]
        y = ax.value(row)
        lo, hi = ax.value(rhi + 1 + 2 * m), ax.value(rlo - 1 - 2 * m)
        rec = {"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [col, row]}
        xs = f"; marker column {col:.0f}" + (f" (x as read {cal['x'].value(col):.3g})" if "x" in cal else "")
        note = f"{cal_note(cal)}; marker r {rr:.0f} px{xs}"
        ov = cfg.get("bars_override", {}).get(key, {})
        if cfg.get("error_bars", True):
            eb = error_bar(T, O, col, row, rr, ax, m, up=ov.get("up", True), down=ov.get("down", True),
                           lw=cfg.get("lw"))
            if eb is None:
                rec.update({"bar_lo": rec["lo"], "bar_hi": rec["hi"], "bar_lo_outer": ax.value(row + rr + 1.5 + 2 * m),
                            "bar_hi_outer": ax.value(row - rr - 1.5 - 2 * m)})
                note += "; no stem found: error bar at most the marker"
            else:
                ends, w, sc = eb
                for k in ("hi", "lo"):
                    if ov.get(k) == "hidden" and k in ends and ends[k][0] != "inside":
                        ends[k] = ("hidden", ends[k][1])
                b_lo, b_hi, o_lo, o_hi, notes, hrow, lrow = bar_values(ends, row, rr, ax, m)
                rec.update({"bar_lo": min(b_lo, b_hi), "bar_hi": max(b_lo, b_hi),
                            "bar_lo_outer": min(o_lo, o_hi), "bar_hi_outer": max(o_lo, o_hi),
                            "px_lo": hrow, "px_hi": lrow})
                note += "; bar " + ",".join(f"{k}:{v[0]}" for k, v in sorted(ends.items()))
                if notes:
                    note += "; " + "; ".join(notes)
                if ov.get("note"):
                    note += "; " + ov["note"]
        rec["note"] = note
        out.append(rec)
    return out


# ---------------------------------------------------------------- bars
def read_bars(image, at, cfg):
    """cfg: fills (list of RGB of bar fills), groups (labels left to right of the bars found, by
    their order), ylabels..., zero: labels of groups with no visible bar (value at the axis)."""
    img = np.asarray(image)
    cal = calibrate(img, cfg)
    ax = cal["y"]
    m = ax.misfit
    dk = cal["dk"]
    c0, c1, r0, r1 = cal["left"]
    axis_row = int(round(ax.px(0.0)))
    alw = float(c1 - c0 + 1)  # the axis line width: the bars' outlines are drawn as heavy
    # bar columns: each fill colour present in a band just above the axis line
    lo_b, hi_b = axis_row - cfg.get("band", (14, 7))[0], axis_row - cfg.get("band", (14, 7))[1]
    bars = []
    for fc in cfg["fills"]:
        fm = colour(img, fc, cfg.get("tol", 50))
        colmask = fm[lo_b:hi_b, c1 + 3:].mean(0) > 0.5
        for a, b in _runs(colmask):
            if b - a > 20:
                bars.append((a + c1 + 3, b + c1 + 3, tuple(fc)))
    bars.sort()
    groups = [_k(g) for g in cfg["groups"]]
    if len(bars) != len(groups):
        raise RuntimeError(f"found {len(bars)} bars for {len(groups)} groups: {[(b[0], b[1]) for b in bars]}")
    by = dict(zip(groups, bars))
    out = []
    for a in at:
        key = _k(a)
        x = float(a)
        if key not in by:
            out.append({"x": x, "y": None, "note": cfg.get("missing_note", {}).get(key, "no bar")})
            continue
        b0, b1, fc = by[key]
        fill = colour(img, fc, cfg.get("tol", 50))
        is_dark = bool(dk[(lo_b + hi_b) // 2, (b0 + b1) // 2])
        # the bar's top edge, at a quarter and three quarters of its width (clear of the stem)
        tops = []
        for cc in (b0 + (b1 - b0) // 4, b1 - (b1 - b0) // 4):
            fr = [ab for ab in _runs(fill[:axis_row, cc]) if ab[1] >= hi_b - 2]
            ftop = fr[-1][0]
            k = ftop - 1
            while k > 0 and dk[k, cc]:
                k -= 1
            tops.append((k + 1, ftop))
        otop = float(np.mean([t[0] for t in tops]))
        ftop = float(np.mean([t[1] for t in tops]))
        if is_dark:
            # a black bar: its outline is not told apart from its fill; the outline's centre is
            # half an axis-line width below the top edge
            lw = alw
            outline = otop + lw / 2 - 0.5
        else:
            lw = max(1.0, ftop - otop)
            outline = otop + lw / 2 - 0.5
        cc = (b0 + b1) // 2
        y = ax.value(outline)
        rec = {"x": x, "y": y, "lo": ax.value(outline + lw / 2 + 1 + 2 * m), "hi": ax.value(outline - lw / 2 - 1 - 2 * m),
               "px": [float(cc), float(outline)]}
        # error bar: dark stem above the bar top near the centre column
        probe_row = int(otop) - 4
        q = (b1 - b0) // 4
        stem_cols = [c for c in range(b0 + q, b1 - q) if dk[probe_row, c]]
        note = f"{cal_note(cal)}; bar columns {b0}-{b1}" + ("; a black bar" if is_dark else "")
        if stem_cols and len(stem_cols) < 0.5 * (b1 - b0):
            sc = int(round(np.mean(stem_cols)))
            w = len(stem_cols)
            r = probe_row
            cap = []
            last = r
            while r > 0 and dk[r, sc]:
                runs = [ab for ab in _runs(dk[r, sc - 100:sc + 101]) if ab[0] <= 101 and ab[1] >= 99]
                if runs and runs[0][1] - runs[0][0] + 1 >= 2.5 * w:
                    cap.append(r)
                elif cap:
                    break
                last = r
                r -= 1
            top_row = float(np.mean(cap)) if cap else last + w / 2
            hi_v = ax.value(top_row)
            mir = 2 * outline - top_row
            pad = 1.5 + 2 * m
            rec.update({"bar_hi": hi_v, "bar_lo": ax.value(mir), "bar_hi_outer": ax.value(top_row - pad),
                        "bar_lo_outer": ax.value(mir + pad), "px_lo": top_row, "px_hi": mir})
            note += f"; error bar upper end {'at its cap' if cap else 'at the stem end'}; lower end hidden by the bar: mirror of the upper"
        else:
            rec.update({"bar_hi": rec["hi"], "bar_lo": rec["lo"], "bar_hi_outer": rec["hi"], "bar_lo_outer": rec["lo"]})
            note += "; no error bar stem visible above the bar: at most the bar's outline"
        rec["note"] = note
        out.append(rec)
    return out


# ---------------------------------------------------------------- curves
def _trace(M, seed, lw, min_len, max_jump):
    """Trace a line through the column runs of M from seed (col, row), both ways. A column is
    clean when the run nearest the previous centre is no thicker than the line at the local slope
    would be (1.6 line widths, stretched by the slope, + 2 px); otherwise (a marker, an error bar
    or another line merged with it) the column is left out and the trace carries on."""
    h, w = M.shape
    rows = [None] * w
    sc, sr = int(seed[0]), float(seed[1])
    for step in (+1, -1):
        prev = sr
        hist = []
        c = sc if step > 0 else sc - 1
        miss = 0
        while 0 <= c < w:
            rs = [(a, b) for a, b in _runs(M[:, c]) if b - a + 1 >= min_len]
            if rs:
                a, b = min(rs, key=lambda ab: abs((ab[0] + ab[1]) / 2 - prev))
                cen = (a + b) / 2
                if abs(cen - prev) <= max_jump + (b - a) / 2 + 4.0 * miss:
                    s = abs(hist[-1] - hist[-6]) / 5 if len(hist) >= 6 else 0.0
                    s = max(s, abs(cen - prev) / (miss + 1))  # the slope across a gap
                    if b - a + 1 <= 1.6 * lw * np.sqrt(1 + s * s) + 2:
                        rows[c] = cen
                        hist.append(cen)
                        prev = cen
                        miss = 0
                    else:
                        miss += 1
                else:
                    miss += 1
            else:
                miss += 1
            if miss > 300:
                break
            c += step
    return rows


def curve_rows(img, cal, cfg, blank=()):
    M = colour(img, cfg["color"], cfg.get("tol", 60))
    if cfg.get("vclose"):
        # a thinner line of another colour drawn along this one splits it into two strips: a
        # vertical closing joins them again
        M = ndi.binary_closing(M, structure=np.ones((int(cfg["vclose"]), 1), bool))
    # markers of the same colour on the line are blanked, with their horizontal error bars and
    # caps (a box `blank_x` r to each side and 1.5 r up and down), so the trace does not take
    # them for the line; the line is interpolated across the blanked columns
    for bc, br, brad in blank:
        kx, ky = int(cfg.get("blank_x", 1.3) * brad), int(1.5 * brad)
        M[max(0, int(br) - ky):int(br) + ky + 1, max(0, int(bc) - kx):int(bc) + kx + 1] = False
    if cfg.get("open_px"):
        # the model lines of Fig. 4 are about three times as thick as the error bars and caps
        # of the same colour: an opening with a disk removes the thin marks and keeps the line
        M = ndi.binary_opening(M, structure=_disk(cfg["open_px"]).astype(bool))
    x0, x1, y0, y1 = _plot_box(cal, img)
    M[:, :max(0, x0 - 2)] = False
    if cfg.get("box"):
        b = cfg["box"]
        keep = np.zeros_like(M)
        keep[b[1]:b[3], b[0]:b[2]] = True
        M &= keep
    # one seed, or several, each traced only within its own column range [c_from, c_to); "auto":
    # the line where it leaves the y axis (the model lines of Fig. 4 start at the axis)
    if cfg.get("seed") == "auto":
        sc = x0 + cfg.get("auto_offset", 25)
        rs = [ab for ab in _runs(M[:, sc]) if y0 <= ab[0] <= y1]
        if not rs:
            raise RuntimeError("no line where it leaves the y axis")
        a, b = max(rs, key=lambda ab: ab[1] - ab[0])
        cfg = dict(cfg, seed=[sc, (a + b) / 2])
    seeds = cfg.get("seeds") or [list(cfg["seed"]) + [0, M.shape[1]]]
    rows = [None] * M.shape[1]
    lws = []
    for sc, sr, cf, ct in seeds:
        # the run of the line's colour in the seed column nearest the seed row (within 80 px)
        run = sorted([ab for ab in _runs(M[:, int(sc)]) if abs((ab[0] + ab[1]) / 2 - sr) <= 80],
                     key=lambda ab: abs((ab[0] + ab[1]) / 2 - sr))
        if not run:
            raise RuntimeError(f"no line near the seed {(sc, sr)}")
        sr = (run[0][0] + run[0][1]) / 2
        lw = float(cfg.get("lw") or (run[0][1] - run[0][0] + 1))
        lws.append(lw)
        part = _trace(M, (sc, sr), lw, cfg.get("min_len", 1), cfg.get("max_jump", 12))
        for c in range(max(0, int(cf)), min(M.shape[1], int(ct))):
            rows[c] = part[c]
    return rows, max(lws)


def _interp(rows, col, maxgap):
    """Row at column col: clean or interpolated from neighbours; also the row span covered."""
    w = len(rows)
    c = int(round(col))
    if 0 <= c < w and rows[c] is not None:
        return rows[c], rows[c], rows[c], 0
    L = next((k for k in range(c - 1, max(-1, c - maxgap), -1) if 0 <= k < w and rows[k] is not None), None)
    R = next((k for k in range(c + 1, min(w, c + maxgap)) if rows[k] is not None), None)
    if L is None or R is None:
        return None, None, None, None
    t = (col - L) / (R - L)
    v = rows[L] + t * (rows[R] - rows[L])
    return v, min(rows[L], rows[R], v), max(rows[L], rows[R], v), R - L


def read_curve(image, at, cfg):
    img = np.asarray(image)
    cal = calibrate(img, cfg)
    ax = cal["y"]
    m = ax.misfit
    maxgap = cfg.get("maxgap", 200)
    out = []
    cols = []
    blank = []
    if cfg.get("at_markers"):
        mk = dict(cfg["at_markers"])
        mk["ylabels"] = cfg["ylabels"]
        found, _, _, _ = find_markers(img, cal, mk)
        present = [_k(p) for p in mk["present"]]
        if len(found) != len(present):
            raise RuntimeError(f"reference markers: found {len(found)}, expected {len(present)}")
        ref = dict(zip(present, [f[0] for f in found]))
        for a in at:
            cols.append(ref.get(_k(a)))
        if mk.get("color") == cfg.get("color"):
            blank += [(f[0], f[1], f[4]) for f in found]
        for extra in cfg.get("blank_also", []):  # other series of the line's colour
            ek = dict(extra)
            ek["ylabels"] = cfg["ylabels"]
            blank += [(f[0], f[1], f[4]) for f in find_markers(img, cal, ek)[0]]
    else:
        for a in at:
            cols.append(cal["x"].px(float(a)))
    rows, lw = curve_rows(img, cal, cfg, blank)
    for key, why in cfg.get("not_read", {}).items():
        if _k(key) in [_k(a) for a in at]:
            cols[[_k(a) for a in at].index(_k(key))] = ("skip", why)
    xm = cal["x"].misfit if cal.get("x_from_labels") and not cfg.get("at_markers") else 0.0
    xpx_per = None
    for a, col in zip(at, cols):
        x = float(a)
        if col is None:
            out.append({"x": x, "y": None, "note": "no reference marker for this gel"})
            continue
        if isinstance(col, tuple):
            out.append({"x": x, "y": None, "note": col[1]})
            continue
        v, vlo, vhi, gap = _interp(rows, col, maxgap)
        if v is None:
            out.append({"x": x, "y": None, "note": f"curve not found near column {col:.0f}"})
            continue
        lo_r, hi_r = vlo, vhi
        if xm > 0:
            for dc in np.arange(-2 * xm, 2 * xm + 1, 2.0):
                vv, a1, b1, _ = _interp(rows, col + dc, maxgap)
                if vv is not None:
                    lo_r, hi_r = min(lo_r, a1), max(hi_r, b1)
        pad = cfg.get("half_width_frac", 0.5) * lw + 1 + 2 * m
        y = ax.value(v)
        lo, hi = ax.value(hi_r + pad), ax.value(lo_r - pad)
        note = f"{cal_note(cal)}; line width {lw:.0f} px; column {col:.0f}"
        if gap:
            note += f"; interpolated across a {gap} px gap (markers or bars on the line)"
        if xm > 0:
            note += f"; interval spans x +- 2 x misfit ({2 * xm:.0f} px), the labels not being on one log scale"
        if cfg.get("at_markers"):
            note += "; read at the column of the measured marker of this gel"
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [float(col), float(v)],
                    "px_lo": float(lo_r - pad), "px_hi": float(hi_r + pad), "note": note})
    return out
