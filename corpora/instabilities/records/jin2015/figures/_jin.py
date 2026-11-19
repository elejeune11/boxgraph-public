# Shared helpers for the jin2015 figure readings: everything is measured on the rendered crop.
# The plots are framed boxes with inward ticks on all four sides (Mathematica / MATLAB style).
import math

import numpy as np


def gray(img):
    return img.astype(float).mean(axis=2)


def dark(img, thr=110):
    """Near-black, unsaturated pixels (axes, ticks, black curves, text)."""
    a = img.astype(int)
    sat = a.max(axis=2) - a.min(axis=2)
    return (gray(img) < thr) & (sat < 60)


def color(img, rgb, tol):
    a = img.astype(float)
    return np.sqrt(((a - np.array(rgb, float)) ** 2).sum(axis=2)) < tol


def hue_mask(img, kind):
    """Colour classes by channel dominance, robust to JPEG blur."""
    a = img.astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "red":
        return (r > 150) & (g < 110) & (b < 110) & (r - g > 90)
    if kind == "green":
        return (g > 110) & (g - r > 30) & (g - b > 50)
    if kind == "blue":
        return (b > 110) & (b - r > 50) & (b - g > 30)
    raise ValueError(kind)


def frame(img, frac=0.5, thr=110):
    """Centre lines of the plot frame: (c0, r0, c1, r1) and line half-thickness."""
    d = dark(img, thr)
    H, W = d.shape
    rows = [r for r in range(H) if d[r].sum() > frac * W]
    cols = [c for c in range(W) if d[:, c].sum() > frac * H]

    def groups(v):
        out, cur = [], [v[0]]
        for x in v[1:]:
            if x - cur[-1] <= 2:
                cur.append(x)
            else:
                out.append(cur)
                cur = [x]
        out.append(cur)
        return out

    gr, gc = groups(rows), groups(cols)
    top, bot, left, right = gr[0], gr[-1], gc[0], gc[-1]
    half = max(len(top), len(bot), len(left), len(right)) / 2.0
    return (float(np.mean(left)), float(np.mean(top)), float(np.mean(right)), float(np.mean(bot))), half


def _clusters(profile, start, minlen):
    """Runs where profile >= minlen; returns (centre index, max length)."""
    out, cur = [], []
    for i, v in enumerate(profile):
        if v >= minlen:
            cur.append((i, v))
        elif cur:
            idx = [c[0] for c in cur]
            out.append((start + float(np.mean(idx)), max(c[1] for c in cur)))
            cur = []
    if cur:
        idx = [c[0] for c in cur]
        out.append((start + float(np.mean(idx)), max(c[1] for c in cur)))
    return out


def _run_from(line):
    n = 0
    for v in line:
        if not v:
            break
        n += 1
    return n


def ticks(img, box, half, side, maxlen=80, minlen=6, thr=110, margin=None):
    """Inward ticks on one side of the frame: list of (pixel position, length)."""
    d = dark(img, thr)
    c0, r0, c1, r1 = [int(round(v)) for v in box]
    h = int(math.ceil(half)) + 1
    m = margin if margin is not None else 2 * h + 4
    if side == "left":
        prof = [_run_from(d[r, c0 + h:c0 + h + maxlen]) for r in range(r0 + m, r1 - m)]
        return _clusters(prof, r0 + m, minlen)
    if side == "right":
        prof = [_run_from(d[r, c1 - h - maxlen:c1 - h][::-1]) for r in range(r0 + m, r1 - m)]
        return _clusters(prof, r0 + m, minlen)
    if side == "bottom":
        prof = [_run_from(d[r1 - h - maxlen:r1 - h, c][::-1]) for c in range(c0 + m, c1 - m)]
        return _clusters(prof, c0 + m, minlen)
    if side == "top":
        prof = [_run_from(d[r0 + h:r0 + h + maxlen, c]) for c in range(c0 + m, c1 - m)]
        return _clusters(prof, c0 + m, minlen)
    raise ValueError(side)


