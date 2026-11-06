"""Shared reading code for the data figures of Andreu et al. 2021 (GraphPad-style raster plots).

Each reading file (figures/<reading id>.py) holds a CONFIG dict and calls one of the readers
below. The reading file pins this file's SHA-256, because the build caches a reading by the bytes
of the reading file only.

Everything is found in the image; the only things typed in are the printed tick labels that the
found tick marks are matched to (in order), the colours of the series, and which label of a
categorical axis each group is.

Calibration (`calibrate`)
- y axes: the long dark vertical lines of the plot. The ticks of a y axis are short dark stubs
  just outside the axis line (left of a left axis, right of a right axis). The stubs found are
  matched, bottom to top, to the printed labels and fitted by a straight line (in log10 of the
  label for a log axis). The misfit is the RMS residual in pixels.
- x axis: the row of the bottom axis line is the row with the most dark pixels in the lower part.
  Ticks are dark stubs just below it that are not dark just above it (so the // break marks and
  segment end marks, which cross the line, are not ticks). They are matched left to right to the
  printed labels; numeric labels are fitted in the same way (linear or log); a categorical label
  (Ns, Sq, a group name) keeps its tick column.
- A broken (two-segment) y axis is calibrated per segment.

Markers (`read_markers_at`, `read_markers_free`)
- target colour mask (the series' colour), occluder mask (other series' colours and black: things
  drawn possibly on top of the target), the rest is background.
- the marker radius r is the largest inscribed radius of the target mask (the disks are the
  thickest target shapes; stems and caps are thinner).
- centre: the disk of radius r maximising  T + 0.5 O - 3 B  (pixels of target, occluder,
  background inside the disk) near the tick column; a candidate with dark text right of it is the
  legend and is skipped.
- interval of the centre: all rows (same column) where the disk lies within target or occluder
  (at most 4% background) and still covers some target. For a fully visible marker this is the
  blur (1-2 px); for one partly behind another marker it spans every place it could be. Plus 1 px
  and twice the y misfit.
- error bars: from the centre, along the stem column, up and down while the target colour
  continues (gaps of occluder are crossed). The outer edge of the cap is the last target row; the
  bar end is the cap's centre line (half the cap thickness inside). If the stem ends inside an
  occluder, the end is hidden there: it is taken as the mirror of the other end, and the outer
  interval covers both the mirror and the hidden span. A bar that does not leave the marker is
  reported as at most the marker.
Scatter plots with a mean line (`read_means`)
- the mean is the longest dark horizontal run in the group's column band that does not touch the
  band's edges (a significance bar spans between groups and does); its row is its centre.
- error bar: the dark stem above and below the mean line, as for markers, ending in caps.
Histograms (`read_hist`)
- each bin at its labelled tick: the bar top is the first row from the top, in the bin's centre
  column, from which bar fill or outline continues down to the axis; the value is at the centre
  of the top outline.
"""
import numpy as np
from scipy import ndimage as ndi


# ---------------------------------------------------------------- masks
def _f(img):
    return np.asarray(img)[..., :3].astype(float)


def dark(img, thr=110, sat=60):
    f = _f(img)
    mx, mn = f.max(2), f.min(2)
    return (mx < thr) & (mx - mn < sat)


def colour(img, rgb, tol=70):
    f = _f(img)
    return np.sqrt(((f - np.array(rgb, float)) ** 2).sum(2)) < tol


def _runs(v):
    m = np.concatenate([[False], np.asarray(v, bool), [False]]).astype(int)
    d = np.diff(m)
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1))


def _groups(idx, gap=3):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def _centres(idx, gap=3):
    return [float(np.mean(g)) for g in _groups(list(idx), gap)]


# ---------------------------------------------------------------- calibration
class Axis:
    def __init__(self, pos, labels, scale="linear", what="y"):
        self.pos = np.array(pos, float)
        self.labels = list(labels)
        self.scale = scale
        v = self._t(np.array(labels, float))
        if len(pos) < 2:
            raise RuntimeError(f"{what} axis: fewer than two ticks")
        self.a, self.b = np.polyfit(v, self.pos, 1)
        res = self.pos - np.polyval([self.a, self.b], v)
        self.misfit = float(np.sqrt(np.mean(res ** 2))) if len(pos) > 2 else 0.5

    def _t(self, v):
        return np.log10(v) if self.scale == "log10" else v

    def px(self, value):
        return float(self.a * self._t(np.array(value, float)) + self.b)

    def value(self, p):
        t = (p - self.b) / self.a
        return float(10 ** t if self.scale == "log10" else t)


