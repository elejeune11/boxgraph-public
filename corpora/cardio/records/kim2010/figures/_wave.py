"""Shared reading code for the waveform panels of Figs. 2, 3 and 5 (black solid, dashed and
dotted curves on a white Excel-style chart with grey axis lines).

Calibration, from the rendered crop only:
  * y: the grey horizontal lines across the plot (the top gridline, the x axis, and in flow
    panels a bottom gridline), each matched to the printed label beside it (`hlines`, top to
    bottom); with three lines the fit has a misfit to check;
  * x: the grey vertical y axis (x = 0) and the short grey tick at the right end of the x axis
    (x = `xmax`), checked against the right end of the gridlines.
Curves: black pixels. A curve is followed column by column from a seed point (given in data
units, only to say which curve is meant), predicting each next row from the local slope; a
solid curve has ink in every column, a dashed or dotted one has gaps, bridged by interpolation
between the ink on either side. The pixels of the solid curve are removed before a dashed or
dotted curve is followed, except where the two overlap.
Each value's 95% interval covers the ink the centre line can lie in (a run of ink less the line
thickness), 2 px of placement, the calibration misfit, and, across a gap or an overlap, the ink
on either side.
"""
import numpy as np


def _runs(idx):
    out = []
    if len(idx) == 0:
        return out
    s = p = int(idx[0])
    for i in idx[1:]:
        i = int(i)
        if i != p + 1:
            out.append((s, p))
            s = i
        p = i
    out.append((s, p))
    return out


def _masks(image):
    rgb = image[..., :3].astype(float)
    g = rgb.mean(axis=2)
    spread = rgb.max(axis=2) - rgb.min(axis=2)
    grey = (g > 110) & (g < 215) & (spread < 30)
    dark = g < 100
    return grey, dark


def calibrate(image, hlines, xmax, axis="grey"):
    """axis: 'grey' when the axis lines and gridlines are grey (Figs. 2, 5), 'black' when they
    are drawn in black like the curves (Fig. 3)."""
    grey, dark = _masks(image)
    if axis == "black":
        grey = dark
    h, w = grey.shape
    # y axis: the longest vertical grey line
    colsum = grey.sum(axis=0)
    c_axis_runs = _runs(np.where(colsum > 0.5 * colsum.max())[0])
    a, b = max(c_axis_runs, key=lambda r: colsum[r[0]:r[1] + 1].sum())
    c0 = (a + b) / 2.0
    col_axis = int(round(c0))
    rows_axis = np.where(grey[:, max(a - 1, 0):b + 2].any(axis=1))[0]
    # horizontal grey lines to the right of the axis
    right = grey[:, col_axis + 10:]
    frac = right.sum(axis=1) / right.shape[1]
    lines = [((r0 + r1) / 2.0, r0, r1) for r0, r1 in _runs(np.where(frac > (0.6 if axis == "black" else 0.35))[0])
             if r1 - r0 < 40]
    # an axis line or gridline starts at the y axis (grey curves, such as the right ventricle's
    # pressure-volume loops, do not)
    lines = sorted(ln for ln in lines if grey[int(ln[1]):int(ln[2]) + 1, col_axis + 12:col_axis + 20].any())
    if len(lines) != len(hlines):
        raise ValueError(f"found {len(lines)} horizontal grey lines, expected {len(hlines)}")
    py = np.array([r for r, _, _ in lines])
    vy = np.array(hlines, float)
    by, ay = np.polyfit(py, vy, 1)
    res_y = float(np.max(np.abs(py - (vy - ay) / by)))
    # x axis line: the line carrying the tick at x = xmax; ticks hang below it
    thick = max(r1 - r0 + 1 for _, r0, r1 in lines)
    ends, ticks = [], []
    for rc, r0, r1 in lines:
        cols = np.where(grey[int(rc), :])[0]
        ends.append(cols.max() - thick / 2.0)
        # a tick hangs from the line: ink in every row of a short band just below it
        below = grey[r1 + 2:r1 + 2 + 2 * thick, col_axis + 20:]
        tc = [(p + q) / 2.0 + col_axis + 20 for p, q in _runs(np.where(below.sum(axis=0) >= 2 * thick - 1)[0])
              if q - p < 3 * thick]
        ticks += tc
    c1_end = float(np.median(ends))
    c1 = max(ticks) if ticks else c1_end
    bx = xmax / (c1 - c0)
    ax = -bx * c0
    res_x = abs(c1 - c1_end)
    return {"ax": ax, "bx": bx, "ay": ay, "by": by, "res_x": res_x, "res_y": res_y, "c0": c0, "c1": c1,
            "top": float(lines[0][0]), "bottom": float(max(lines[-1][0], rows_axis.max())), "line_px": thick,
            "line_rows": [(r0, r1) for _, r0, r1 in lines]}


