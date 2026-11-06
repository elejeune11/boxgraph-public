"""Shared reading code for the force/rigidity and flow/rigidity panels of Elosegui-Artola et al. 2016
(Fig. 3d,e on PDF p. 4; Fig. 6a-i on PDF p. 7). Everything is found in the image; the only numbers typed in
are the printed tick labels each reader passes (x: 0.1, 1, 10, 100 kPa on a log axis; y: the labels of
the left axis, bottom up).

Method:
- axes: the left axis is the column with the longest run of dark (black, unsaturated) pixels, the bottom
  axis the row with the longest dark run;
- ticks: on the y axis, short dark horizontal marks just left of the axis; on the x axis, short dark
  vertical marks just below it. They are matched to the printed labels in order (bottom up, left to
  right) and fitted by a straight line (x in log10); the misfit (rms, px) is reported and goes into
  every interval;
- curves (`read_curve`): pixels of the line's colour (a hue window, saturated) inside the plot box. A
  column is split in runs; runs thicker than `max_run` px (markers, error-bar caps and stems seen end-on,
  steep parts) are kept only where the line is steep. The line is traced from a seed column (where the
  caller says the wanted branch lies: top or bottom of the colour's runs) to both sides, each column taking
  the run nearest the previous centre; columns where it is hidden (behind a marker, an error bar or a line
  drawn on top) are bridged by linear interpolation between the traced columns on each side, and the note
  says so. Value: centre of the run averaged over +-3 columns. 95% interval: half the run height (line
  thickness, larger where steep) + 2 px + 2 x the y misfit; for an interpolated position also half the
  jump across the gap;
- points (`read_points`): markers are compact blobs of the colour (filled discs, or rings for open
  markers), several line widths across; each is read at its centre. Its error bar is the thin vertical
  line of the same colour through that centre, with short horizontal caps; its ends are where that
  line stops. Intervals: +-(1 px + misfit) on the centre, bar ends widened by 2 px + 2 x misfit.
"""
import numpy as np


# ---------------------------------------------------------------- masks
def hsv(img):
    rgb = img[..., :3].astype(float) / 255.0
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    d = mx - mn + 1e-9
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0)
    return h, s, mx


def dark_mask(img):
    rgb = img[..., :3].astype(float)
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    return (mx < 110) & (mx - mn < 40)


def color_mask(img, hue, width=25, smin=0.35, vmin=0.25):
    h, s, v = hsv(img)
    dh = np.abs((h - hue + 180) % 360 - 180)
    return (dh < width) & (s > smin) & (v > vmin)


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


