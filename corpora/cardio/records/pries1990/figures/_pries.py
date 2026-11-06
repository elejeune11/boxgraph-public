"""Shared reading code for Figs. 1 and 3 of Pries et al. 1990 (black line plots, log diameter axis).

Calibration comes from the image: the frame lines are the long dark rows and columns; the x ticks
hang below the lowest frame line (major ticks, the longer ones, are labelled 5, 10, 20, 50, 100
on the page) and the y ticks stick out to the left of the left frame line (labelled as printed
beside them). A curve is identified by its rank from the top among the curves crossing a column,
using only columns where exactly the expected number of curves is seen (a dash gap or two curves
merging into one run changes the count, and that column is not used).
"""

import numpy as np

X_LABELS = [5.0, 10.0, 20.0, 50.0, 100.0]


def dark(image):
    g = image.astype(float).mean(axis=2)
    paper = float(np.percentile(g, 60))
    ink = float(np.percentile(g, 0.5))
    return g < (paper + ink) / 2


def _groups(idx):
    """Consecutive integers grouped: list of (first, last)."""
    out = []
    for i in idx:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(g) for g in out]


def _longest(v):
    best, cur = 0, 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def frame(d):
    """Horizontal frame lines (first, last row) top to bottom, and for each panel its left and
    right frame columns (first, last)."""
    H, W = d.shape
    long_rows = [r for r in range(H) if _longest(d[r]) >= 0.6 * W]
    hlines = _groups(long_rows)
    panels = []
    for k in range(0, len(hlines) - 1, 2):
        top, bot = hlines[k], hlines[k + 1]
        span = d[top[1] + 1:bot[0], :]
        frac = span.mean(axis=0)
        cols = _groups([c for c in range(W) if frac[c] >= 0.9])
        panels.append({"top": top, "bottom": bot, "left": cols[0], "right": cols[-1]})
    return hlines, panels


def _ticks(lengths, min_len=6):
    """Group neighbouring positions whose perpendicular run is at least min_len: (centre, length)."""
    pos = [p for p, n in sorted(lengths.items()) if n >= min_len]
    return [((a + b) / 2.0, max(lengths[q] for q in range(a, b + 1))) for a, b in _groups(pos) if b - a <= 40]


def fit(pos, vals):
    pos, vals = np.asarray(pos, float), np.asarray(vals, float)
    A = np.vstack([np.ones_like(pos), pos]).T
    coef, *_ = np.linalg.lstsq(A, vals, rcond=None)
    res = vals - A @ coef
    slope = coef[1]
    misfit_px = float(np.max(np.abs(res / slope))) if len(pos) > 2 else 0.0
    return coef, misfit_px


def calibrate(image, panel_index, y_labels):
    """x: log10(D) as a linear function of column; y: value as a linear function of row."""
    d = dark(image)
    hlines, panels = frame(d)
    p = panels[panel_index]
    # x ticks below the lowest frame line of the figure
    last = hlines[-1]
    H = d.shape[0]
    p_last = panels[-1]
    W = d.shape[1]
    lengths = {}
    for c in range(p_last["left"][0] - 5, p_last["right"][1] + 6):
        # the dark run through the (possibly slightly tilted) line, downwards
        r = last[0] - 6
        while r <= last[1] + 6 and not d[r, c]:
            r += 1
        n = 0
        while r < H and d[r, c]:
            n += 1
            r += 1
        lengths[c] = n
    base = float(np.median(list(lengths.values())))
    lengths = {c: max(0, int(n - base)) for c, n in lengths.items()}
    # the left frame line continues below the axis at the unlabelled left end (D = 4): not a labelled tick
    xt = [t for t in _ticks(lengths) if abs(t[0] - (p_last["left"][0] + p_last["left"][1]) / 2) > 15]
    longest = max(n for _, n in xt)
    major = [c for c, n in xt if n >= 0.75 * longest]
    if len(major) != len(X_LABELS):
        raise ValueError(f"found {len(major)} major x ticks, expected {len(X_LABELS)}: {xt}")
    xcoef, xmis = fit(major, np.log10(X_LABELS))
    # y ticks to the left of this panel's left frame line
    lengths = {}
    for r in range(p["top"][0] - 15, p["bottom"][1] + 16):
        # the dark run through the left frame line, leftwards
        c = p["left"][1] + 6
        while c >= p["left"][0] - 6 and not d[r, c]:
            c -= 1
        n = 0
        while c >= 0 and d[r, c]:
            n += 1
            c -= 1
        lengths[r] = n
    base = float(np.median(list(lengths.values())))
    lengths = {r: max(0, int(n - base)) for r, n in lengths.items()}
    yt = _ticks(lengths)
    if len(yt) != len(y_labels):
        longest = max(n for _, n in yt)
        yt = [t for t in yt if t[1] >= 0.5 * longest]  # drops curve ends touching the frame
    if len(yt) != len(y_labels):
        raise ValueError(f"found {len(yt)} y ticks, expected {len(y_labels)}: {yt}")
    yrows = [r for r, _ in yt]
    ycoef, ymis = fit(yrows, y_labels)
    return {"d": d, "panel": p, "x": xcoef, "x_misfit_px": xmis, "y": ycoef, "y_misfit_px": ymis,
            "x_ticks": major, "y_ticks": yrows}