def _column_runs(dark, top, bottom, c):
    col = dark[top:bottom, c]
    return [(r0 + top, r1 + top) for r0, r1 in _runs(np.where(col)[0])]


def _dist(run, row):
    r0, r1 = run
    return 0.0 if r0 <= row <= r1 else min(abs(row - r0), abs(row - r1))


def track(dark, top, bottom, c_start, c_end, seed_col, seed_row, max_gap, th):
    """Follow a curve from the seed both ways. Returns {col: (r0, r1)} of the run of ink
    taken as the curve in each column where ink was found."""
    found = {}
    # the seed may fall in a gap of a dashed line: take the nearest column with ink near it
    for dc in sorted(range(-60, 61), key=abs):
        runs = [r for r in _column_runs(dark, top, bottom, seed_col + dc) if _dist(r, seed_row) <= 6 * th]
        if runs:
            seed_col += dc
            break
    if not runs:
        raise ValueError(f"no ink near the seed column {seed_col}")
    first = min(runs, key=lambda r: _dist(r, seed_row))
    if _dist(first, seed_row) > 6 * th:
        raise ValueError(f"no ink near the seed ({seed_col}, {seed_row})")
    found[seed_col] = first
    for step, stop in ((1, c_end), (-1, c_start)):
        hist = [(seed_col, (first[0] + first[1]) / 2.0)]
        last_run = first
        c = seed_col
        gap = 0
        while (c + step - stop) * step <= 0:
            c += step
            pc, pr = hist[-1]
            # slope from the recent track (rows per column)
            k = [hc for hc in hist[-12:]]
            slope = 0.0
            if len(k) >= 3 and abs(k[-1][0] - k[0][0]) > 0:
                slope = (k[-1][1] - k[0][1]) / (k[-1][0] - k[0][0])
            pred = pr + slope * (c - pc)
            runs = _column_runs(dark, top, bottom, c)
            best, bd = None, None
            for r in runs:
                # a run continuing the last one (touching it in rows) is the curve going on
                if gap == 0 and r[0] <= last_run[1] + 1 and r[1] >= last_run[0] - 1:
                    d = _dist(r, pred) * 0.5
                else:
                    d = _dist(r, pred)
                if bd is None or d < bd:
                    best, bd = r, d
            tol = 2.0 * th + 1.5 * abs(slope) * (1 + gap) + 0.5 * gap
            if best is not None and bd <= tol:
                found[c] = best
                last_run = best
                # the track goes on at the predicted row, kept within the run: a long run (a steep
                # stretch, or another curve crossing) does not pull the track to its middle
                lo_r, hi_r = best[0] + th / 2.0, best[1] - th / 2.0
                if lo_r > hi_r:
                    lo_r = hi_r = (best[0] + best[1]) / 2.0
                hist.append((c, min(max(pred, lo_r), hi_r)))
                gap = 0
            else:
                gap += 1
                if gap > max_gap:
                    break
    return found


