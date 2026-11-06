"""Shared figure-reading code for olufsen2012. Everything is found in the image.

Calibration: the plot box is the frame of long dark lines (centre of each frame line). The tick
labels printed outside the box are found as clusters of dark ink: the labels left of the box give
rows (each label's vertical centre is its tick's row), the labels under the box give columns (each
label's horizontal centre is its tick's column). The printed values I matched to the labels are
passed in by each reader in order (top to bottom, left to right). A straight line value -> pixel is
fitted to all labels and the worst misfit is reported and added to every interval.

Curves are found by colour (Figs. 8, 9) or as dark neutral ink (Fig. 5 lines); markers as
connected blobs of their colour.
"""
import numpy as np
from scipy import ndimage


def gray(image):
    return image[..., :3].astype(float).mean(axis=2)


def chroma(image):
    im = image[..., :3].astype(float)
    return im.max(axis=2) - im.min(axis=2)


def dark_neutral(image, level=110, max_chroma=60):
    return (gray(image) < level) & (chroma(image) < max_chroma)


def groups(idx, gap=2):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def frame(image, frac=0.6):
    """Rows/columns of the frame lines: (top, bot, left, right, half-thickness) as line centres."""
    d = dark_neutral(image)
    h, w = d.shape
    rows, cols = d.sum(1), d.sum(0)
    rg = groups(list(np.where(rows > frac * rows.max())[0]))
    cg = groups(list(np.where(cols > frac * cols.max())[0]))
    rg = [g for g in rg if len(g) >= 2] or rg
    cg = [g for g in cg if len(g) >= 2] or cg
    top, bot = float(np.mean(rg[0])), float(np.mean(rg[-1]))
    left, right = float(np.mean(cg[0])), float(np.mean(cg[-1]))
    half = 0.5 * max(len(rg[0]), len(rg[-1]), len(cg[0]), len(cg[-1]))
    return top, bot, left, right, half


def _clusters_1d(lo_hi, gap):
    """Merge intervals (lo, hi) closer than gap; return merged (lo, hi)."""
    out = []
    for lo, hi in sorted(lo_hi):
        if out and lo - out[-1][1] <= gap:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out


def label_rows(image, top, bot, left, gap_px, margin):
    """Vertical centres of the tick labels left of the box (between rows top-margin and bot+margin)."""
    d = gray(image) < 128
    r0, r1 = int(max(0, top - margin)), int(min(d.shape[0], bot + margin))
    region = d[r0:r1, : int(left - gap_px)]
    lab, n = ndimage.label(region)
    boxes = ndimage.find_objects(lab)
    spans = [(b[0].start + r0, b[0].stop - 1 + r0) for b in boxes if b is not None]
    # keep only clusters near the axis: the rightmost column group of ink
    cl = _clusters_1d(spans, gap=2)
    return [0.5 * (a + b) for a, b in cl], region


def label_rows_near(image, top, bot, left, gap_px, margin, width):
    """As label_rows, but only ink within `width` px left of (left - gap_px): the tick labels, not the axis title."""
    d = gray(image) < 128
    r0, r1 = int(max(0, top - margin)), int(min(d.shape[0], bot + margin))
    c1 = int(left - gap_px)
    c0 = int(max(0, c1 - width))
    region = d[r0:r1, c0:c1]
    lab, n = ndimage.label(region)
    spans = [(b[0].start + r0, b[0].stop - 1 + r0) for b in ndimage.find_objects(lab) if b is not None]
    cl = _clusters_1d(spans, gap=2)
    return [0.5 * (a + b) for a, b in cl]


def label_cols(image, bot, left, right, gap_px, height, merge_gap, margin):
    """Horizontal centres of the tick labels under the box (rows bot+gap_px .. bot+gap_px+height,
    columns from 3 margins left of the box to 3 margins right of it, so wide end labels are whole).
    Ink touching the top row of that band is left out: it is the lower part of a y label at the
    corner, not an x label (x labels sit clear of the frame)."""
    d = gray(image) < 128
    r0 = int(bot + gap_px)
    r1 = int(min(d.shape[0], r0 + height))
    c0, c1 = int(max(0, left - 3 * margin)), int(min(d.shape[1], right + 3 * margin))
    region = d[r0:r1, c0:c1]
    lab, n = ndimage.label(region)
    spans = [(b[1].start + c0, b[1].stop - 1 + c0) for b in ndimage.find_objects(lab)
             if b is not None and b[0].start > 0]
    cl = _clusters_1d(spans, gap=merge_gap)
    return [0.5 * (a + b) for a, b in cl]


def fit(pix, vals, what):
    if len(pix) != len(vals):
        raise ValueError(f"expected {len(vals)} {what} labels, found {len(pix)} at {[round(p) for p in pix]}")
    pix, vals = np.asarray(pix, float), np.asarray(vals, float)
    a, b = np.polyfit(vals, pix, 1)
    return a, b, float(np.abs(a * vals + b - pix).max())


