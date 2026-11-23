"""Shared reading code for the figures of panzetta2023.

The figures are raster images in the PDF, of two kinds: MATLAB line plots (Figs. 4, 5, 7, S2, S3:
a full box with inward tick marks) and Excel charts (Figs. 3, 6, 8, 9: a box without tick marks,
labels beside it). Each reading file names one panel and one series and calls `read_spec`.
Everything else is found in the image.

Frame    the plot box is the outermost pair of long thin dark vertical lines and the first and
         last long thin dark horizontal lines of the crop.
Axes     MATLAB: the tick marks are short dark segments standing inward from the left (or bottom)
         frame line. The printed labels of the axis give the values of the ticks; on a log axis the
         ticks are those of each decade (1..9 x 10^k). The calibration is found by matching: one
         labelled value (the `anchor`) sits on the frame line, and the scale is the one that places
         the most listed values on tick candidates (within 3 px); the matched ticks are then fitted
         by least squares (pixel against value, or log10 value), and the largest residual (at least
         half a pixel) is the misfit.
         Excel: no ticks. Each label is a block of dark text beside the frame; Excel centres a label
         on its value, so the label centres, matched in order to the printed labels, give the
         calibration (least squares, misfit as above). Category axes (bar charts) are not
         calibrated: bars are taken in order, left to right, as the categories listed in `at`.
Curves   (MATLAB) pixels whose grey level is in the series' band, inside the box, with the tick
         marks removed. The curve is followed column by column from a seed (the k-th run of the
         band from the top, in the column of a given x) by `boxgraph.digitize.trace`, which bridges
         gaps (dashes, markers of other series) and marks where curves of the same band merge. At a
         requested x, the traced centre; across a gap, the linear interpolation of the nearest traced
         columns on either side. 95% interval: half the run's height, half a pixel, the y misfit, the
         slope times the x misfit, and half the jump across a gap; where curves merge the interval
         covers the merged run.
Markers  (Excel and MATLAB points) the band's pixels opened by a disk wider than the line, so that
         only markers remain; the component whose centre column is nearest to the requested x
         (within the marker width) is the point, at its centroid. Interval: one pixel plus the misfit.
Bars     (Excel) columns of the series' band forming a run at least `min_bar` px wide that starts at
         the zero line; the bar end is the median far end over the bar's middle half. Error bars:
         caps are short horizontal runs of the error-bar band centred on the bar's centre column,
         narrower than half the bar; the two caps (or one cap and the bar end's mirror) whose
         midpoint is nearest to the bar end are its error bar. A cap hidden inside a bar of the same
         colour is taken as the mirror of the other end, as the note says.
"""
import importlib.util
import math
from pathlib import Path

import numpy as np
from scipy import ndimage

_DIG = None


def dig():
    global _DIG
    if _DIG is None:
        from boxgraph import digitize as d
        _DIG = d
    return _DIG


def gray(img):
    return img[..., :3].astype(float).mean(axis=2)


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def _longest(v, gap=2):
    best, bs = 0, 0
    for g in _groups(np.where(v)[0], gap=gap):
        n = int(g[-1] - g[0] + 1)
        if n > best:
            best, bs = n, int(g[0])
    return best, bs


# ------------------------------------------------------------------ frame

def frame(img, thr=175, frac=0.5, max_w=12):
    g = gray(img)
    m = g < thr
    H, W = m.shape
    cols = [c for c in range(W) if _longest(m[:, c])[0] >= frac * H]
    rows = [r for r in range(H) if _longest(m[r])[0] >= frac * W]
    cg = [x for x in _groups(cols, 1) if len(x) <= max_w]
    rg = [x for x in _groups(rows, 1) if len(x) <= max_w]
    if len(cg) < 1 or len(rg) < 2:
        raise ValueError("plot frame not found")
    left, right = cg[0], cg[-1]
    top, bottom = rg[0], rg[-1]
    return {"left": (int(left[0]), int(left[-1])), "right": (int(right[0]), int(right[-1])),
            "top": (int(top[0]), int(top[-1])), "bottom": (int(bottom[0]), int(bottom[-1]))}


