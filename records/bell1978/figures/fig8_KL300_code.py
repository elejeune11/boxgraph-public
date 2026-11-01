"""Fig. 8 (PDF p. 7 = 624): log10 t* against f*, four black curves (KL = 300, 1000, 3000, 10^4).

Everything is found in the image (900 dpi crop of the panel with its tick labels):
  box:  the four frame lines, as the rows/columns with the longest dark runs;
  y:    the tick marks on the left frame edge (one per unit) are found as short
        horizontal dark runs just inside the edge; the label blobs left of the frame
        ("2", "0", ..., "-14") are matched to the nearest tick, top label = 2 and each
        next label 2 lower; the ticks between labels get the odd values. Linear fit.
  x:    the tick marks rising from the bottom frame edge are found as short vertical
        dark runs just inside it; there are six, printed .6, .8, 1.0, 2, 3, 4. The axis
        is calibrated on 1.0, 2, 3, 4 (evenly spaced); .6 and .8 are reported as
        residuals only (they sit off the linear scale the other four define).
  curve: the four curves are distinct runs in the column at f* = 2 (no labels there);
        the chosen one (0 = top) is followed column by column in both directions,
        accepting only runs of about the line's thickness near the predicted row, so
        the curve labels (which touch the curves near f* = 3-3.5) are skipped. At each
        `at`, a quadratic is fitted to the traced centres within +-W columns.
Interval: calibration misfit (y, and x times the local slope) + 2x the local-fit rms
+ a quarter of the line thickness, all in pixels, converted with the y scale.
"""
import numpy as np

WHICH = 0            # 0 = top curve (KL=300), 1 = KL=1000, 2 = KL=3000, 3 = KL=10^4
X_LABELS = [0.6, 0.8, 1.0, 2.0, 3.0, 4.0]   # matched: the printed x labels, left to right
X_CAL = [1.0, 2.0, 3.0, 4.0]                 # the evenly spaced labelled ticks used to calibrate
Y_TOP_LABEL = 2.0                            # matched: the top y label is "2", then 0, -2, ..., -14
Y_LABEL_STEP = -2.0
SEED_X = 2.0
WIN = 30             # half-window in columns for the local fit