class Axis:
    """value = 10**(a + b*pixel) (log) or a + b*pixel (linear), fitted by least squares."""

    def __init__(self, pix, vals, log):
        self.log = log
        u = [math.log10(v) if log else v for v in vals]
        b, a = np.polyfit(pix, u, 1)
        self.a, self.b = float(a), float(b)
        res = [(self.to_pix(v) - p) for p, v in zip(pix, vals)]
        self.misfit_px = float(max(abs(x) for x in res)) if res else 0.0
        self.n = len(pix)

    def to_val(self, p):
        u = self.a + self.b * p
        return 10 ** u if self.log else u

    def to_pix(self, v):
        u = math.log10(v) if self.log else v
        return (u - self.a) / self.b

    def per_px(self, p):
        """Value change for one pixel at pixel p."""
        return abs(self.to_val(p + 0.5) - self.to_val(p - 0.5))


def lin_axis_from_ticks(tk, values, major_frac=0.0):
    """Linear axis: ticks (all of length >= major_frac*max) matched in order to `values`."""
    tk = sorted(tk)
    L = max(t[1] for t in tk)
    pos = [t[0] for t in tk if t[1] >= major_frac * L]
    if len(pos) != len(values):
        raise ValueError(f"found {len(pos)} ticks at {pos}, expected {len(values)}")
    return Axis(pos, values, False)


def runs(col):
    """Runs of True in a boolean column: list of (start, end) inclusive."""
    out, s = [], None
    for i, v in enumerate(col):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append((s, i - 1))
            s = None
    if s is not None:
        out.append((s, len(col) - 1))
    return out


def curve_rows(mask, col, r0, r1, halfwin=2, minrun=2):
    """Row centres of the runs of `mask` in columns col-halfwin..col+halfwin within rows r0..r1,
    from the column itself: list of (centre, half thickness)."""
    c = int(round(col))
    m = mask[int(r0):int(r1), c]
    out = []
    for s, e in runs(m):
        if e - s + 1 >= minrun:
            out.append((r0 + (s + e) / 2.0, (e - s + 1) / 2.0))
    return out


def point(x, y, lo, hi, col, row, row_lo, row_hi, note=""):
    return {"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [float(col), float(row)],
            "px_lo": float(row_lo), "px_hi": float(row_hi), "note": note}


def interval(yax, row, half, misfit):
    """95% interval on a value read at `row`: half the line thickness plus the calibration
    misfit plus one pixel, in pixels, mapped through the axis."""
    w = half + misfit + 1.0
    a, b = yax.to_val(row - w), yax.to_val(row + w)
    return min(a, b), max(a, b), row - w, row + w


def log_axis(tk, majors, lo_exp, hi_exp, major_frac=0.7, tol_dec=0.012):
    """Calibrate a log axis from its ticks: the longer ticks carry the labels `majors` (pixel
    order); every other tick is matched to the nearest k*10^n and kept if within tol_dec decades.
    Returns an Axis fitted to all matched ticks."""
    tk = sorted(tk)
    L = max(t[1] for t in tk)
    maj = [t[0] for t in tk if t[1] >= major_frac * L]
    if len(maj) != len(majors):
        raise ValueError(f"found {len(maj)} major ticks at {maj}, expected {len(majors)} ({majors})")
    if len(maj) == 1:
        # one decade tick: its neighbours are 0.9 and 2 times its value; the farther one is 2x
        p0 = maj[0]
        below = max((t[0] for t in tk if t[0] < p0 - 1), default=None)
        above = min((t[0] for t in tk if t[0] > p0 + 1), default=None)
        if below is None or above is None:
            raise ValueError("one major tick without neighbours on both sides")
        if abs(above - p0) > abs(p0 - below):
            ax = Axis([p0, above, below], [majors[0], 2 * majors[0], 0.9 * majors[0]], True)
        else:
            ax = Axis([p0, below, above], [majors[0], 2 * majors[0], 0.9 * majors[0]], True)
    else:
        ax = Axis(maj, majors, True)
    cands = sorted({k * 10.0 ** n for n in range(lo_exp, hi_exp + 1) for k in range(1, 10)})
    pix, vals = [], []
    for p, _ in tk:
        u = math.log10(ax.to_val(p))
        best = min(cands, key=lambda c: abs(math.log10(c) - u))
        if abs(math.log10(best) - u) < tol_dec:
            pix.append(p)
            vals.append(best)
    return Axis(pix, vals, True)