def box(fr):
    return (fr["left"][1] + 1, fr["top"][1] + 1, fr["right"][0], fr["bottom"][0])


# ------------------------------------------------------------------ MATLAB ticks

def tick_candidates(img, fr, side, length, thr=120, far=30):
    """Positions of short dark segments standing inward from a frame line (and not continuing
    `far` px further: a curve or a legend line is longer than a tick)."""
    m = gray(img) < thr
    out = []
    if side == "left":
        c = fr["left"][1] + 1
        r0, r1 = fr["top"][0], fr["bottom"][1] + 1
        seg = m[r0:r1, c:c + length]
        beyond = m[r0:r1, c + length + far:c + length + far + 6].any(axis=1)
        hit = seg.all(axis=1) & ~beyond
        for gidx in _groups(np.where(hit)[0], 1):
            out.append(r0 + (gidx[0] + gidx[-1] + 1) / 2.0)
    else:  # bottom
        r = fr["bottom"][0] - 1
        c0, c1 = fr["left"][0], fr["right"][1] + 1
        seg = m[r - length + 1:r + 1, c0:c1]
        beyond = m[r - length - far - 6:r - length - far, c0:c1].any(axis=0)
        hit = seg.all(axis=0) & ~beyond
        for gidx in _groups(np.where(hit)[0], 1):
            out.append(c0 + (gidx[0] + gidx[-1] + 1) / 2.0)
    return out


def _u(v, scale):
    return math.log10(v) if scale == "log10" else float(v)


def match_axis(cands, values, scale, anchor_px=None, anchor_val=None, tol=3.0, direction=1):
    """The linear map (pixel against value, or log10 value) that places the most listed `values`
    on tick candidates within `tol` px, tried from every pair of candidates and pair of values;
    `direction` is the sign of pixels per unit (-1 for a y axis). Ties go to the smaller residual.
    The anchor (a labelled value on the frame line) is used only if `anchor_px` is given."""
    us = np.array([_u(v, scale) for v in values])
    cs = np.array(sorted(cands), float)
    best = None
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            if cs[j] - cs[i] < 20:
                continue
            for a in range(len(us)):
                for b_ in range(a + 1, len(us)):
                    slope = (cs[j] - cs[i]) / (us[b_] - us[a]) * (1 if direction > 0 else -1)
                    if slope * direction <= 0:
                        continue
                    if direction > 0:
                        p = cs[i] + slope * (us - us[a])
                    else:
                        p = cs[j] + slope * (us - us[a])
                    d = np.abs(p[:, None] - cs[None, :])
                    k = d.argmin(axis=1)
                    ok = d[np.arange(len(us)), k] <= tol
                    n = len(set(k[ok].tolist()))  # distinct ticks: two values on one tick count once
                    res = float(d[np.arange(len(us)), k][ok].sum())
                    key = (n, -res)
                    if best is None or key > best[0]:
                        best = (key, [(float(cs[k[q]]), values[q]) for q in range(len(us)) if ok[q]])
    marks = best[1] if best else []
    if anchor_px is not None and not any(w == anchor_val for _, w in marks):
        marks.append((anchor_px, anchor_val))
    if len(marks) < 3:
        raise ValueError(f"axis calibration: only {len(marks)} ticks matched the printed labels")
    return dig().Axis(scale, marks)


def matlab_axes(img, fr, spec):
    xs, ys = spec["x"], spec["y"]
    L = spec.get("tick_len", 8)
    t = spec.get("tick_thr", 120)
    xc = tick_candidates(img, fr, "bottom", spec.get("x_tick_len", L), thr=t)
    yc = tick_candidates(img, fr, "left", spec.get("y_tick_len", L), thr=t)
    # the frame line may itself carry the first or last tick: it is a candidate too
    xe = [(fr["left"][0] + fr["left"][1] + 1) / 2.0, (fr["right"][0] + fr["right"][1] + 1) / 2.0]
    ye = [(fr["top"][0] + fr["top"][1] + 1) / 2.0, (fr["bottom"][0] + fr["bottom"][1] + 1) / 2.0]
    xa = match_axis(xc + xe, xs["ticks"], xs.get("scale", "linear"), direction=1)
    ya = match_axis(yc + ye, ys["ticks"], ys.get("scale", "linear"), direction=-1)
    return xa, ya, xc, yc