def _runs(v):
    """(start, end exclusive) of runs of True."""
    d = np.diff(np.concatenate([[0], v.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def _line_center(prof):
    """Subpixel centre of the darkest band in a 1-D darkness profile."""
    i = int(np.argmax(prof))
    lo, hi = max(i - 6, 0), min(i + 7, len(prof))
    w = np.clip(prof[lo:hi] - 0.3 * prof[i], 0, None)
    return float((np.arange(lo, hi) * w).sum() / w.sum())


def calibrate(img):
    g = img.astype(float).mean(axis=2)
    dark = g < 128
    h, w = g.shape
    dk = np.clip(255 - g, 0, None)
    # frame: columns / rows where dark pixels cover most of the plot height / width
    colfrac, rowfrac = dark.mean(axis=0), dark.mean(axis=1)
    left = _line_center(np.where(np.arange(w) < w // 3, colfrac, 0))
    right = _line_center(np.where(np.arange(w) > 2 * w // 3, colfrac, 0))
    top = _line_center(np.where(np.arange(h) < h // 3, rowfrac, 0))
    bottom = _line_center(np.where(np.arange(h) > 2 * h // 3, rowfrac, 0))
    # y ticks: horizontal marks just inside the left edge
    strip = dark[:, int(left) + 8:int(left) + 30]
    tick_rows = []
    for s, e in _runs(strip.mean(axis=1) > 0.9):
        if e - s <= 12 and top + 5 < s and e < bottom - 5:
            prof = dk[s - 3:e + 3, int(left) + 8:int(left) + 30].mean(axis=1)
            tick_rows.append(s - 3 + _line_center(prof))
    tick_rows = np.array(sorted(tick_rows))
    step = float(np.median(np.diff(tick_rows)))
    # y labels: ink blobs left of the frame
    # (the window stops short of the rotated axis title "Log10 t*" further left)
    lab = dark[:, max(int(left) - 190, 0):int(left) - 25].any(axis=1)
    blobs = [((s + e - 1) / 2.0) for s, e in _runs(lab) if e - s > 20]
    pts = []
    for i, b in enumerate(blobs):
        k = int(np.argmin(np.abs(tick_rows - b)))
        if abs(tick_rows[k] - b) < step / 3:
            pts.append((k, Y_TOP_LABEL + Y_LABEL_STEP * i))
    # every tick gets a value from its index relative to the labelled ones
    ks, vs = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
    per_tick, v0 = np.polyfit(ks, vs, 1)
    vals = v0 + per_tick * np.arange(len(tick_rows))
    if np.max(np.abs(np.polyval([per_tick, v0], ks) - vs)) > 0.01 or abs(abs(per_tick) - 1) > 0.01:
        raise RuntimeError("y labels do not match one tick per unit")
    yb, ya = np.polyfit(vals, tick_rows, 1)            # row = ya + yb * value
    misfit_y = float(np.max(np.abs(tick_rows - (ya + yb * vals))))
    # x ticks: vertical marks rising from the bottom edge
    xs = dark[int(bottom) - 30:int(bottom) - 8, :]
    tick_cols = []
    for s, e in _runs(xs.mean(axis=0) > 0.95):
        if e - s <= 12 and left + 5 < s and e < right - 5:
            prof = dk[int(bottom) - 30:int(bottom) - 8, s - 3:e + 3].mean(axis=0)
            tick_cols.append(s - 3 + _line_center(prof))
    tick_cols = sorted(tick_cols)
    if len(tick_cols) != len(X_LABELS):
        raise RuntimeError(f"found {len(tick_cols)} x ticks, expected {len(X_LABELS)}: {tick_cols}")
    cal = [(c, v) for c, v in zip(tick_cols, X_LABELS) if v in X_CAL]
    cc, cv = np.array([c[0] for c in cal]), np.array([c[1] for c in cal])
    xb, xa = np.polyfit(cv, cc, 1)                     # col = xa + xb * value
    misfit_x = float(np.max(np.abs(cc - (xa + xb * cv))))
    off = {v: float(c - (xa + xb * v)) for c, v in zip(tick_cols, X_LABELS) if v not in X_CAL}
    return dict(left=left, right=right, top=top, bottom=bottom, ya=ya, yb=yb, xa=xa, xb=xb,
                misfit_y=misfit_y, misfit_x=misfit_x, n_y=len(tick_rows), n_ylab=len(pts),
                x_off=off, dark=dark)


def _col_runs(dark, c, r0, r1):
    return [(s + r0, e + r0) for s, e in _runs(dark[r0:r1, c])]


def trace(img, which, cal):
    dark = cal["dark"]
    r0, r1 = int(cal["top"]) + 8, int(cal["bottom"]) - 8
    c0, c1 = int(cal["left"]) + 35, int(cal["right"]) - 8
    seed_c = int(round(cal["xa"] + cal["xb"] * SEED_X))
    # the tick marks at the top and bottom frame edges lie in this column too: skip runs near the frame
    runs = [r for r in _col_runs(dark, seed_c, r0, r1) if r[0] > r0 + 50 and r[1] < r1 - 50]
    if len(runs) != 4:
        raise RuntimeError(f"expected 4 curves at f* = {SEED_X}, found {len(runs)}")
    lw = float(np.median([e - s for s, e in runs]))
    s, e = runs[which]
    pts = {seed_c: ((s + e - 1) / 2.0, e - s)}
    for direction in (1, -1):
        hist = [(seed_c, pts[seed_c][0])]
        c, gap = seed_c + direction, 0
        while c0 <= c <= c1 and gap < 80:
            recent = hist[-20:]
            if len(recent) >= 3:
                p = np.polyfit([q[0] for q in recent], [q[1] for q in recent], 1)
                pred, slope = np.polyval(p, c), p[0]
            else:
                pred, slope = hist[-1][1], 0.0
            expect = lw * np.sqrt(1 + slope ** 2)
            tol = max(4.0, 0.5 * expect) + 0.5 * gap * abs(slope) * 0.1
            best = None
            for s, e in _col_runs(dark, c, r0, r1):
                ctr = (s + e - 1) / 2.0
                if abs(ctr - pred) < tol and (e - s) < 1.4 * expect + 2:
                    if best is None or abs(ctr - pred) < abs(best[0] - pred):
                        best = (ctr, e - s)
            if best is not None:
                pts[c] = best
                hist.append((c, best[0]))
                gap = 0
            else:
                gap += 1
            c += direction
    return pts, lw


def read(image, at):
    return read_which(image, at, WHICH)


def read_which(image, at, which):
    cal = calibrate(image)
    pts, lw = trace(image, which, cal)
    cols = np.array(sorted(pts))
    rows = np.array([pts[c][0] for c in cols])
    out = []
    note0 = (f"y: {cal['n_y']} ticks, {cal['n_ylab']} labels matched, misfit {cal['misfit_y']:.2f} px; "
             f"x: ticks 1.0-4 misfit {cal['misfit_x']:.2f} px, .6 off by {cal['x_off'].get(0.6, 0):+.1f} px, "
             f".8 off by {cal['x_off'].get(0.8, 0):+.1f} px; line {lw:.0f} px")
    for x in at:
        c = cal["xa"] + cal["xb"] * x
        sel = np.abs(cols - c) <= WIN
        if sel.sum() < 10 or cols.min() > c + 3 or cols.max() < c - 3:
            out.append({"x": x, "y": None, "note": f"the curve is not traced at this f* (traced columns "
                        f"{cols.min()}-{cols.max()}, wanted {c:.0f})"})
            continue
        # a quadratic when the window has traced columns on both sides; at a curve end
        # (one-sided window) a quadratic extrapolates badly, so a straight line
        both = (cols[sel] < c - WIN / 2).any() and (cols[sel] > c + WIN / 2).any()
        p = np.polyfit(cols[sel] - c, rows[sel], 2 if both else 1)
        row = float(p[-1])
        slope = float(p[-2])
        rms = float(np.sqrt(np.mean((np.polyval(p, cols[sel] - c) - rows[sel]) ** 2)))
        err_px = cal["misfit_y"] + abs(slope) * cal["misfit_x"] + 2 * rms + lw / 4
        y = (row - cal["ya"]) / cal["yb"]
        err = err_px / abs(cal["yb"])
        out.append({"x": x, "y": float(y), "lo": float(y - err), "hi": float(y + err), "px": [float(c), row],
                    "px_lo": row - err_px, "px_hi": row + err_px,
                    "note": f"{int(sel.sum())} traced columns, local rms {rms:.2f} px, slope {slope:.2f}; " + note0})
    return out