# ---------------------------------------------------------------- calibration
def calibrate(img, ylabels, xlabels=(0.1, 1.0, 10.0, 100.0), axis_extra=None):
    """Axes, ticks and the two linear maps. `axis_extra`: pixels of another colour the axis lines are
    drawn in (Fig. 6b, whose axes are the blue frame of the reference panel); the ticks stay black."""
    dk = dark_mask(img)
    ax_m = dk if axis_extra is None else (dk | axis_extra)
    h, w = dk.shape
    longest = {}
    for c in range(w):
        for a, b in runs(ax_m[:, c]):
            if b - a > longest.get(c, (0,))[0]:
                longest[c] = (b - a, a, b)
    top_len = max(v[0] for v in longest.values())
    # the y axis: the leftmost column whose dark run is nearly the longest (a frame's far side is not it)
    xa = min(c for c, v in longest.items() if v[0] >= 0.8 * top_len)
    _, ya0, ya1 = longest[xa]
    cols = [c for c in range(max(0, xa - 12), min(w, xa + 12)) if ax_m[ya0:ya1, c].mean() > 0.9]
    x_axis_l, x_axis_r = min(cols), max(cols)
    best = (0, None)
    for r in range(h // 2, h):
        for a, b in runs(ax_m[r]):
            if b - a > best[0]:
                best = (b - a, (r, a, b))
    _, (yb, xb0, xb1) = best
    # the axis may be cut by a line of another colour drawn across it (Fig. 6e, h): bridge gaps <= 30 px
    for a, b in runs(ax_m[yb]):
        if a > xb1 and a - xb1 <= 30:
            xb1 = b
    rows =[r for r in range(max(0, yb - 12), min(h, yb + 12)) if ax_m[r, xb0:xb1].mean() > 0.9]
    y_axis_t, y_axis_b = min(rows), max(rows)
    # y ticks: dark pixels in a band just left of the axis
    band = dk[:, max(0, x_axis_l - 30):x_axis_l - 2]
    trows = np.flatnonzero(band.mean(axis=1) > 0.5)
    ty = [float(np.mean(g)) for g in groups(trows) if len(g) < 25]
    ty = [t for t in ty if ya0 - 5 <= t <= y_axis_b + 5]
    if len(ty) != len(ylabels):
        raise RuntimeError(f"expected {len(ylabels)} y ticks, found {len(ty)} at {ty}")
    ty = sorted(ty, reverse=True)
    ay, by = np.polyfit(ylabels, ty, 1)
    ymis = float(np.sqrt(np.mean((np.polyval([ay, by], ylabels) - np.array(ty)) ** 2)))
    # x ticks: dark pixels in a band just below the axis
    band = dk[y_axis_b + 2:y_axis_b + 30, :]
    tcols = np.flatnonzero(band.mean(axis=0) > 0.5)
    tx = [float(np.mean(g)) for g in groups(tcols) if len(g) < 25]
    tx = [t for t in tx if x_axis_l - 5 <= t <= xb1 + 5]
    if len(tx) != len(xlabels):
        raise RuntimeError(f"expected {len(xlabels)} x ticks, found {len(tx)} at {tx}")
    lx = np.log10(xlabels)
    ax, bx = np.polyfit(lx, tx, 1)
    xmis = float(np.sqrt(np.mean((np.polyval([ax, bx], lx) - np.array(tx)) ** 2)))
    # plot box: from the axes to just beyond the last x tick and the top y tick (a frame drawn around a
    # panel, as in Fig. 6b, can run further)
    right = int(min(xb1, max(tx) + 15))
    top = int(max(ya0, min(ty) - 15))
    return dict(ax=ax, bx=bx, ay=ay, by=by, xmis=xmis, ymis=ymis, left=x_axis_r + 1, right=right,
                top=top, bottom=y_axis_t - 1, xticks=tx, yticks=ty)


def col_of(cal, x):
    return cal["ax"] * np.log10(x) + cal["bx"]


def x_of(cal, col):
    return 10 ** ((col - cal["bx"]) / cal["ax"])


def y_of(cal, row):
    return (row - cal["by"]) / cal["ay"]


# ---------------------------------------------------------------- curves
def trace(mask, cal, seed_x, branch="top", max_run=40, max_jump=25, col_range=None):
    """Trace one line of `mask`. Returns {column: (top, bottom)}."""
    top, bot = cal["top"] + 2, cal["bottom"] - 2
    c0, c1 = (cal["left"] + 3, cal["right"] - 3) if col_range is None else col_range

    def col_runs(c):
        return [(a + top, b + top) for a, b in runs(mask[top:bot, c])]

    # seed: the column nearest seed_x with a thin run; there, the topmost (or bottommost) thin run
    s0 = int(round(col_of(cal, seed_x)))
    seed, first = None, None
    for dc in range(0, 40):
        for cc in (s0 - dc, s0 + dc):
            rs = [r for r in col_runs(cc) if r[1] - r[0] <= max_run]
            if rs:
                seed = cc
                first = min(rs, key=lambda r: r[0]) if branch == "top" else max(rs, key=lambda r: r[1])
                break
        if seed is not None:
            break
    if seed is None:
        return {}
    path = {seed: first}
    for step in (1, -1):
        prev = (first[0] + first[1]) / 2
        slope = 0.0
        miss = 0
        c = seed + step
        while c0 <= c <= c1:
            rs = col_runs(c)
            expect = prev + slope * (miss + 1)
            # a steep line crosses a column in a taller run: allow max_run (1 + |slope|), no more, so an
            # error bar (a tall thin run) is not taken for the line
            cand = [r for r in rs if r[1] - r[0] <= max_run * (1 + min(abs(slope), 4.0))
                    and (r[0] - max_jump - 1.5 * miss <= expect <= r[1] + max_jump + 1.5 * miss)]
            if cand:
                r = min(cand, key=lambda r: abs((r[0] + r[1]) / 2 - expect))
                cen = (r[0] + r[1]) / 2
                slope = 0.7 * slope + 0.3 * (cen - prev) / (miss + 1)
                path[c] = r
                prev = cen
                miss = 0
            else:
                miss += 1
                if miss > 120:
                    break
            c += step
    return path


def read_curve(img, cal, path, at, extra_note=""):
    xs = np.array(sorted(path))
    out = []
    note0 = f"x ticks misfit {cal['xmis']:.1f} px, y ticks misfit {cal['ymis']:.1f} px"
    if extra_note:
        note0 += "; " + extra_note
    for x in at:
        col = col_of(cal, x)
        if not len(xs) or col < xs.min() - 2 or col > xs.max() + 2:
            out.append({"x": float(x), "y": None, "note": "outside the drawn line"})
            continue
        near = [c for c in range(int(round(col)) - 3, int(round(col)) + 4) if c in path]
        note = note0
        if len(near) >= 3:
            cen = float(np.mean([(path[c][0] + path[c][1]) / 2 for c in near]))
            half = float(np.mean([(path[c][1] - path[c][0]) / 2 for c in near]))
        else:
            left, right = xs[xs < col], xs[xs > col]
            if not len(left) or not len(right):
                out.append({"x": float(x), "y": None, "note": "line not found here"})
                continue
            cl_, cr_ = left.max(), right.min()
            yl = (path[cl_][0] + path[cl_][1]) / 2
            yr = (path[cr_][0] + path[cr_][1]) / 2
            cen = yl + (yr - yl) * (col - cl_) / (cr_ - cl_)
            half = max(path[cl_][1] - path[cl_][0], path[cr_][1] - path[cr_][0]) / 2 + abs(yr - yl) / 2
            note += f"; line hidden over columns {cl_ + 1}-{cr_ - 1}, interpolated"
        y = y_of(cal, cen)
        dy = (half + 2 + 2 * cal["ymis"]) / abs(cal["ay"])
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [float(col), float(cen)], "px_lo": float(cen - half), "px_hi": float(cen + half),
                    "note": note})
    return out