def log_ticks(lo_exp, hi_exp):
    out = []
    for e in range(lo_exp, hi_exp):
        out += [k * 10 ** e for k in range(1, 10)]
    out.append(10 ** hi_exp)
    return out


# ------------------------------------------------------------------ Excel labels

def label_centres(img, fr, side, thr=140, gap=30, min_size=10, pad=60, offset=4, row_gap=8, gap_rows=4,
                  width=None):
    """Centres of the label blocks beside the frame. `width`: use only that many columns of the
    block nearest the frame (the last digit of right-aligned labels), so that an axis title close
    to the labels is not taken for one."""
    m = gray(img) < thr
    H, W = m.shape
    if side in ("left", "right"):
        r0, r1 = max(fr["top"][0] - pad, 0), min(fr["bottom"][1] + pad, H)
        present = m[r0:r1].any(axis=0)
        if side == "left":
            idx = range(fr["left"][0] - offset, -1, -1)
        else:
            idx = range(fr["right"][1] + offset, W)
        first = last = None
        miss = 0
        for c in idx:
            if present[c]:
                if first is None:
                    first = c
                last, miss = c, 0
            elif first is not None:
                miss += 1
                if miss > gap:
                    break
        c0, c1 = min(first, last), max(first, last)
        if width:
            if side == "left":
                c0 = max(c0, c1 - width)
            else:
                c1 = min(c1, c0 + width)
        rows = m[r0:r1, c0:c1 + 1].any(axis=1)
        out = []
        for gr in _groups(np.where(rows)[0], gap_rows):
            if gr[-1] - gr[0] + 1 >= min_size:
                out.append(r0 + (gr[0] + gr[-1] + 1) / 2.0)
        return out
    # bottom
    c0, c1 = max(fr["left"][0] - pad, 0), min(fr["right"][1] + pad, W)
    present = m[:, c0:c1].any(axis=1)
    first = last = None
    miss = 0
    for r in range(fr["bottom"][1] + offset, H):
        if present[r]:
            if first is None:
                first = r
            last, miss = r, 0
        elif first is not None:
            miss += 1
            if miss > row_gap:
                break
    cols = m[first:last + 1, c0:c1].any(axis=0)
    out = []
    for gc in _groups(np.where(cols)[0], gap):
        if gc[-1] - gc[0] + 1 >= min_size:
            out.append(c0 + (gc[0] + gc[-1] + 1) / 2.0)
    return out


def excel_axis(cents, labels, scale="linear", vertical=False):
    """Labels are listed in increasing value: left to right, or bottom to top (`vertical`)."""
    if len(cents) != len(labels):
        raise ValueError(f"found {len(cents)} label blocks for {len(labels)} printed labels")
    return dig().Axis(scale, list(zip(sorted(cents, reverse=vertical), labels)))


# ------------------------------------------------------------------ masks

def band(img, lo, hi, bx=None, inset=3):
    g = gray(img)
    m = (g >= lo) & (g <= hi)
    if bx is not None:
        c0, r0, c1, r1 = bx
        out = np.zeros_like(m)
        out[r0 + inset:r1 - inset, c0 + inset:c1 - inset] = m[r0 + inset:r1 - inset, c0 + inset:c1 - inset]
        m = out
    return m


def remove_ticks(mask, fr, xc, yc, L):
    m = mask.copy()
    for r in yc:
        r = int(r)
        m[r - 4:r + 5, fr["left"][1] + 1:fr["left"][1] + L + 4] = False
        m[r - 4:r + 5, fr["right"][0] - L - 3:fr["right"][0]] = False
    for c in xc:
        c = int(c)
        m[fr["bottom"][0] - L - 3:fr["bottom"][0], c - 4:c + 5] = False
        m[fr["top"][1] + 1:fr["top"][1] + L + 4, c - 4:c + 5] = False
    return m