def calibrate(image, x_vals, y_vals, *, x_gap, x_height, x_merge, y_gap, y_width, margin, frame_frac=0.6,
              x_from_frame=None, y_from_frame=None, x_skip=None, y_stop=None):
    """x_vals: printed x labels left to right; y_vals: printed y labels top to bottom.
    x_from_frame / y_from_frame: optional (value at left/top frame, value at right/bottom frame) added
    as two more calibration points (the frame lines sit at the end labels).
    x_skip: search x labels only from this many px right of the left frame (leaves out a label
    under the corner that may belong to either axis); y_stop: search y labels only down to this
    many px above the bottom frame."""
    top, bot, left, right, half = frame(image, frame_frac)
    if x_skip is None:
        xc = label_cols(image, bot, left, right, x_gap, x_height, x_merge, margin)
    else:
        xc = label_cols(image, bot, left + x_skip + 3 * margin, right, x_gap, x_height, x_merge, margin)
    if y_stop is None:
        yr = label_rows_near(image, top, bot, left, y_gap, margin, y_width)
    else:
        yr = label_rows_near(image, top, bot - y_stop - margin, left, y_gap, margin, y_width)
    xp, xv = list(xc), list(x_vals)
    if len(xp) != len(xv):
        raise ValueError(f"expected {len(xv)} x labels, found {len(xp)} at {[round(p) for p in xp]}")
    yp, yv = list(yr), list(y_vals)
    if len(yp) != len(yv):
        raise ValueError(f"expected {len(yv)} y labels, found {len(yp)} at {[round(p) for p in yp]}")
    if x_from_frame:
        xp += [left, right]
        xv += list(x_from_frame)
    if y_from_frame:
        yp += [top, bot]
        yv += list(y_from_frame)
    ax, bx, xmis = fit(xp, xv, "x")
    ay, by, ymis = fit(yp, yv, "y")
    return dict(top=top, bot=bot, left=left, right=right, half=half, xmis=xmis, ymis=ymis,
                col_of=lambda x: ax * x + bx, x_of=lambda c: (c - bx) / ax, val_of=lambda r: (r - by) / ay,
                x_labels=xc, y_labels=yr, dx_per_px=1.0 / abs(ax), dy_per_px=1.0 / abs(ay))


def note(cal):
    return (f"calibrated on {len(cal['x_labels'])} x and {len(cal['y_labels'])} y tick labels; "
            f"misfit x {cal['xmis']:.1f} px, y {cal['ymis']:.1f} px")


def interval(cal, r_lo, r_hi, pad=2.0):
    """Value interval for a row span, widened by the y misfit and pad px."""
    p = pad + cal["ymis"]
    a, b = cal["val_of"](r_lo - p), cal["val_of"](r_hi + p)
    return min(a, b), max(a, b), r_lo - p, r_hi + p


def color_mask(image, rgb, tol):
    im = image[..., :3].astype(float)
    return np.sqrt(((im - np.asarray(rgb, float)) ** 2).sum(axis=2)) < tol


def inside(cal, mask, inset):
    m = mask.copy()
    t, b, l, r = (int(round(v)) for v in (cal["top"], cal["bot"], cal["left"], cal["right"]))
    m[: t + inset, :] = False
    m[b - inset:, :] = False
    m[:, : l + inset] = False
    m[:, r - inset:] = False
    return m


def column_runs(mask, c, r0, r1):
    return [(g[0] + r0, g[-1] + r0) for g in groups(list(np.where(mask[r0:r1, c])[0]), gap=1)]


def read_color_curve(image, cal, at, mask, half_window, slope_pad=True):
    """Value of a coloured curve at each x. In a window of +-half_window columns, collect the rows of
    the curve's pixels; fit a straight line row(c) through them (dashes and dots leave gaps but the
    window spans several) and evaluate at the column of x. The interval is the spread of the
    curve's pixels about that line (its thickness), plus the y misfit and the x misfit times the slope."""
    out = []
    for x in at:
        c = cal["col_of"](x)
        ci = int(round(c))
        cs, rs = [], []
        for cc in range(ci - half_window, ci + half_window + 1):
            if cc < 0 or cc >= mask.shape[1]:
                continue
            rr = np.where(mask[:, cc])[0]
            cs += [cc] * len(rr)
            rs += list(rr)
        if len(set(cs)) < max(3, half_window // 3):
            out.append({"x": x, "y": None, "note": f"only {len(set(cs))} columns of the curve's colour near column {ci}"})
            continue
        cs, rs = np.asarray(cs, float), np.asarray(rs, float)
        if np.ptp(cs) == 0:
            out.append({"x": x, "y": None, "note": "curve pixels in one column only"})
            continue
        k, m = np.polyfit(cs, rs, 1)
        res = rs - (k * cs + m)
        if np.ptp(res) > 6 * (np.percentile(res, 90) - np.percentile(res, 10) + 2):
            out.append({"x": x, "y": None, "note": "pixels of this colour scatter: another mark of the same colour nearby"})
            continue
        rc = k * c + m
        thick = 0.5 * (np.percentile(res, 98) - np.percentile(res, 2))
        extra = abs(k) * cal["xmis"] if slope_pad else 0.0
        lo, hi, plo, phi = interval(cal, rc - thick - extra, rc + thick + extra)
        out.append({"x": x, "y": cal["val_of"](rc), "lo": lo, "hi": hi, "px": [c, rc], "px_lo": plo, "px_hi": phi,
                    "note": f"line fit over columns {ci - half_window}-{ci + half_window}, half thickness {thick:.1f} px; " + note(cal)})
    return out


def blobs(mask, min_area, max_area=None):
    lab, n = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        area = int((lab[sl] == i).sum())
        if area < min_area or (max_area and area > max_area):
            continue
        out.append(dict(r0=sl[0].start, r1=sl[0].stop - 1, c0=sl[1].start, c1=sl[1].stop - 1, area=area))
    return out