# How many curves cross a column at diameter D, where that count is reliable. Positions where the
# curve labels (HD = 0.8, 0.6, 0.45, 0.3, 0.1) stand among the curves, or where the curves crowd
# together or leave the panel, are None (seen on the page: labels near D = 30-60 in Fig. 1 upper,
# 22-34 and 60-75 in Fig. 1 lower, 37-65 in Fig. 3).
def n_fig1_upper(D):
    return 5 if (D <= 28 or D >= 62) else None


def n_fig1_lower(D):
    if 9.5 <= D <= 20.5:
        return 5  # HD = 0.8 leaves the panel at the top near D = 24
    if 36 <= D <= 56 or D >= 80:
        return 4
    return None


def n_fig3(D):
    return 5 if (8.8 <= D <= 32 or D >= 70) else None


def col_of(cal, D):
    a, b = cal["x"]
    return (np.log10(D) - a) / b


def val_of(cal, row):
    a, b = cal["y"]
    return a + b * row


def runs_in(cal, col, margin=12):
    p = cal["panel"]
    r0, r1 = p["top"][1] + 1 + margin, p["bottom"][0] - margin
    v = cal["d"][r0:r1, int(col)]
    out = []
    for a, b in _groups(list(np.nonzero(v)[0])):
        out.append((r0 + a, r0 + b))
    return out


def read_rank(cal, at, from_bottom, n_expected, window=40, min_cols=6):
    """Read the curve that is `from_bottom`-th from the bottom (0 = lowest) among the curves that
    cross a column. n_expected: a function of D giving how many curves cross the panel there
    (None where labels or crowding make the count unreliable)."""
    out = []
    p = cal["panel"]
    for D in at:
        c = col_of(cal, D)
        n = n_expected(D)
        rank = None if n is None else n - 1 - from_bottom
        if c < p["left"][1] + 15 or c > p["right"][0] - 15 or rank is None or rank < 0:
            out.append({"x": D, "y": None, "note": "outside the readable part of the panel"})
            continue
        cols, centres, halfs = [], [], []
        for cc in range(int(round(c)) - window, int(round(c)) + window + 1):
            if cc <= p["left"][1] + 3 or cc >= p["right"][0] - 3:
                continue
            rs = runs_in(cal, cc)
            if len(rs) != n:
                continue
            a, b = rs[rank]
            cols.append(cc)
            centres.append((a + b) / 2.0)
            halfs.append((b - a + 1) / 2.0)
        if len(cols) < min_cols:
            out.append({"x": D, "y": None, "note": f"only {len(cols)} columns near D={D} show exactly {n} curves"})
            continue
        cols, centres = np.asarray(cols, float), np.asarray(centres, float)
        keep = np.ones(len(cols), bool)
        for _ in range(3):
            # a quadratic trend through the columns; columns far off it (a curve missed in a dash
            # gap while another run took its place) are dropped
            A = np.vstack([np.ones_like(cols), cols - c, (cols - c) ** 2]).T
            coef, *_ = np.linalg.lstsq(A[keep], centres[keep], rcond=None)
            r_all = centres - A @ coef
            mad = 1.4826 * float(np.median(np.abs(r_all[keep])))
            new = np.abs(r_all) <= max(3.0 * mad, 4.0)
            if new.sum() < min_cols or (new == keep).all():
                break
            keep = new
        if keep.sum() < min_cols or keep.sum() < 0.5 * len(cols):
            out.append({"x": D, "y": None, "note": f"columns near D={D} disagree on which run is the curve"})
            continue
        resid = r_all[keep]
        row = float(coef[0])
        half = float(np.median(halfs))
        # 95% interval: half the line's vertical extent, the trend misfit, and the calibration misfits
        slope_px = abs(float(coef[1]))
        err_px = half + 2.0 * float(np.std(resid)) + cal["y_misfit_px"] + slope_px * cal["x_misfit_px"] + 0.5
        y = float(val_of(cal, row))
        lo, hi = sorted([float(val_of(cal, row + err_px)), float(val_of(cal, row - err_px))])
        out.append({"x": D, "y": y, "lo": lo, "hi": hi, "px": [float(c), row],
                    "px_lo": row - err_px, "px_hi": row + err_px,
                    "note": f"{len(cols)} columns; line half-extent {half:.1f} px; +-{err_px:.1f} px"})
    return out