def misfit(axis):
    return max(axis.residual_px, 0.5)


# ------------------------------------------------------------------ curves

def runs_in_col(mask, c):
    rows = np.nonzero(mask[:, c])[0]
    return [((g[0] + g[-1] + 1) / 2.0, (g[-1] - g[0] + 1) / 2.0) for g in _groups(rows, 1)]


def seed_point(mask, xa, seed, ya=None):
    """The k-th run (from the top; negative from the bottom) of the band in the column of x, or the
    nearest column that has enough runs. `ymin`/`ymax` (axis values) bound the search window, to
    keep the legend out."""
    c = int(math.floor(xa.to_pixel(seed["x"])))
    if "near" in seed:  # start on the run nearest to a row picked by eye (a start, not a value read)
        target = ya.to_pixel(seed["near"])
        for k in range(0, 60):
            dc = (k + 1) // 2 * (1 if k % 2 else -1)
            runs = [r for r in runs_in_col(mask, c + dc) if r[1] >= seed.get("min_half", 1.5)
                    and abs(r[0] - target) <= seed.get("within", 25)]
            if runs:
                return (c + dc + 0.5, min(runs, key=lambda r: abs(r[0] - target))[0])
        raise ValueError(f"no seed run near y = {seed['near']} at x = {seed['x']}")
    need = seed["rank"] + 1 if seed["rank"] >= 0 else -seed["rank"]
    for k in range(0, 60):
        dc = (k + 1) // 2 * (1 if k % 2 else -1)
        runs = [r for r in runs_in_col(mask, c + dc) if r[1] >= seed.get("min_half", 1.5)]
        if ya is not None and "ymax" in seed:
            runs = [r for r in runs if r[0] >= ya.to_pixel(seed["ymax"])]
        if ya is not None and "ymin" in seed:
            runs = [r for r in runs if r[0] <= ya.to_pixel(seed["ymin"])]
        if len(runs) >= need:
            runs.sort()
            return (c + dc + 0.5, runs[seed["rank"]][0])
    raise ValueError(f"no seed run at x = {seed['x']}")


def trace(mask, seed, max_gap=30, min_half=1.0, bend=0.4):
    """Follow a curve from the seed (column, row) both ways, column by column: in each column the
    run nearest to the row predicted by the last stretch traced (a line fitted to its last 15
    columns), accepted if within 6 px + its half-height + `bend` px per column of gap (a curve bends
    while hidden). Runs thinner than `min_half` (the antialiased rim of another curve) are skipped.
    Returns column -> (centre, half-height, merged), merged where the run is much taller than the
    curve's own (another curve of the same band joins it)."""
    W = mask.shape[1]
    c0 = int(math.floor(seed[0]))
    runs = [r for r in runs_in_col(mask, c0) if r[1] >= min_half]
    if not runs:
        return {}
    first = min(runs, key=lambda r: abs(r[0] - seed[1]))
    typical = first[1]
    path = {c0: (first[0], first[1], False)}
    for step in (1, -1):
        hist = [(c0, first[0])]
        c, gap = c0 + step, 0
        while 0 <= c < W and gap <= max_gap:
            h = hist[-15:]
            b = 0.0
            if len(h) >= 3:
                xs_ = np.array([p[0] for p in h], float)
                ys_ = np.array([p[1] for p in h], float)
                b, a = np.polyfit(xs_, ys_, 1)
                pred = a + b * c
            else:
                pred = hist[-1][1]
            stretch = math.sqrt(1 + b * b)
            cand = [r for r in runs_in_col(mask, c) if r[1] >= min_half]
            ok = False
            if cand:
                best = min(cand, key=lambda r: abs(r[0] - pred))
                if abs(best[0] - pred) <= 6 + best[1] + bend * gap:
                    merged = best[1] > 2.5 * typical * stretch + 4
                    centre = best[0]
                    if merged:
                        top, bot = best[0] - best[1], best[0] + best[1]
                        centre = min(max(pred, top), bot)
                    else:
                        typical = 0.9 * typical + 0.1 * best[1] / stretch
                    path[c] = (centre, best[1], merged)
                    hist.append((c, centre))
                    gap, ok = 0, True
            if not ok:
                gap += 1
            c += step
    return path


