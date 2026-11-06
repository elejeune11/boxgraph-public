"""Fig. 12 (PDF p. 11): measured pressures of Remington and Wood (ref. 41), a scanned figure with
only a left and a bottom axis (no frame).

Calibration, all from the image: the left axis is the column with the most dark pixels, the bottom
axis the row with the most dark pixels. y ticks are the short dark segments that leave the left
axis to the right; x ticks the short dark segments that rise from the bottom axis. Each reader
passes the printed labels it matched to these ticks; a straight line is fitted and its worst
misfit added to every interval.

Thick line ('Aortic' in A, '0 cm' in B): the dark mask is opened with a disk a little wider than
the thin lines. The disk radius comes from the image: the half-widths of the ink (ridge values of
the distance transform) have a main mode for the thin lines; the radius is that mode + 1.5 px,
so only the thick line (half-width about 2 px more) survives; the surviving pieces are linked by a
dilation of the disk's size and only the widest linked piece, the curve, is kept (labels, arrow
heads and bits of thicker dashes stay apart from it). At a
column, the value is the centre of the wanted surviving run (the reader says which: the lowest,
the uppermost, or the only one); its interval is the run's extent + 2 px + the y misfit + the
local slope times the x misfit.

Topmost line: the uppermost dark run in the column (any line style), for the stretch where one
curve is clearly above all others (the radial pressure peak in B).
"""
import numpy as np
from scipy import ndimage