def chain(mask, top, bottom, seed_col, seed_row, reach, kind="dashed"):
    """Follow a dashed or dotted curve as a chain of separate strokes: from the stroke nearest the
    seed, step to the stroke whose back end is nearest the current stroke's front end (within
    `reach` px and not behind it in x), both ways. Returns {col: (r0, r1)}: the extent of the
    chained ink in each column that has some."""
    from scipy import ndimage as ndi

    sub = mask[top:bottom]
    lab, n = ndi.label(sub, structure=np.ones((3, 3)))
    if n == 0:
        raise ValueError("no strokes")
    objs = ndi.find_objects(lab)
    ends = {}
    for i, sl in enumerate(objs, start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        rr = rr + sl[0].start + top
        cc = cc + sl[1].start
        if len(rr) < 6:
            continue
        pts = np.stack([cc, rr], axis=1).astype(float)
        m = pts.mean(axis=0)
        if len(pts) > 2:
            u = np.linalg.svd(pts - m, full_matrices=False)[2][0]
        else:
            u = np.array([1.0, 0.0])
        if u[0] < 0:
            u = -u
        proj = (pts - m) @ u
        back, front = pts[np.argmin(proj)], pts[np.argmax(proj)]
        ends[i] = (back, front, float(cc.mean()), float(cc.mean()))
    # the stroke nearest the seed
    best, bd = None, None
    for i, (b, f, c0, c1) in ends.items():
        rr, cc = np.nonzero(lab[objs[i - 1]] == i)
        d = np.min(np.hypot(cc + objs[i - 1][1].start - seed_col, rr + objs[i - 1][0].start + top - seed_row))
        if bd is None or d < bd:
            best, bd = i, d
    if bd is None or bd > reach:
        raise ValueError(f"no stroke near the seed ({seed_col}, {seed_row})")
    taken = [best]
    # strokes much smaller (for dashes) or much larger (for dots) than the seed's stroke belong to
    # another curve: a dashed curve does not step onto dots, nor a dotted one onto dashes
    sizes = {i: int(np.sum(lab[objs[i - 1]] == i)) for i in ends}
    ref = sizes[best]
    for direction in (1, -1):
        cur = best
        while True:
            b, f, c0, c1 = ends[cur]
            here = f if direction == 1 else b
            cand, cd = None, None
            for j, (bj, fj, cj0, cj1) in ends.items():
                if j in taken:
                    continue
                if kind == "dashed" and sizes[j] < 0.3 * ref:
                    continue
                if kind == "dotted" and sizes[j] > 3.0 * ref:
                    continue
                there = bj if direction == 1 else fj
                # the next stroke lies further along in x (by its mean column: strokes on a steep
                # stretch overlap in columns)
                if direction == 1 and cj0 <= c1:
                    continue
                if direction == -1 and cj1 >= c0:
                    continue
                d = float(np.hypot(*(there - here)))
                if d <= reach and (cd is None or d < cd):
                    cand, cd = j, d
            if cand is None:
                break
            taken.append(cand)
            cur = cand
    keep = np.isin(lab, taken)
    found = {}
    for c in np.where(keep.any(axis=0))[0]:
        rows = np.where(keep[:, c])[0]
        found[int(c)] = (int(rows.min()) + top, int(rows.max()) + top)
    full = np.zeros_like(mask)
    full[top:bottom] = keep
    return found, full


def value_at(found, c, th, merged_len):
    """Centre row and the rows the centre line may lie in, at column c (int)."""
    if c in found:
        r0, r1 = found[c]
        mid = (r0 + r1) / 2.0
        half = max(0.0, (r1 - r0 + 1 - th) / 2.0)

        def alone(k):
            near = [found[j][1] - found[j][0] + 1 for j in range(k - 25, k + 26) if j in found]
            return found[k][1] - found[k][0] + 1 <= np.median(near) + 0.8 * th

        if alone(c):
            return mid, mid - half, mid + half, "ink", False
        # another curve crosses here and lengthens the run: the centre is interpolated between the
        # nearest columns where the curve runs alone; the interval keeps the whole merged run
        left = next((k for k in range(c - 1, c - 120, -1) if k in found and alone(k)), None)
        right = next((k for k in range(c + 1, c + 120) if k in found and alone(k)), None)
        if left is None or right is None:
            return mid, mid - half, mid + half, "ink", True
        ml, mr = sum(found[left]) / 2.0, sum(found[right]) / 2.0
        m = ml + (mr - ml) * (c - left) / (right - left)
        return m, min(m, r0 + th / 2.0), max(m, r1 - th / 2.0), "ink", True
    left = [k for k in found if k < c]
    right = [k for k in found if k > c]
    if not left or not right:
        return None
    cl, cr = max(left), min(right)
    (l0, l1), (q0, q1) = found[cl], found[cr]
    ml, mr = (l0 + l1) / 2.0, (q0 + q1) / 2.0
    mid = ml + (mr - ml) * (c - cl) / (cr - cl)
    lo = min(l0 + th / 2.0, q0 + th / 2.0, mid)
    hi = max(l1 - th / 2.0, q1 - th / 2.0, mid)
    return mid, lo, hi, f"gap of {cr - cl - 1} columns bridged", False


def read_wave(image, at, hlines, xmax, seed, style, label, solid_seed=None, axis="grey", dashed_seed=None):
    """Read one curve. seed = (x, y) in data units on the curve; style 'solid', 'dashed' or
    'dotted'. For a dashed or dotted curve, solid_seed names the solid curve to remove first;
    for a dotted curve, dashed_seed names a dashed curve to remove as well."""
    cal = calibrate(image, hlines, xmax, axis)
    grey, dark = _masks(image)
    if axis == "black":
        # the black axis lines are not curves: take them out (a curve touching them is bridged)
        dark = dark.copy()
        for rr in cal["line_rows"]:
            dark[rr[0] - 2:rr[1] + 3, :] = False
        dark[:, :int(np.ceil(cal["c0"] + cal["line_px"] / 2.0 + 2))] = False
    ax, bx, ay, by = cal["ax"], cal["bx"], cal["ay"], cal["by"]
    top = int(cal["top"] - 60)
    bottom = int(cal["bottom"] + 60)
    top, bottom = max(top, 0), min(bottom, dark.shape[0])
    c_start = int(np.ceil(cal["c0"]))
    c_end = int(np.floor(cal["c1"]))
    # the plot only: nothing left of the y axis or right of x = xmax
    dark = dark.copy()
    dark[:, :c_start] = False
    dark[:, c_end + 1:] = False

    def col(x):
        return (x - ax) / bx

    def row(y):
        return (y - ay) / by

    # line thickness: the shortest common run of ink of the solid curve
    if style == "solid":
        found = track(dark, top, bottom, c_start, c_end, int(round(col(seed[0]))), row(seed[1]), 8, 12)
        lens = np.array([r1 - r0 + 1 for r0, r1 in found.values()])
        th = float(np.percentile(lens, 10))
        found = track(dark, top, bottom, c_start, c_end, int(round(col(seed[0]))), row(seed[1]), 8, th)
    else:
        sfound = track(dark, top, bottom, c_start, c_end, int(round(col(solid_seed[0]))), row(solid_seed[1]), 8, 12)
        lens = np.array([r1 - r0 + 1 for r0, r1 in sfound.values()])
        th = float(np.percentile(lens, 10))
        sfound = track(dark, top, bottom, c_start, c_end, int(round(col(solid_seed[0]))), row(solid_seed[1]), 8, th)
        # remove the solid curve where it runs alone: a run not much longer than the solid's runs
        # in the neighbouring columns (a steep stretch has long runs throughout; another curve
        # crossing makes a few runs longer than their neighbours, and those are kept)
        clean = dark.copy()
        cols = sorted(sfound)
        lens = {c: sfound[c][1] - sfound[c][0] + 1 for c in cols}
        for c in cols:
            near = [lens[k] for k in range(c - 25, c + 26) if k in lens]
            if lens[c] <= np.median(near) + 0.8 * th:
                r0, r1 = sfound[c]
                clean[max(r0 - 3, 0):r1 + 4, c] = False
        dark = clean
        if dashed_seed is not None:
            # a dotted curve beside a dashed one: take the dashed strokes out too
            for s in (dashed_seed if isinstance(dashed_seed[0], (tuple, list)) else [dashed_seed]):
                _, dmask = chain(dark, top, bottom, int(round(col(s[0]))), row(s[1]), 8.0 * th)
                dark = dark & ~dmask
        reach = 8.0 * th if style == "dashed" else 4.0 * th
        # several seeds when the curve is hidden for a long stretch (under another curve) and
        # its visible pieces must each be found
        found = {}
        for s in (seed if isinstance(seed[0], (tuple, list)) else [seed]):
            f, _ = chain(dark, top, bottom, int(round(col(s[0]))), row(s[1]), reach, kind=style)
            for c, (r0, r1) in f.items():
                if c in found:
                    r0, r1 = min(r0, found[c][0]), max(r1, found[c][1])
                found[c] = (r0, r1)
    out = []
    for x in at:
        c = int(round(col(x)))
        v = value_at(found, c, th, 3.0 * th)
        if v is None:
            out.append({"x": x, "y": None, "note": f"{label}: the curve was not followed to x = {x}"})
            continue
        mid, rlo, rhi, how, merged = v
        pad = 2.0 + cal["res_y"] + abs(cal["res_x"]) * 0.0
        rlo, rhi = rlo - pad, rhi + pad
        # x calibration misfit moves the column; allow for the curve's change over it
        if cal["res_x"] > 0:
            for dc in (-int(np.ceil(cal["res_x"])), int(np.ceil(cal["res_x"]))):
                w = value_at(found, c + dc, th, 3.0 * th)
                if w is not None:
                    rlo, rhi = min(rlo, w[1] - pad), max(rhi, w[2] + pad)
        y = ay + by * mid
        ya, yb = ay + by * rlo, ay + by * rhi
        note = (f"{label}: {how}" + ("; overlaps another curve here, interval is the merged ink" if merged else "")
                + f"; line {th:.0f} px; y misfit {cal['res_y']:.1f} px, x end misfit {cal['res_x']:.1f} px")
        out.append({"x": x, "y": y, "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, mid],
                    "px_lo": rlo, "px_hi": rhi, "note": note})
    return out