def read_traced(img, at, spec, xa, ya, mask):
    paths = []
    for sd in spec["seeds"]:
        p = trace(mask, seed_point(mask, xa, sd, ya), max_gap=spec.get("max_gap", 30),
                  min_half=sd.get("min_half", 1.0), bend=spec.get("bend", 0.4))
        lo = xa.to_pixel(sd["from"]) if "from" in sd else -1e9
        hi = xa.to_pixel(sd["to"]) if "to" in sd else 1e9
        paths.append((lo, hi, p))
    mx, my = misfit(xa), misfit(ya)
    out = []
    for xv in at:
        pc = xa.to_pixel(xv)
        col = int(math.floor(pc))
        use = [p for lo, hi, p in paths if lo <= pc <= hi]
        if not use:
            out.append({"x": xv, "y": None, "note": "outside the stretch read for this curve (curves cross or merge)"})
            continue
        path = use[0]
        note = ""
        if col in path:
            centre, half, amb = path[col]
            nb = [path[k][0] for k in (col - 2, col + 2) if k in path]
            slope = (nb[-1] - nb[0]) / 4 if len(nb) == 2 else 0.0
            jump = 0.0
        else:
            left = [k for k in path if col - spec.get("max_gap", 30) - 5 <= k < col]
            right = [k for k in path if col < k <= col + spec.get("max_gap", 30) + 5]
            if not left or not right:
                out.append({"x": xv, "y": None, "note": "the traced curve does not reach this x"})
                continue
            a, b = max(left), min(right)
            ya_, yb_ = path[a][0], path[b][0]
            centre = ya_ + (yb_ - ya_) * (pc - a) / (b - a)
            half = max(path[a][1], path[b][1])
            amb = path[a][2] or path[b][2]
            slope = (yb_ - ya_) / (b - a)
            jump = abs(yb_ - ya_) / 2
            note = f"interpolated across a gap of {b - a} px"
        if amb:
            note = (note + "; " if note else "") + "curves of the same grey merge here: the interval covers the merged run"
        h = half + 0.5 + abs(slope) * mx + my + jump
        y = ya.to_value(centre)
        a1, b1 = ya.to_value(centre - h), ya.to_value(centre + h)
        out.append({"x": xv, "y": y, "lo": min(a1, b1), "hi": max(a1, b1), "px": [pc, centre], "note": note})
    return out


def read_ranked(img, at, spec, xa, ya, mask):
    """Where a family of curves lies in a known order and apart: at each x, the columns nearest to
    it (within `search` px) in which the band shows exactly `n` runs at least `min_half` high; the
    curve is the `rank`-th of them from the top. A column with fewer runs (two curves touching) or
    more (a stray mark) is skipped; if no column within reach has `n` runs, the value is not read."""
    mx, my = misfit(xa), misfit(ya)
    n, k = spec["n"], spec["rank"]
    out = []
    for xv in at:
        pc = xa.to_pixel(xv)
        c0 = int(math.floor(pc))
        got = None
        for j in range(0, 2 * spec.get("search", 8) + 1):
            dc = (j + 1) // 2 * (1 if j % 2 else -1)
            runs = sorted(r for r in runs_in_col(mask, c0 + dc) if r[1] >= spec.get("min_half", 2.5))
            lg = spec.get("legend")  # under the legend's columns, keep only what lies below it
            if lg is not None and xv >= lg["x_from"]:
                runs = [r for r in runs if r[0] >= ya.to_pixel(lg["ymax"])]
            if len(runs) == n:
                got = (c0 + dc, runs[k])
                break
        if got is None:
            out.append({"x": xv, "y": None, "note": f"no column near this x shows the {n} curves apart"})
            continue
        c, (centre, half) = got
        left = sorted(r for r in runs_in_col(mask, c - 3) if r[1] >= spec.get("min_half", 2.5))
        right = sorted(r for r in runs_in_col(mask, c + 3) if r[1] >= spec.get("min_half", 2.5))
        slope = (right[k][0] - left[k][0]) / 6 if len(left) == n and len(right) == n else 0.0
        h = half + 0.5 + abs(slope) * (abs(pc - (c + 0.5)) + mx) + my
        y = ya.to_value(centre)
        a1, b1 = ya.to_value(centre - h), ya.to_value(centre + h)
        note = f"curve {k + 1} of {n} from the top, in column {c - c0:+d} px from x"
        if half > 8:
            note += "; a tall run here (a marker, or the line is steep): the interval covers it"
        out.append({"x": xv, "y": y, "lo": min(a1, b1), "hi": max(a1, b1), "px": [c + 0.5, centre], "note": note})
    return out