def _longest_run_cols(dk):
    h, w = dk.shape
    out = np.zeros(w, int)
    for c in range(w):
        rs = _runs(dk[:, c])
        if rs:
            out[c] = max(b - a + 1 for a, b in rs)
    return out


def vertical_axes(dk, min_frac=0.3):
    """Dark vertical lines at least min_frac of the height: [(c0, c1, r0, r1)] left to right."""
    h, w = dk.shape
    lr = _longest_run_cols(dk)
    cols = np.flatnonzero(lr >= min_frac * h)
    out = []
    for g in _groups(list(cols), 2):
        c = g[len(g) // 2]
        rs = max(_runs(dk[:, c]), key=lambda r: r[1] - r[0])
        out.append((g[0], g[-1], rs[0], rs[1]))
    return out


def ticks_on_vaxis(dk, c0, c1, side, r0, r1, probe=(3, 12), min_frac=0.85):
    """Rows of tick stubs of a vertical axis line occupying columns c0..c1."""
    if side < 0:
        band = dk[:, max(0, c0 - probe[1]):c0 - probe[0]]
    else:
        band = dk[:, c1 + probe[0] + 1:c1 + probe[1] + 1]
    rows = np.flatnonzero(band.mean(1) >= min_frac)
    rows = [r for r in rows if r0 - 8 <= r <= r1 + 8]
    return _centres(rows, 2)


def bottom_axis(dk, x_from=None, x_to=None):
    h, w = dk.shape
    lo = h // 3
    x_from = 0 if x_from is None else int(x_from)
    x_to = w if x_to is None else int(x_to)
    cov = dk[lo:, x_from:x_to].sum(1)
    r = int(np.argmax(cov)) + lo
    rows = [i for i in range(max(0, r - 20), min(h, r + 20)) if dk[i, x_from:x_to].sum() > 0.6 * cov.max()]
    rows = _groups(rows, 1)
    rows = [g for g in rows if r in g][0]
    return rows[0], rows[-1]


def xticks(dk, top, bot, probe=(3, 12), c_from=0, c_to=None, breaks=True):
    c_to = dk.shape[1] if c_to is None else c_to
    if not breaks:  # an axis without break marks (dotted grid lines may cross it)
        below = dk[bot + probe[0] + 1:bot + probe[1] + 1, :].mean(0) >= 0.85
        return _centres([c for c in np.flatnonzero(below) if c_from <= c < c_to], 2)
    below = dk[bot + probe[0] + 1:bot + probe[1] + 1, :].mean(0) >= 0.85
    above = dk[max(0, top - probe[1]):top - probe[0], :].mean(0) >= 0.5
    # a narrow mark crossing the axis is a break or segment-end mark, not a tick; a wide dark
    # region above (a marker sitting on the axis) does not disqualify the tick under it
    bw = [b - a + 1 for a, b in _runs(below)]
    tick_w = float(np.median(bw)) if bw else 8.0
    narrow = np.zeros_like(above)
    for a, b in _runs(above):
        if b - a + 1 <= 2.5 * tick_w:
            narrow[a:b + 1] = True
    cols = [c for c in np.flatnonzero(below & ~narrow) if c_from <= c < c_to]
    return _centres(cols, 2)


def calibrate(img, cfg):
    """Axes from the image. cfg: ylabels (left axis, bottom up), y2labels (right axis, optional),
    yscale, xlabels (left to right; numbers or names), xscale, probe (tick probe in px),
    ysegments (list of label lists, bottom segment first) for a broken left axis."""
    dk = dark(img, cfg.get("dark_thr", 110))
    probe = tuple(cfg.get("probe", (3, 12)))
    vax = vertical_axes(dk, cfg.get("vmin_frac", 0.3))
    if not vax:
        raise RuntimeError("no vertical axis found")
    cal = {"dk": dk, "notes": []}
    left = vax[0]
    if cfg.get("ysegments"):
        # broken axis: all vertical runs in the left axis column, each segment its own ticks
        c = (left[0] + left[1]) // 2
        segs = sorted([r for r in _runs(dk[:, c]) if r[1] - r[0] > 0.04 * dk.shape[0]], key=lambda r: -r[0])
        if len(segs) < len(cfg["ysegments"]):
            raise RuntimeError(f"broken axis: found {len(segs)} segments")
        cal["ysegs"] = []
        for (r0, r1), labels in zip(segs, cfg["ysegments"]):
            t = ticks_on_vaxis(dk, left[0], left[1], -1, r0, r1, probe)
            if len(t) != len(labels):
                raise RuntimeError(f"broken axis segment {r0}-{r1}: {len(t)} ticks for {len(labels)} labels: {t}")
            ax = Axis(sorted(t, reverse=True), labels, cfg.get("yscale", "linear"))
            cal["ysegs"].append((r0, r1, ax))
        cal["y"] = cal["ysegs"][0][2]
    else:
        t = ticks_on_vaxis(dk, left[0], left[1], -1, left[2], left[3], tuple(cfg.get("yprobe", probe)))
        if cfg.get("ydrop_bottom"):  # lowest tick(s) obscured (a marker on the axis corner): not used
            t = sorted(t)[:-cfg["ydrop_bottom"]]
        labels = cfg["ylabels"]
        if len(t) != len(labels):
            raise RuntimeError(f"left axis: {len(t)} ticks for {len(labels)} labels: {t}")
        cal["y"] = Axis(sorted(t, reverse=True), labels, cfg.get("yscale", "linear"))
    cal["left"] = left
    if cfg.get("y2labels"):
        right = vax[-1]
        t = ticks_on_vaxis(dk, right[0], right[1], +1, right[2], right[3], probe)
        if len(t) != len(cfg["y2labels"]):
            raise RuntimeError(f"right axis: {len(t)} ticks for {len(cfg['y2labels'])} labels: {t}")
        cal["y2"] = Axis(sorted(t, reverse=True), cfg["y2labels"], cfg.get("y2scale", "linear"))
        cal["right"] = right
    if cfg.get("no_xaxis"):
        # no bottom axis line and no x ticks: the plot ends at the foot of the y axis; groups are
        # found from the data (read_means)
        cal["xaxis"] = (left[3] + 1, left[3] + 1)
        cal["xcol"] = {}
        cal["plot"] = (left[1] + 1, dk.shape[1] - 1, 0, left[3])
        return cal
    top, bot = bottom_axis(dk, left[1] + 2, (vax[-1][0] - 2) if cfg.get("y2labels") else None)
    cal["xaxis"] = (top, bot)
    xt = xticks(dk, top, bot, tuple(cfg.get("xprobe", probe)), left[0] - 4,
                (cal["right"][1] + 4) if "right" in cal else None, cfg.get("x_breaks", True))
    xl = cfg["xlabels"]
    if cfg.get("xtick_skip_first"):
        xt = xt[1:]
    if len(xt) != len(xl):
        raise RuntimeError(f"x axis: {len(xt)} ticks for {len(xl)} labels: {[round(v) for v in xt]}")
    cal["xcol"] = dict(zip([str(v) for v in xl], xt))
    num = [(c, v) for c, v in zip(xt, xl) if isinstance(v, (int, float))]
    if len(num) >= 2:
        cal["x"] = Axis([c for c, _ in num], [v for _, v in num], cfg.get("xscale", "linear"), "x")
    cal["plot"] = (left[1] + 1, (cal["right"][0] - 1) if "right" in cal else dk.shape[1] - 1, 0, top - 1)
    return cal


def yaxis_for(cal, row, which="y"):
    if which == "y" and "ysegs" in cal:
        for r0, r1, ax in cal["ysegs"]:
            if r0 - 10 <= row <= r1 + 10:
                return ax
        return min(cal["ysegs"], key=lambda s: min(abs(row - s[0]), abs(row - s[1])))[2]
    return cal[which]


def cal_note(cal, which="y"):
    ys = [ax.misfit for _, _, ax in cal["ysegs"]] if (which == "y" and "ysegs" in cal) else [cal[which].misfit]
    xs = f"x ticks misfit {cal['x'].misfit:.1f} px, " if "x" in cal else ""
    return xs + "y ticks misfit " + "/".join(f"{m:.1f}" for m in ys) + " px"


# ---------------------------------------------------------------- markers
MIN_VISIBLE = 0.03   # a marker must show at least this fraction of its disk


def _disk(r):
    k = int(np.ceil(r))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    return (xx ** 2 + yy ** 2 <= r * r).astype(float)


def masks(img, cfg):
    """Target: the series colour. Occluder: any ink that is not the target (other series, black,
    and the anti-aliased rims between colours). Background: near-white paper."""
    tgt = colour(img, cfg["color"], cfg.get("tol", 70))
    paper = _f(img).min(2) > cfg.get("paper", 215)
    occ = ~tgt & ~paper
    return tgt, occ


def marker_radius(tgt, median=False):
    """The markers' radius: by default the largest inscribed radius of the target colour (the
    markers are its thickest shapes). With median=True, for figures where overlapping markers
    merge into thicker blobs: the inscribed radius of each connected shape, and the median of
    those at least half the thickest (letters and lines are thinner)."""
    edt = ndi.distance_transform_edt(tgt)
    if not median:
        return float(edt.max()) + 0.5
    lab, n = ndi.label(tgt)
    if n == 0:
        return 3.0
    m = np.asarray(ndi.maximum(edt, lab, index=np.arange(1, n + 1)))
    big = m[m >= 0.5 * m.max()]
    return float(np.median(big)) + 0.5


def _scores(tgt, occ, r):
    from scipy.signal import fftconvolve
    k = _disk(r)
    n = k.sum()
    T = np.rint(fftconvolve(tgt.astype(float), k, mode="same"))
    O = np.rint(fftconvolve(occ.astype(float), k, mode="same"))
    B = n - T - O
    return T, O, B, n


def _is_legend(dk, cx, cy, r, right=None):
    h, w = dk.shape
    w = w if right is None else min(w, int(right) - 4)
    r0, r1 = int(max(0, cy - r)), int(min(h, cy + r))
    c0, c1 = int(min(w, cx + 2 * r)), int(min(w, cx + 9 * r))
    if c1 <= c0:
        return False
    return dk[r0:r1, c0:c1].mean() > 0.03


def _centre_interval(T, O, B, n, cx, cy, h):
    # a fully visible marker: where the disk stays (almost) all target; a partly hidden one:
    # wherever it lies within ink and still covers some target
    tmin = 0.85 * n if T[cy, cx] >= 0.9 * n else MIN_VISIBLE * n
    ok = lambda r: (0 <= r < h) and B[r, cx] <= 0.04 * n and T[r, cx] >= tmin
    lo = hi = cy
    while ok(lo - 1):
        lo -= 1
    while ok(hi + 1):
        hi += 1
    return lo, hi


def _walk(tgt, occ, cx, start, step, wide, limit):
    """Walk along the stem from row start. The target is looked for across +-wide columns (a cap
    may show beside another series' stem); an occluder only on the stem (+-2 columns).
    Returns (last target row, last occluder row after it or None)."""
    h = tgt.shape[0]
    last, last_occ = None, None
    r = start
    gap = 0
    while 0 <= r < h and r != limit:
        t = tgt[r, max(0, cx - wide):cx + wide + 1].any()
        o = occ[r, max(0, cx - 2):cx + 3].any()
        if t:
            last, gap, last_occ = r, 0, None
        elif o:
            last_occ, gap = r, 0
        else:
            gap += 1
            if gap > 2:
                break
        r += step
    return last, last_occ


def _cap_thickness(mask, cx, end, step, stem_w, stop=None):
    """Thickness of the cap at the outer end `end` (rows going back towards the centre, not
    into the marker, which begins at row `stop`)."""
    t = 0
    r = end
    while 0 <= r < mask.shape[0] and (stop is None or (r - stop) * step > 0):
        row = mask[r, max(0, cx - 6 * stem_w):cx + 6 * stem_w + 1]
        if row.sum() > 2.2 * stem_w:
            t += 1
            r -= step
        else:
            break
    return max(t, 1)


def _stem_width(mask, cx, rows, max_w=None):
    """Typical width of the vertical line through cx over rows; runs wider than max_w (an
    axis line, say) are not a stem."""
    ws = []
    for r in rows:
        if 0 <= r < mask.shape[0]:
            for a, b in _runs(mask[r]):
                if a - 2 <= cx <= b + 2 and (max_w is None or b - a + 1 <= max_w):
                    ws.append(b - a + 1)
    return int(np.median(ws)) if ws else 3


def error_bar(mask, occ, cx, cy, r, ax, top_limit=0, wide=None, bottom_limit=None):
    """Ends of the error bar through (cx, cy) in mask; returns dict of bar values and a note."""
    h = mask.shape[0]
    cx = int(round(cx))
    cy = int(round(cy))
    rr = int(np.ceil(r))
    sw = _stem_width(mask, cx, [x for x in range(cy - rr - 15, cy + rr + 16) if abs(x - cy) > rr + 2],
                     max(20, 2 * rr))
    if wide is None:
        wide = min(max(rr, 3 * sw), int(1.3 * rr) + 1)
    bottom = h if bottom_limit is None else int(bottom_limit)
    notes = []
    ends = {}   # name -> (row, kind, extra): kind visible | marker | hidden (extra = hidden span)
    for name, step, limit in (("hi", -1, top_limit - 1), ("lo", +1, bottom)):
        last, last_occ = _walk(mask, occ, cx, cy, step, wide, limit)
        edge = cy + step * r
        beyond = last is not None and (last - cy) * step > rr + 4
        t = _cap_thickness(mask, cx, last, step, sw, cy + step * (rr + 3)) if beyond else 0
        if beyond and (t >= 2 or last_occ is None):
            ends[name] = (last - step * (t - 1) / 2.0, "visible", t)
        elif last_occ is not None and (last_occ - cy) * step > rr + 1 and \
                (last_occ - (last if last is not None else edge)) * step > max(6, 2 * sw):
            start = last if beyond else edge
            ends[name] = (None, "hidden", sorted([start, last_occ]))
        elif beyond:
            ends[name] = (last, "visible", 1)
        else:
            ends[name] = (edge, "marker", None)
    rows = {}
    for name, sgn in (("hi", -1), ("lo", +1)):
        end, kind, extra = ends[name]
        other = ends["lo" if name == "hi" else "hi"]
        side = "upper" if sgn < 0 else "lower"
        if kind == "hidden":
            span = extra
            if other[1] != "hidden":
                mirror = 2 * cy - other[0]
                rows[name] = (mirror, [min(mirror, span[0]), max(mirror, span[1])])
                notes.append(f"{side} bar end hidden behind another mark (rows {int(span[0])}-{int(span[1])}); "
                             f"taken as the mirror of the other end")
            else:
                rows[name] = ((span[0] + span[1]) / 2.0, span)
                notes.append(f"{side} bar end hidden behind another mark (rows {int(span[0])}-{int(span[1])})")
        elif kind == "marker":
            rows[name] = (end, [end - 1, end + 1])
            notes.append(f"{side} bar end within the marker: at most the marker")
        else:
            rows[name] = (end, [end - extra / 2.0 - 1, end + extra / 2.0 + 1])
    out = {}
    m = 2 * ax.misfit
    hi_row, hi_out = rows["hi"]
    lo_row, lo_out = rows["lo"]
    out["bar_hi"] = ax.value(hi_row)
    out["bar_lo"] = ax.value(lo_row)
    out["bar_hi_outer"] = max(ax.value(min(hi_out) - m), ax.value(max(hi_out) + m))
    out["bar_lo_outer"] = min(ax.value(min(lo_out) - m), ax.value(max(lo_out) + m))
    out["px_bar"] = [hi_row, lo_row]
    return out, notes


def _result(x, ax, cx, cy, lo_r, hi_r, note, bar=None):
    m = 2 * ax.misfit + 1.0
    y = ax.value(cy)
    a, b = ax.value(hi_r + m), ax.value(lo_r - m)
    res = {"x": x, "y": y, "lo": min(a, b, y), "hi": max(a, b, y), "px": [float(cx), float(cy)],
           "px_lo": float(lo_r - m), "px_hi": float(hi_r + m), "note": note}
    if bar:
        res.update({k: float(v) for k, v in bar.items() if k != "px_bar"})
    return res


def find_marker(sc, dk, col, r, plot, band=None, legend=True):
    """Best marker centre near column col; returns (cx, cy, lo, hi, partial) or None.
    sc = _scores(...). A candidate disk must cover some target and lie within target or
    occluder (at most 4% background)."""
    T, O, B, n = sc
    S = T + 0.5 * O - 3 * B
    c0, c1, r0, r1 = plot
    band = r if band is None else band
    a0, a1 = int(max(c0, col - band)), int(min(c1, col + band)) + 1
    sub = S[r0:r1 + 1, a0:a1]
    valid = (T[r0:r1 + 1, a0:a1] >= MIN_VISIBLE * n) & (B[r0:r1 + 1, a0:a1] <= 0.04 * n)
    order = np.argsort(np.where(valid, sub, -1e9).ravel())[::-1]
    for idx in order[:20000]:
        rr, cc = np.unravel_index(idx, sub.shape)
        if not valid[rr, cc]:
            return None
        cy, cx = rr + r0, cc + a0
        if legend and _is_legend(dk, cx, cy, r, c1):
            continue
        lo, hi = _centre_interval(T, O, B, n, cx, cy, T.shape[0])
        return cx, cy, lo, hi, T[cy, cx] < 0.9 * n
    return None


def _yax(cal, cfg):
    return cal["y2" if cfg.get("axis") == "right" else "y"]


def read_markers_at(image, at, cfg):
    """One marker per tick: cfg['read'] lists the x labels to read (category names or numbers);
    x of a numeric label is the label, x of a category is cfg['xvalue'][name]."""
    img = np.asarray(image)
    cal = calibrate(img, cfg)
    tgt, occ = masks(img, cfg)
    r = cfg.get("radius") or marker_radius(tgt)
    sc = _scores(tgt, occ, r)
    out = []
    for lab in cfg["read"]:
        col = cal["xcol"][str(lab)]
        xval = cfg.get("xvalue", {}).get(str(lab), lab)
        found = find_marker(sc, cal["dk"], col, r, cal["plot"], cfg.get("band"), cfg.get("legend", True))
        if found is None:
            out.append({"x": float(xval), "y": None, "note": f"no {cfg.get('name', 'marker')} found at {lab}"})
            continue
        cx, cy, lo, hi, partial = found
        ax = yaxis_for(cal, cy, "y2" if cfg.get("axis") == "right" else "y")
        note = f"at {lab}; marker r {r:.1f} px; " + cal_note(cal, "y2" if cfg.get("axis") == "right" else "y")
        if partial:
            note += f"; marker partly hidden, centre anywhere in rows {lo}-{hi}"
        bar = None
        if cfg.get("error_bars"):
            bar, bnotes = error_bar(tgt, occ, cx, cy, r, ax, bottom_limit=cal["xaxis"][0])
            if bnotes:
                note += "; " + "; ".join(bnotes)
        out.append(_result(float(xval), ax, cx, cy, lo, hi, note, bar))
        if bar:
            out[-1]["px_lo"], out[-1]["px_hi"] = bar["px_bar"][0], bar["px_bar"][1]
    return out


def read_markers_free(image, at, cfg):
    """All markers of the colour in the plot, left to right; x from the x calibration (snapped to
    cfg['snap'] when within a quarter of it, as the points sit on a regular grid)."""
    img = np.asarray(image)
    cal = calibrate(img, cfg)
    tgt, occ = masks(img, cfg)
    r = marker_radius(tgt, cfg.get("radius_median", False))
    T, O, B, n = _scores(tgt, occ, r)
    S = T + 0.5 * O - 3 * B
    edt = ndi.distance_transform_edt(tgt | occ)
    c0, c1, r0, r1 = cal["plot"]
    good = (T >= 0.6 * n) & (B <= 0.05 * n)
    good[:, :c0 + int(r)] = False
    good[:, c1 - int(r):] = False
    good[r1 - int(r) + 1:, :] = False
    mx = ndi.maximum_filter(np.where(good, S, -1e9), size=int(3 * r))
    pk = np.argwhere(good & (S == mx))
    pts = []
    for cy, cx in sorted(pk.tolist(), key=lambda p: p[1]):
        if any(abs(cx - p[0]) < 1.5 * r and abs(cy - p[1]) < 1.5 * r for p in pts):
            continue
        if cfg.get("legend", True) and _is_legend(cal["dk"], cx, cy, r, c1):
            continue
        pts.append((cx, cy))
    if cfg.get("snap"):
        # one marker per grid position: the candidate with the largest inscribed radius (a marker
        # centre, not a cap or a crossing of bars)
        s = cfg["snap"]
        best = {}
        for cx, cy in pts:
            k = round(cal["x"].value(cx) / s)
            if k not in best or edt[cy, cx] > edt[best[k][1], best[k][0]]:
                best[k] = (cx, cy)
        pts = [best[k] for k in sorted(best)]
    out = []
    ax = _yax(cal, cfg)
    for cx, cy in pts:
        xv = cal["x"].value(cx)
        note = f"marker r {r:.1f} px; " + cal_note(cal)
        if cfg.get("snap"):
            s = cfg["snap"]
            q = round(xv / s) * s
            if abs(q - xv) < s / 4:
                note += f"; x {xv:.3g} from the calibration, on the {s:g} grid"
                xv = q
        lo, hi = _centre_interval(T, O, B, n, cx, cy, tgt.shape[0])
        bar = None
        if cfg.get("error_bars"):
            bar, bnotes = error_bar(tgt, occ, cx, cy, r, ax, bottom_limit=cal["xaxis"][0])
            if bnotes:
                note += "; " + "; ".join(bnotes)
        out.append(_result(float(xv), ax, cx, cy, lo, hi, note, bar))
        if bar:
            out[-1]["px_lo"], out[-1]["px_hi"] = bar["px_bar"][0], bar["px_bar"][1]
    return out


# ---------------------------------------------------------------- scatter plots with mean +- s.e.m.
def _bridged(dk, ink, max_gap=80):
    """Dark mask with short gaps in each row filled where the gap is all ink (a dot drawn over a
    line), never where it is paper."""
    out = dk.copy()
    for r in range(dk.shape[0]):
        rs = _runs(dk[r])
        for (a0, a1), (b0, b1) in zip(rs, rs[1:]):
            if b0 - a1 - 1 <= max_gap and ink[r, a1 + 1:b0].all():
                out[r, a1 + 1:b0] = True
    return out


def read_means(image, at, cfg):
    img = np.asarray(image)
    cal = calibrate(img, cfg)
    ax = cal["y"]
    ink = _f(img).min(2) < 215
    dk = _bridged(dark(img, cfg.get("line_thr", 70), 60), ink)
    if not cal["xcol"]:
        # groups from the mean lines: the longest horizontal dark runs in the plot, one per group
        c_lo, c_hi, r_top, r_bot = cal["plot"]
        runs = []
        for rr in range(r_top, r_bot - 3):
            for s, e in _runs(dk[rr, c_lo + 6:c_hi]):
                runs.append((e - s + 1, (s + e) / 2.0 + c_lo + 6))
        Lmax = max(L for L, _ in runs)
        cents = sorted(c for L, c in runs if L >= 0.7 * Lmax)
        groups = [float(np.mean(g)) for g in _groups(sorted(cents), int(0.5 * Lmax)) if g]
        groups = [float(np.mean([c for c in cents if abs(c - g) < 0.5 * Lmax])) for g in groups]
        if len(groups) != len(cfg["xlabels"]):
            raise RuntimeError(f"found {len(groups)} mean lines for {len(cfg['xlabels'])} groups")
        cal["xcol"] = {str(lab): g for lab, g in zip(cfg["xlabels"], groups)}
        cfg = dict(cfg, band_frac=cfg.get("band_frac", 0.45))
    cols = [cal["xcol"][str(lab)] for lab in cfg["xlabels"]]
    sp = np.median(np.diff(sorted(cols))) if len(cols) > 1 else 200
    c_lo, c_hi, r_top, r_bot = cal["plot"]
    out = []
    for lab, col in zip(cfg["xlabels"], cols):
        if str(lab) not in [str(v) for v in cfg["read"]]:
            continue
        xval = cfg.get("xvalue", {}).get(str(lab), lab)
        half = int(cfg.get("band_frac", 0.45) * sp)
        a0, a1 = int(col - half), int(col + half)
        cands = []
        for rr in range(r_top + 2, r_bot - 2):
            for s, e in _runs(dk[rr, a0:a1 + 1]):
                if s == 0 or e == a1 - a0:
                    continue  # touches the band edge: a significance bar or the axis
                if not (s + a0 - 4 <= col <= e + a0 + 4):
                    continue
                cands.append((e - s + 1, rr, s + a0, e + a0))
        if not cands:
            out.append({"x": float(xval), "y": None, "note": f"no mean line at {lab}"})
            continue
        # the mean line: among the longest runs (>= 90% of the longest; dots drawn over it are
        # bridged), the thickest band of rows
        Lmax = max(c[0] for c in cands)
        longs = [c for c in cands if c[0] >= 0.9 * Lmax]
        bands = _groups(sorted({c[1] for c in longs}), 1)
        band_rows = max(bands, key=len)
        L, rr, s, e = max((c for c in longs if c[1] in band_rows), key=lambda c: c[0])
        # thickness of the mean line: rows where the run of that length continues
        rows = [q for q in range(rr - 40, rr + 41) if 0 <= q < dk.shape[0] and dk[q, s + 2:e - 1].mean() > 0.9]
        rows = [g for g in _groups(rows, 1) if rr in g][0]
        cy = (rows[0] + rows[-1]) / 2.0
        cx = int(round((s + e) / 2))
        thick = rows[-1] - rows[0] + 1
        # the error-bar stem: the column near the centre with the most dark just above and below
        # the line (a dot bridged onto one end of the line shifts the run's centre)
        q = max(2, L // 4)
        cols_ = np.arange(max(0, cx - q), min(dk.shape[1], cx + q + 1))
        cnt = (dk[max(0, rows[0] - 25):max(0, rows[0] - 3), cols_].sum(0)
               + dk[rows[-1] + 3:rows[-1] + 25, cols_].sum(0))
        if cnt.max() > 10:
            best_cols = cols_[cnt >= 0.8 * cnt.max()]
            cx = int(round(np.median(best_cols)))
        note = f"at {lab}; mean line {L} px long, {thick} px thick; " + cal_note(cal)
        bar, bnotes = error_bar(dk, ink & ~dk, cx, cy, thick / 2.0, ax, wide=3)
        if bnotes:
            note += "; " + "; ".join(n_.replace("marker", "mean line") for n_ in bnotes)
        res = _result(float(xval), ax, cx, cy, rows[0], rows[-1], note, bar)
        res["px_lo"], res["px_hi"] = bar["px_bar"][0], bar["px_bar"][1]
        out.append(res)
    return out


# ---------------------------------------------------------------- histograms
def read_hist(image, at, cfg):
    img = np.asarray(image)
    cal = calibrate(img, cfg)
    ax = cal["y"]
    fill = colour(img, cfg["color"], cfg.get("tol", 70))
    dk = dark(img, 120, 80)
    ink = fill | dk
    top_ax = cal["xaxis"][0]
    out = []
    for lab in cfg["xlabels"]:
        col = int(round(cal["xcol"][str(lab)]))
        c = ink[:top_ax, col - 1:col + 2].any(1)
        # rows from the axis upward while ink continues
        r = top_ax - 1
        while r > 0 and c[r]:
            r -= 1
        top_edge = r + 1
        # the outline at the top: dark rows from top_edge down
        t = 0
        while top_edge + t < top_ax and dk[top_edge + t, col - 1:col + 2].any() and not fill[top_edge + t, col]:
            t += 1
        filled_below = fill[top_edge + t:top_ax, col].mean() if top_ax > top_edge + t else 0
        if top_ax - top_edge <= 2:
            cy, t = (cal["xaxis"][0] + cal["xaxis"][1]) / 2.0, 1   # the axis line's centre: zero
            note = "no bar above the axis"
        else:
            cy = top_edge + (t - 1) / 2.0
            note = f"top outline {t} px; fill below {filled_below:.2f}"
        m = 2 * ax.misfit + 1 + t / 2.0
        y = ax.value(cy)
        out.append({"x": float(lab), "y": y, "lo": min(y, ax.value(cy + m)), "hi": max(y, ax.value(cy - m)),
                    "px": [float(col), float(cy)], "px_lo": float(cy - m), "px_hi": float(cy + m),
                    "note": f"bin {lab}; {note}; " + cal_note(cal)})
    return out


# ---------------------------------------------------------------- loading by the reading files
def load_and_read(path_of_reader, sha, image, at, cfg, fn):
    import hashlib
    from pathlib import Path
    kit = Path(path_of_reader).with_name("_kit.py")
    if hashlib.sha256(kit.read_bytes()).hexdigest() != sha:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    return globals()[fn](image, at, cfg)