def merge_ticks(a, b, tol=6.0):
    """Ticks seen on two opposite sides: keep the positions found on both (within tol px),
    averaged, with the shorter length (a curve meeting the frame lengthens a tick on one side);
    a mark on one side only is dropped."""
    out = []
    for p, l in sorted(a):
        near = [q for q in b if abs(q[0] - p) <= tol]
        if near:
            q = min(near, key=lambda q: abs(q[0] - p))
            out.append(((p + q[0]) / 2.0, min(l, q[1])))
    return out


def trace_at(mask, col, r0, r1, win=40, thick_max=None, prefer=None):
    """Centre row of a thin curve in `mask` at column `col`, from a straight-line fit to the
    single-run centres of the columns within +-win (columns where the mask has more than one
    run, or a run thicker than thick_max, are skipped: markers, labels, crossings).
    `prefer` (a row) picks, in each column, the run nearest it when there are several.
    Returns (row, half thickness, residual px, n columns) or None."""
    cs, rs, hs = [], [], []
    for c in range(int(col) - win, int(col) + win + 1):
        if c < 0 or c >= mask.shape[1]:
            continue
        rr = curve_rows(mask, c, r0, r1)
        if prefer is not None and rr:
            rr = [min(rr, key=lambda t: abs(t[0] - prefer))]
            if abs(rr[0][0] - prefer) > 3 * win:
                continue
        if len(rr) != 1:
            continue
        if thick_max is not None and rr[0][1] * 2 > thick_max:
            continue
        cs.append(c)
        rs.append(rr[0][0])
        hs.append(rr[0][1])
    if len(cs) < max(6, win // 3):
        return None
    k, m = np.polyfit(cs, rs, 1)
    res = np.array(rs) - (k * np.array(cs) + m)
    keep = np.abs(res) < max(3.0, 2.5 * res.std())
    if keep.sum() >= 6:
        k, m = np.polyfit(np.array(cs)[keep], np.array(rs)[keep], 1)
        res = np.array(rs)[keep] - (k * np.array(cs)[keep] + m)
    return float(k * col + m), float(np.median(hs)), float(np.abs(res).max()), len(cs)


def follow(mask, c_start, r_start, c_lo, c_hi, r0, r1, max_jump=12):
    """Follow a curve column by column from (c_start, r_start), in both directions, taking in
    each column the run nearest the previous row (within max_jump px); returns {column: row}."""
    path = {}
    for step, end in ((1, c_hi), (-1, c_lo)):
        prev, missed, slope = r_start, 0, 0.0
        for c in range(int(c_start), int(end), step):
            rr = curve_rows(mask, c, r0, r1)
            guess = prev + slope * (missed + 1)  # carry on along the recent slope over gaps
            if rr:
                best = min(rr, key=lambda t: abs(t[0] - guess))
                if abs(best[0] - guess) <= max_jump * (1 + 0.5 * missed):
                    slope = 0.8 * slope + 0.2 * (best[0] - prev) / (missed + 1)
                    prev, missed = best[0], 0
                else:
                    missed += 1
            else:
                missed += 1
            path[c] = prev + slope * missed
    return path


def read_curve(mask, xax, yax, box, half, at, win=40, thick_max=None, guess=None, margin=30, tag="",
               seed=None, max_res=6.0):
    """Read a curve of `mask` at the x values `at`; 95% interval from half the line thickness,
    the local fit residual, the axis misfits (x misfit through the local slope) and one pixel.
    `seed` = (x value, y value) on the curve where it is alone: the curve is then followed from
    there and, in each column, the run nearest the followed path is taken. A local fit with a
    residual above max_res px (a curve hidden under another, or confused with markers) is not read."""
    c0, r0, c1, r1 = box
    if seed is not None and guess is None:
        path = follow(mask, xax.to_pix(seed[0]), yax.to_pix(seed[1]), c0 + margin, c1 - margin,
                      r0 + margin, r1 - margin)
        guess = lambda col: path.get(int(round(col)))  # noqa: E731
    out = []
    for x in at:
        col = xax.to_pix(x)
        if not (c0 + half < col < c1 - half):
            out.append({"x": x, "y": None, "note": f"{tag} x outside the plot box"})
            continue
        pref = guess(col) if guess else None
        t = trace_at(mask, col, r0 + margin, r1 - margin, win=win, thick_max=thick_max, prefer=pref)
        if t is None:
            out.append({"x": x, "y": None, "note": f"{tag} curve not found near this x"})
            continue
        row, h, res, n = t
        if res > max_res:
            out.append({"x": x, "y": None, "note": f"{tag} not read: local fit residual {res:.1f} px (curve hidden "
                                                   f"under another or among markers)"})
            continue
        t2 =trace_at(mask, col + 5, r0 + margin, r1 - margin, win=win, thick_max=thick_max, prefer=pref)
        slope = abs((t2[0] - row) / 5.0) if t2 else 0.0
        w = h + res + yax.misfit_px + slope * xax.misfit_px + 1.0
        lo, hi = yax.to_val(row + w), yax.to_val(row - w)
        out.append({"x": x, "y": yax.to_val(row), "lo": min(lo, hi), "hi": max(lo, hi),
                    "px": [col, row], "px_lo": row - w, "px_hi": row + w,
                    "note": f"{tag} line half-thickness {h:.1f} px, fit residual {res:.1f} px over {n} columns"})
    return out


def ring_centres(mask, rmin, rmax, box, frac=0.55, thick=3):
    """Centres of open circular markers in `mask`: the radius whose ring kernel matches best,
    then peaks of the ring correlation above `frac` of a full ring.
    Returns (list of (col, row, score), radius)."""
    from scipy.ndimage import maximum_filter
    from scipy.signal import fftconvolve
    c0, r0, c1, r1 = [int(round(v)) for v in box]
    m = mask[r0:r1, c0:c1].astype(float)
    best = None
    for R in range(rmin, rmax + 1):
        yy, xx = np.mgrid[-R - thick:R + thick + 1, -R - thick:R + thick + 1]
        rr = np.sqrt(xx ** 2 + yy ** 2)
        ker = (np.abs(rr - R) <= thick / 2.0).astype(float)
        inner = (rr < R - thick).astype(float)
        acc = fftconvolve(m, ker[::-1, ::-1], mode="same") / ker.sum()
        acc -= 0.5 * fftconvolve(m, inner[::-1, ::-1], mode="same") / inner.sum()
        score = acc.max()
        if best is None or score > best[0]:
            best = (score, R, acc)
    score, R, acc = best
    peaks = (acc == maximum_filter(acc, size=2 * R)) & (acc > frac)
    rows, cols = np.nonzero(peaks)
    cand = sorted(((float(acc[r, c]), c0 + float(c), r0 + float(r)) for r, c in zip(rows, cols)), reverse=True)
    kept = []
    for s, c, r in cand:  # one centre per ring: plateaus give several equal peaks
        if all((c - k[0]) ** 2 + (r - k[1]) ** 2 > R * R for k in kept):
            kept.append((c, r, s))
    return sorted(kept), R