# ------------------------------------------------------------------ markers

def read_markers(img, at, spec, xa, ya, mask):
    r = spec["open_r"]
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (xx * xx + yy * yy) <= r * r
    opened = ndimage.binary_opening(mask, structure=disk)
    lab, n = ndimage.label(opened)
    comps = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        if len(rr) < spec.get("min_area", 50):
            continue
        comps.append((cc.mean() + 0.5, rr.mean() + 0.5, cc.max() - cc.min() + 1, rr.max() - rr.min() + 1, len(rr)))
    mx, my = misfit(xa), misfit(ya)
    out = []
    for xv in at:
        pc = xa.to_pixel(xv)
        near = [c for c in comps if abs(c[0] - pc) <= max(c[2], 10) * 0.75 + mx]
        if not near:
            out.append({"x": xv, "y": None, "note": "no marker of this series found at this x"})
            continue
        c = min(near, key=lambda c: abs(c[0] - pc))
        note = f"marker {c[2]}x{c[3]} px, {abs(c[0] - pc):.1f} px from the x position"
        if c[3] > 1.4 * c[2] or c[2] > 1.4 * c[3]:
            note += "; marker not round (merged with another): the interval covers its extent"
            h = max(c[2], c[3]) / 2.0 + my
        else:
            h = 1.0 + my
        y = ya.to_value(c[1])
        a1, b1 = ya.to_value(c[1] - h), ya.to_value(c[1] + h)
        out.append({"x": xv, "y": y, "lo": min(a1, b1), "hi": max(a1, b1), "px": [c[0], c[1]], "note": note})
    return out


# ------------------------------------------------------------------ bars