def dashes(mask, cal, exclude=None, dt_range=(7.5, 14.0), len_range=(50, 330), avoid=None):
    """The dashes of a dashed line: connected components of the mask (inside the plot box, outside
    `exclude`) as thick as the line (maximum of the distance transform in dt_range), elongated (length along
    the principal axis in len_range px) and not vertical (wider than 1.5 x their thickness, which leaves out
    the vertical threshold line and error bars). Returns {column: (top, bottom)} of the dash pixels."""
    from scipy import ndimage
    m = mask.copy()
    m[:cal["top"], :] = False
    m[cal["bottom"] - 2:, :] = False
    m[:, :cal["left"] + 3] = False
    m[:, cal["right"] - 2:] = False
    if exclude is not None:
        m &= ~exclude
    dt = ndimage.distance_transform_edt(m)
    lab, n = ndimage.label(m)
    path = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        sub = lab[sl] == i
        dmax = float(dt[sl][sub].max())
        if not (dt_range[0] <= dmax <= dt_range[1]):
            continue
        rr, cc = np.nonzero(sub)
        if len(rr) < 50:
            continue
        if ndimage.binary_fill_holes(sub).sum() > 1.15 * sub.sum():
            continue   # encloses a hole: an open circle (with its bar), not a dash
        cov = np.cov(np.vstack([cc, rr]))
        length = 4 * np.sqrt(max(np.linalg.eigvalsh(cov)))
        width_cols = cc.max() - cc.min() + 1
        if not (len_range[0] <= length <= len_range[1]) or width_cols < 3 * dmax:
            continue
        if avoid:
            # a piece of another (solid) line cut short by markers, not a dash
            ucols = np.unique(cc)
            on = sum(1 for c in ucols if int(c + sl[1].start) in avoid
                     and avoid[int(c + sl[1].start)][0] - 5 <= rr[cc == c].mean() + sl[0].start
                     <= avoid[int(c + sl[1].start)][1] + 5)
            if on >= 0.5 * len(ucols):
                continue
        comp = {}
        for c in np.unique(cc):
            rows = rr[cc == c]
            comp[int(c + sl[1].start)] = (int(rows.min() + sl[0].start), int(rows.max() + sl[0].start))
        path.append(comp)
    return chain(path)


def chain(comps, max_gap=400, max_rise=300):
    """Keep the dashes that form one dashed line: start from the rightmost dash and walk left, each next
    dash ending at most max_gap columns before the current one starts and within max_rise rows of it
    (a stray dash-like shape elsewhere, such as a piece of a bar cap, is dropped). Returns
    {column: (top, bottom)}."""
    if not comps:
        return {}

    def ends(p):
        cs = sorted(p)
        lc, rc = cs[0], cs[-1]
        return lc, rc, sum(p[lc]) / 2, sum(p[rc]) / 2

    comps = sorted(comps, key=lambda p: max(p))
    cur = comps.pop()
    out = dict(cur)
    while True:
        lc, _, ly, _ = ends(cur)
        best = None
        for p in comps:
            plc, prc, ply, pry = ends(p)
            if prc < lc and lc - prc <= max_gap and abs(pry - ly) <= max_rise:
                if best is None or prc > ends(best)[1]:
                    best = p
        if best is None:
            break
        comps.remove(best)
        out.update(best)
        cur = best
    return out