def _groups(idx, gap=1):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def axes(image):
    g = image[..., :3].astype(float).mean(axis=2)
    dark = g < 128
    h, w = dark.shape
    left = int(np.argmax(dark[:, : w // 2].sum(0)))
    bottom = int(h // 2 + np.argmax(dark[h // 2:, :].sum(1)))
    # axis half-widths
    lw = int(np.sum(dark[h // 2, max(0, left - 15):left + 16]))
    bw = int(np.sum(dark[max(0, bottom - 15):bottom + 16, w // 2]))
    L = 20
    yt = [r for r in range(0, bottom - bw - L) if dark[r, left + lw:left + lw + L].all()]
    xt = [c for c in range(left + lw, w) if dark[bottom - bw - L:bottom - bw, c].all()]
    yt = [float(np.mean(gr)) for gr in _groups(yt, 2)]
    xt = [float(np.mean(gr)) for gr in _groups(xt, 2)]
    return dict(gray=g, dark=dark, left=left, bottom=bottom, yticks=yt, xticks=xt)


def fit(pix, vals):
    pix, vals = np.asarray(pix, float), np.asarray(vals, float)
    a, b = np.polyfit(vals, pix, 1)
    return a, b, float(np.abs(a * vals + b - pix).max())


def calibrate(image, x_labels, x_select, y_labels, y_select):
    """x_labels: the printed values of the x ticks picked by x_select (a slice of the ticks sorted
    left to right); y likewise with the ticks sorted bottom to top."""
    ax_ = axes(image)
    xt = sorted(ax_["xticks"])[x_select]
    yt = sorted(ax_["yticks"], reverse=True)[y_select]
    if len(xt) != len(x_labels) or len(yt) != len(y_labels):
        raise ValueError(f"ticks found x {ax_['xticks']} y {ax_['yticks']}")
    axx, bx, xmis = fit(xt, x_labels)
    ayy, by, ymis = fit(yt, y_labels)
    ax_.update(col_of=lambda x: axx * x + bx, x_of=lambda c: (c - bx) / axx, val_of=lambda r: (r - by) / ayy,
               row_of=lambda v: ayy * v + by, xmis=xmis, ymis=ymis, ax=axx)
    return ax_


def thick_mask(cal):
    dark = cal["dark"]
    dt = ndimage.distance_transform_edt(dark)
    ridge = (dt == ndimage.maximum_filter(dt, size=3)) & (dt > 0)
    hist = np.bincount(np.round(dt[ridge]).astype(int))
    r = float(np.argmax(hist)) + 1.5
    n = int(np.ceil(r))
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1]
    op = ndimage.binary_opening(dark, structure=(xx ** 2 + yy ** 2) <= r * r)
    # keep only the curve: the surviving pieces are linked by a dilation of about the line width and
    # the widest linked piece is kept (labels, arrow heads and bits of dashes stay apart from it)
    linked = ndimage.binary_dilation(op, iterations=n + 1)
    lab, _ = ndimage.label(linked, structure=np.ones((3, 3)))
    widths = [sl[1].stop - sl[1].start for sl in ndimage.find_objects(lab)]
    return op & (lab == 1 + int(np.argmax(widths))), r


def _runs(col, r0, r1):
    return [(gr[0] + r0, gr[-1] + r0) for gr in _groups(list(np.where(col[r0:r1])[0]), 1)]


def _slope(mask, c, rc, r0, r1, k=12):
    """Local slope (rows per column) of the line through (c, rc): centres of the nearest runs k
    columns either side."""
    cs = []
    for cc in (c - k, c + k):
        runs = _runs(mask[:, cc], r0, r1)
        if not runs:
            return 0.0
        a, b = min(runs, key=lambda ab: abs(0.5 * (ab[0] + ab[1]) - rc))
        cs.append(0.5 * (a + b))
    return (cs[1] - cs[0]) / (2 * k)


def _value(cal, x, c, run, how, slope=0.0, extra_cols=0):
    a, b = run
    rc = 0.5 * (a + b)
    # the x misfit (and any columns pooled in the reading) move the column: as rows, times the slope
    pad = 2 + cal["ymis"] + abs(slope) * (cal["xmis"] + extra_cols)
    ya, yb = cal["val_of"](a - pad), cal["val_of"](b + pad)
    return {"x": x, "y": cal["val_of"](rc), "lo": min(ya, yb), "hi": max(ya, yb), "px": [c, rc],
            "px_lo": a - pad, "px_hi": b + pad,
            "note": f"{how}; run rows {a}-{b}; slope {slope:.2f} rows/col; misfit x {cal['xmis']:.1f} px, y {cal['ymis']:.1f} px"}


def read_thick(cal, at, which, y_floor):
    """which: 'lowest', 'uppermost' or 'only'. Rows below the row of value y_floor (the lowest y tick) are ignored."""
    mask, r = thick_mask(cal)
    r1 = int(cal["row_of"](y_floor)) - 5
    out = []
    for x in at:
        c = int(round(cal["col_of"](x)))
        runs = _runs(mask[:, c], 0, r1)
        if not runs:
            out.append({"x": x, "y": None, "note": f"no thick run in column {c}"})
            continue
        if which == "only" and len(runs) != 1:
            out.append({"x": x, "y": None, "note": f"{len(runs)} thick runs in column {c}: {runs}"})
            continue
        run = max(runs) if which == "lowest" else runs[0]  # 'uppermost' and 'only' take the first
        s = _slope(mask, c, 0.5 * (run[0] + run[1]), 0, r1)
        out.append(_value(cal, x, c, run, f"thick line ({which} of {len(runs)} runs; opening radius {r:.1f} px)", s))
    return out


def read_top(cal, at, y_ceiling, half=8):
    """The uppermost dark run below the row of value y_ceiling, in the union of the columns c-half to
    c+half (so that a gap of a dotted or dashed line does not hand the column to a lower line)."""
    r0 = 0 if y_ceiling is None else int(cal["row_of"](y_ceiling))
    out = []
    for x in at:
        c = int(round(cal["col_of"](x)))
        col = cal["dark"][:, c - half:c + half + 1].any(axis=1)
        runs = _runs(col, r0, cal["bottom"] - 30)
        if not runs:
            out.append({"x": x, "y": None, "note": f"no dark run in column {c}"})
            continue
        tops = []
        for cc in (c - 3 * half, c + 3 * half):
            rr = _runs(cal["dark"][:, cc - half:cc + half + 1].any(axis=1), r0, cal["bottom"] - 30)
            tops.append(0.5 * (rr[0][0] + rr[0][1]) if rr else 0.5 * (runs[0][0] + runs[0][1]))
        s = (tops[1] - tops[0]) / (6 * half)
        out.append(_value(cal, x, c, runs[0], f"uppermost of {len(runs)} dark runs", s, half))
    return out