def bar_segments(mask, zero_row, direction, min_bar, min_len=3, gap=0):
    """Columns where the band forms a run starting within 20 px of the zero line (beyond the frame
    line and its antialiasing), grouped into bars."""
    H, W = mask.shape
    z = int(round(zero_row))
    ends = np.full(W, np.nan)
    for c in range(W):
        col = mask[:, c]
        if direction < 0:  # bars rise: run goes up from zero
            window = col[max(z - 20, 0):z + 1]
            if not window.any():
                continue
            start = max(z - 20, 0) + int(np.nonzero(window)[0].max())
            r = start
            while r > 0:
                if col[r - 1]:
                    r -= 1
                    continue
                # a cap or stem of an error bar drawn across the bar: bridge up to `gap` rows
                ahead = col[max(r - 1 - gap, 0):r - 1]
                if ahead.any():
                    r = max(r - 1 - gap, 0) + int(np.nonzero(ahead)[0].max())
                    continue
                break
            if start - r + 1 >= min_len:
                ends[c] = r
        else:  # bars hang down from zero
            window = col[z:z + 21]
            if not window.any():
                continue
            start = z + int(np.nonzero(window)[0].min())
            r = start
            while r < H - 1:
                if col[r + 1]:
                    r += 1
                    continue
                ahead = col[r + 2:r + 2 + gap]
                if ahead.any():
                    r = r + 2 + int(np.nonzero(ahead)[0].min())
                    continue
                break
            if r - start + 1 >= min_len:
                ends[c] = r + 1
    # an error bar drawn over a bar interrupts its band for a few columns: bridge up to 15
    segs = [g for g in _groups(np.where(~np.isnan(ends))[0], 15) if g[-1] - g[0] + 1 >= min_bar]
    out = []
    for g in segs:
        mid = g[len(g) // 4: len(g) - len(g) // 4]
        e = ends[mid]
        out.append((float(g[0]), float(g[-1] + 1), float(np.median(e[~np.isnan(e)]))))
    return out


def caps(errmask, centre, maxw, minw):
    """Rows of short horizontal runs of the error-bar band centred on the column `centre`."""
    H, W = errmask.shape
    c = int(round(centre))
    rows = []
    for r in range(H):
        if not errmask[r, c]:
            continue
        a = c
        while a > 0 and errmask[r, a - 1]:
            a -= 1
        b = c
        while b < W - 1 and errmask[r, b + 1]:
            b += 1
        w = b - a + 1
        if minw <= w <= maxw and abs((a + b) / 2 - c) <= 6:
            rows.append(r)
    return [(g[0] + g[-1] + 1) / 2.0 for g in _groups(rows, 2)]


def read_bars(img, at, spec, xa, ya, fr):
    bx = box(fr)
    own = band(img, *spec["bar_band"], bx=bx, inset=2)
    m = own
    if "front_band" in spec:  # a bar standing behind another: its visible part continues the front bar
        m = own | band(img, *spec["front_band"], bx=bx, inset=2)
    zero = ya.to_pixel(0.0)
    direction = spec.get("direction", -1)
    segs = bar_segments(m, zero, direction, spec["min_bar"], gap=spec.get("bridge", 0))
    if "categories" in spec and len(segs) == len(spec["categories"]):
        # bars in order are the listed categories; read those asked for
        byc = dict(zip([float(c) for c in spec["categories"]], segs))
        if all(float(x) in byc for x in at):
            segs = [byc[float(x)] for x in at]
    my = misfit(ya)
    out = []
    if len(segs) != len(at):
        return [{"x": xv, "y": None, "note": f"found {len(segs)} bars for {len(at)} categories"} for xv in at]
    em = band(img, *spec["err_band"], bx=bx, inset=1) if "err_band" in spec else None
    for xv, (c0, c1, endr) in zip(at, segs):
        cc = (c0 + c1) / 2.0
        h = 1.0 + my
        y = ya.to_value(endr)
        a1, b1 = ya.to_value(endr - h), ya.to_value(endr + h)
        d = {"x": xv, "y": y, "lo": min(a1, b1), "hi": max(a1, b1), "px": [cc, endr],
             "note": f"bar {int(c1 - c0)} px wide"}
        if "front_band" in spec:
            q0, q1 = int(c0 + (c1 - c0) / 4), int(c1 - (c1 - c0) / 4)
            e = int(round(endr))
            # the 36 rows inside the end: mostly the bar's own grey if it shows (a cap may cross them)
            rows = range(e + 4, e + 40) if direction < 0 else range(e - 40, e - 4)
            frac = float(own[list(rows), q0:q1].mean())
            if frac < 0.4:
                out.append({"x": xv, "y": None, "note": "this bar is hidden behind the bar in front of it"})
                continue
            d["note"] += "; the visible end of a bar standing behind the other series' bar"
        if em is not None:
            cp = caps(em, cc, maxw=(c1 - c0) * 0.5, minw=spec.get("cap_min", 12))
            cp = [r for r in cp if abs(r - zero) > 4]
            best = None
            for i in range(len(cp)):
                for j in range(i + 1, len(cp)):
                    mid = (cp[i] + cp[j]) / 2
                    dd = abs(mid - endr)
                    if best is None or dd < best[0]:
                        best = (dd, cp[i], cp[j], False)
            tol = spec.get("pair_tol", 6)
            if best is None or best[0] > tol:
                # one end hidden: the visible cap beyond the bar end, mirrored
                beyond = [r for r in cp if (r - endr) * direction > 0]
                if beyond and spec.get("mirror", True):
                    r1 = min(beyond, key=lambda r: abs(r - endr))
                    best = (0.0, r1, 2 * endr - r1, True)
                else:
                    best = None
            if best is not None:
                _, ra, rb, mirrored = best
                err = 1.0 + my
                v1, v2 = ya.to_value(ra), ya.to_value(rb)
                lo, hi = min(v1, v2), max(v1, v2)
                o1, o2 = ya.to_value(ra - err), ya.to_value(ra + err)
                o3, o4 = ya.to_value(rb - err), ya.to_value(rb + err)
                d.update({"bar_lo": lo, "bar_hi": hi, "bar_lo_outer": min(o1, o2, o3, o4),
                          "bar_hi_outer": max(o1, o2, o3, o4), "px_lo": min(ra, rb), "px_hi": max(ra, rb)})
                if mirrored:
                    d["note"] += "; one end of the error bar hidden inside the bar: taken as the mirror of the other"
            else:
                d["note"] += "; error bar not found"
        out.append(d)
    return out


# ------------------------------------------------------------------ entry

def read_spec(image, at, spec):
    img = np.asarray(image)
    fr = frame(img, thr=spec.get("frame_thr", 175))
    at = [float(a) for a in at]
    if spec["kind"] == "matlab":
        xa, ya, xc, yc = matlab_axes(img, fr, spec)
        m = band(img, *spec["band"], bx=box(fr))
        if "exclude" in spec:  # the antialiased rim of a darker curve falls in a lighter band
            lo, hi, grow = spec["exclude"]
            ex = ndimage.binary_dilation(band(img, lo, hi), iterations=grow)
            m &= ~ex
        if spec.get("close"):  # JPEG noise speckles a grey line across its band's limits
            m = ndimage.binary_closing(m, iterations=spec["close"])
        m = remove_ticks(m, fr, xc, yc, spec.get("tick_len", 8) + 14)
        if spec.get("trim"):  # drop a strip along the top and bottom frame (short ticks not all found)
            t = spec["trim"]
            m[:fr["top"][1] + 1 + t] = False
            m[fr["bottom"][0] - t:] = False
        if spec.get("mode") == "markers":
            return read_markers(img, at, spec, xa, ya, marker_mask(img, fr, spec))
        if spec.get("mode") == "rank":
            return read_ranked(img, at, spec, xa, ya, m)
        return read_traced(img, at, spec, xa, ya, m)
    # excel
    lk = spec.get("labels", {})
    ys = spec["y"]
    ya = excel_axis(label_centres(img, fr, ys.get("side", "left"), **lk), ys["labels"], vertical=True)
    if spec.get("mode") == "bars":
        return read_bars(img, at, spec, None, ya, fr)
    xa = excel_axis(label_centres(img, fr, "bottom", **spec.get("xlabels", {})), spec["x"]["labels"])
    return read_markers(img, at, spec, xa, ya, marker_mask(img, fr, spec))


def marker_mask(img, fr, spec):
    """The series' band inside the box grown by `pad` px (a marker on the frame line is half outside
    the box; the thin frame line itself does not survive the opening), less the dilated band of
    a darker series if `exclude` is given."""
    pad = spec.get("pad", 25)
    c0, r0, c1, r1 = box(fr)
    H, W = img.shape[:2]
    m = band(img, *spec["band"], bx=(max(c0 - pad, 0), max(r0 - pad, 0), min(c1 + pad, W), min(r1 + pad, H)), inset=0)
    if "exclude" in spec:
        lo, hi, grow = spec["exclude"]
        m &= ~ndimage.binary_dilation(band(img, lo, hi), iterations=grow)
    return m


def load(path):
    spec = importlib.util.spec_from_file_location("panzetta2023_p23", Path(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