# ---------------------------------------------------------------- points with error bars
def find_discs(mask, cal, R, hollow=False, cover=None):
    """Centres of markers of radius about R px. Filled discs: maxima of the distance transform of the
    mask between 0.75 R and 1.25 R (lines and bars are much thinner, so they never reach it). Open
    markers (rings): the same on the mask with its holes filled, keeping only components whose centre is
    not of the colour (a ring, not a disc). With `cover` (pixels of other colours drawn on top), the
    distance transform is taken on mask | cover, so a disc crossed by another colour's line or bar is still
    found, and a disc is kept only if at least half of its central area (0.8 R) is of the colour."""
    from scipy import ndimage
    m = mask.copy() if cover is None else (mask | cover)
    m[:cal["top"], :] = False
    m[cal["bottom"] + 1:, :] = False
    m[:, :cal["left"]] = False
    m[:, cal["right"] + 1:] = False
    if hollow:
        m = ndimage.binary_fill_holes(m)
    dt = ndimage.distance_transform_edt(m)
    lab, n = ndimage.label(dt > 0.75 * R)
    pts = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        sub = np.where(lab[sl] == i, dt[sl], 0)
        if sub.max() > 1.25 * R:
            continue
        # centre: centroid of the core above 90% of its maximum
        rr, cc = np.nonzero(sub > 0.9 * sub.max())
        r0, c0 = float(rr.mean() + sl[0].start), float(cc.mean() + sl[1].start)
        yy, xx = np.ogrid[:mask.shape[0], :mask.shape[1]]
        core = (yy - r0) ** 2 + (xx - c0) ** 2 <= (0.5 * R) ** 2
        if hollow and mask[core].mean() > 0.6:
            continue   # a filled marker, not a ring (a ring's centre is white but for a bar through it)
        if not hollow and cover is None and mask[core].mean() < 0.8:
            continue
        if cover is not None and not hollow:
            inner = (yy - r0) ** 2 + (xx - c0) ** 2 <= (0.8 * R) ** 2
            if mask[inner].mean() < 0.5:
                continue
        pts.append((c0, r0))
    return sorted(pts)


def find_rings(mask, cal, R, min_score=0.8, step=2):
    """Centres of open circles of radius about R px. Candidates are points inside the colour's filled
    regions (distance transform of the mask with holes filled > 0.6 R) whose centre disc (0.5 R) is mostly
    white; each is scored by the fraction of 72 directions in which the colour is met between 0.8 R and
    1.15 R from it (a ring scores near 1; a gap between a line and a bar scores much less), and rejected
    unless in at least 65% of the directions that colour ends again before 1.25-1.4 R (a ring is a thin band
    standing on white; a hole enclosed by thick shapes is not). The best
    candidates at least 1.2 R apart with a score >= min_score are kept, each centre refined as the mean of
    the candidates within 3 px scoring as high."""
    from scipy import ndimage
    m = mask.copy()
    m[:cal["top"], :] = False
    m[cal["bottom"] + 1:, :] = False
    m[:, :cal["left"]] = False
    m[:, cal["right"] + 1:] = False
    filled = ndimage.binary_fill_holes(m)
    dt = ndimage.distance_transform_edt(filled)
    blank = ndimage.uniform_filter((~m).astype(float), size=int(R)) > 0.6
    cand = (dt > 0.6 * R) & blank
    rr, cc = np.nonzero(cand[::step, ::step])
    rr, cc = rr * step, cc * step
    if not len(rr):
        return []
    ang = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    rad = np.arange(0.8 * R, 1.15 * R + 1)
    dy = np.rint(np.outer(np.sin(ang), rad)).astype(int)
    dx = np.rint(np.outer(np.cos(ang), rad)).astype(int)
    rad_out = np.arange(1.25 * R, 1.4 * R + 1)
    oy = np.rint(np.outer(np.sin(ang), rad_out)).astype(int)
    ox = np.rint(np.outer(np.cos(ang), rad_out)).astype(int)
    h, w = m.shape
    score = np.zeros(len(rr))
    outer = np.zeros(len(rr))
    for i in range(72):
        yy = np.clip(rr[:, None] + dy[i][None, :], 0, h - 1)
        xx = np.clip(cc[:, None] + dx[i][None, :], 0, w - 1)
        hit = m[yy, xx].any(axis=1)
        score += hit
        yy = np.clip(rr[:, None] + oy[i][None, :], 0, h - 1)
        xx = np.clip(cc[:, None] + ox[i][None, :], 0, w - 1)
        outer += hit & ~m[yy, xx].all(axis=1)   # the band ends: white somewhere just outside it
    score /= 72
    outer /= 72
    score = np.where(outer >= 0.65, score, 0.0)
    order = np.argsort(-score)
    kept = []
    for j in order:
        if score[j] < min_score:
            break
        if all((rr[j] - r) ** 2 + (cc[j] - c) ** 2 > (1.2 * R) ** 2 for c, r, _ in kept):
            near = (np.abs(rr - rr[j]) <= 3) & (np.abs(cc - cc[j]) <= 3) & (score >= score[j] - 1e-9)
            kept.append((float(cc[near].mean()), float(rr[near].mean()), float(score[j])))
    return sorted((c, r) for c, r, _ in kept)


def _bar_end(mask, c0, r0, R, direction, top, bottom, max_gap=30, cover=None):
    """Outermost cap of the error bar through (c0, r0), going up (direction -1) or down (+1): the stem is
    followed while the colour is present within +-4 px of the centre column (gaps of up to max_gap rows
    bridged, so a line of another colour drawn across the bar does not end it);
    a cap is a thin (<= 14 rows) band of rows where the colour spans at least 1.2 R across the stem.
    Returns the cap's middle row, or None (no cap outside the marker)."""
    cc = int(round(c0))
    r = int(round(r0 + direction * R * 0.9))
    gap = 0
    caps = []
    wide_run = []
    stem = mask if cover is None else (mask | cover)   # the stem may lie under another colour's bar
    while top <= r <= bottom:
        on = stem[r, cc - 4:cc + 5].any()
        if on:
            gap = 0
            # horizontal extent of the colour around the stem in this row
            row = mask[r]
            a = cc
            while a - 1 >= 0 and row[a - 1:a + 1].any():
                a -= 1
            b = cc
            while b + 1 < row.size and row[b:b + 2].any():
                b += 1
            if b - a >= 1.2 * R:
                wide_run.append(r)
            else:
                if wide_run:
                    if len(wide_run) <= 14:
                        caps.append(float(np.mean(wide_run)))
                    wide_run = []
        else:
            gap += 1
            if wide_run:
                if len(wide_run) <= 14:
                    caps.append(float(np.mean(wide_run)))
                wide_run = []
            if gap > max_gap:
                break
        r += direction
    if wide_run and len(wide_run) <= 14:
        caps.append(float(np.mean(wide_run)))
    return caps[-1] if caps else None


def read_points(img, cal, mask, R, hollow=False, note_extra="", cover=None):
    """Markers of radius about R px in `mask`, each with its error bar (see the module docstring)."""
    out = []
    centres = find_rings(mask, cal, R) if hollow else find_discs(mask, cal, R, cover=cover)
    for c0, r0 in centres:
        x = x_of(cal, c0)
        y = y_of(cal, r0)
        dy = ((3 if hollow else 1) + 2 * cal["ymis"]) / abs(cal["ay"])   # a ring's centre: +-3 px
        rec = {"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy), "px": [c0, r0],
               "note": f"marker centre; x ticks misfit {cal['xmis']:.1f} px, y ticks misfit {cal['ymis']:.1f} px"
                       + (f"; {note_extra}" if note_extra else "")}
        t = _bar_end(mask, c0, r0, R, -1, cal["top"], cal["bottom"], cover=cover)
        b = _bar_end(mask, c0, r0, R, +1, cal["top"], cal["bottom"], cover=cover)
        widen = (2 + 2 * cal["ymis"]) / abs(cal["ay"])
        if t is None and b is None:
            hb = R / abs(cal["ay"])
            rec.update({"bar_hi": float(y + hb), "bar_lo": float(y - hb),
                        "bar_hi_outer": float(y + hb + widen), "bar_lo_outer": float(y - hb - widen)})
            rec["note"] += "; error bar hidden inside the marker, reported as at most the marker"
            out.append(rec)
            continue
        if t is None:
            t = r0 - (b - r0)
            rec["note"] += "; upper bar end not found outside the marker, taken as the mirror of the lower"
        if b is None:
            b = r0 + (r0 - t)
            rec["note"] += "; lower bar end not found outside the marker, taken as the mirror of the upper"
        bh, bl = y_of(cal, t), y_of(cal, b)
        rec.update({"bar_hi": float(bh), "bar_lo": float(bl), "bar_hi_outer": float(bh + widen),
                    "bar_lo_outer": float(bl - widen), "px_lo": float(t), "px_hi": float(b)})
        out.append(rec)
    return out
