"""Shared reading helpers for the figures of gardel2008.

Every reading file imports this module through `load_lib()`, which pins the file by its
SHA-256 so a build cache keyed on a reading file cannot serve a reading made with an
older version of these helpers. Everything here works from the image only: no value
from the paper appears in this file.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


def gray(img):
    return np.asarray(img, dtype=float).mean(axis=2)


def sat(img):
    f = np.asarray(img, dtype=float)
    return f.max(axis=2) - f.min(axis=2)


def neutral_dark(img, level=120, max_sat=60):
    return (gray(img) < level) & (sat(img) < max_sat)


def runs(v):
    """Contiguous runs of True in a 1-D boolean array, as (start, stop_exclusive)."""
    v = np.asarray(v, dtype=bool)
    d = np.diff(np.concatenate([[0], v.astype(int), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def line_center(profile_dark, lo, hi):
    """Darkness-weighted centre of a line between indices lo and hi (exclusive)."""
    idx = np.arange(lo, hi)
    w = profile_dark[lo:hi]
    return float((idx * w).sum() / w.sum())


def frame(img, region=None, frac=0.5, level=120):
    """The four edges of a rectangular plot frame: the longest neutral dark lines.
    region: (r0, r1, c0, c1) to search in. Returns dict top, bottom, left, right (subpixel)."""
    m = neutral_dark(img, level)
    r0, r1, c0, c1 = region if region else (0, m.shape[0], 0, m.shape[1])
    sub = m[r0:r1, c0:c1]
    rf = sub.mean(axis=1)
    cf = sub.mean(axis=0)
    rr = [(a, b) for a, b in runs(rf > frac)]
    cc = [(a, b) for a, b in runs(cf > frac)]
    if len(rr) < 2 or len(cc) < 2:
        raise ValueError(f"frame not found: rows {rr}, cols {cc}")
    top = line_center(rf, rr[0][0], rr[0][1]) + r0
    bottom = line_center(rf, rr[-1][0], rr[-1][1]) + r0
    left = line_center(cf, cc[0][0], cc[0][1]) + c0
    right = line_center(cf, cc[-1][0], cc[-1][1]) + c0
    return {"top": top, "bottom": bottom, "left": left, "right": right,
            "lw_row": float(rr[-1][1] - rr[-1][0]), "lw_col": float(cc[0][1] - cc[0][0])}


def ticks(img, line, span, axis, inward, depth, level=120, min_frac=0.6, lw=None, mask=None):
    """Tick marks on a frame edge.
    axis 'x': the edge is a row `line`; ticks are short vertical strokes between columns span=(c0, c1),
    going `inward` (+1 down, -1 up) from the line. axis 'y': the edge is a column, ticks horizontal,
    span = rows. Returns [(centre, length)] with length the stroke's extent from the line in pixels."""
    m = neutral_dark(img, level) if mask is None else mask
    lw = lw or 8
    start = int(round(line + inward * (lw / 2 + 3)))
    stop = int(round(line + inward * depth))
    a, b = sorted((start, stop))
    if axis == "x":
        band = m[a:b, int(span[0]):int(span[1])]
        prof = band.mean(axis=0)
        off = int(span[0])
    else:
        band = m[int(span[0]):int(span[1]), a:b].T
        prof = band.mean(axis=0)
        off = int(span[0])
    out = []
    first = band[:min(6, band.shape[0])] if inward > 0 else band[-min(6, band.shape[0]):]
    near = first.mean(axis=0)
    for s, e in runs(near > min_frac):
        if e - s > 60:
            continue
        c = line_center(near + 1e-9, s, e) + off
        col = band[:, s:e].any(axis=1)
        if inward < 0:
            col = col[::-1]
        length = 0
        for v in col:
            if not v:
                break
            length += 1
        out.append((c, float(length + lw / 2 + 3)))
    return out


def fit(px, vals):
    """px = a + b * value, least squares; returns a, b, max misfit in pixels."""
    px = np.asarray(px, float)
    vals = np.asarray(vals, float)
    b, a = np.polyfit(vals, px, 1)
    mis = float(np.max(np.abs(px - (a + b * vals)))) if len(px) > 2 else 0.0
    return float(a), float(b), mis


def regular(cands, n):
    """From candidate tick positions, the n that form the most regular evenly spaced run."""
    cands = sorted(cands)
    best, best_err = None, np.inf
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            step = (cands[j] - cands[i]) / max(1, (n - 1))
            if step <= 0:
                continue
            pick = []
            err = 0.0
            for k in range(n):
                want = cands[i] + k * step
                d = [abs(c - want) for c in cands]
                q = int(np.argmin(d))
                pick.append(cands[q])
                err += d[q]
            if len(set(pick)) == n and err < best_err:
                best, best_err = pick, err
    return best


def grid_axis(tk, edge_a, edge_b, val_a, val_b, step, edge_tol=8.0, majors_only=False, first_major=None,
              all_major=False):
    """Calibrate one axis from its tick marks.
    tk: [(position, length)] from ticks(). The long ticks carry labels at multiples of `step`; the short
    ones (if any) lie halfway. edge_a, edge_b: the frame edges (pixels) whose end labels are val_a, val_b
    (matched labels). The long ticks are anchored on whichever edge lies on their grid; an edge that
    lies on the grid is also used as a mark. Returns a, b (pixel = a + b * value), misfit, description."""
    longest = max(t[1] for t in tk)
    if all_major:       # one kind of tick only, every one at a label step (short coloured ticks)
        majors, minors = sorted(c for c, _ in tk), []
    else:
        majors = sorted(c for c, ln in tk if ln > 0.75 * longest)
        minors = sorted(c for c, ln in tk if ln <= 0.75 * longest)
    # value change per increasing pixel; an unlabelled edge (value None) is given as the sign of
    # its direction: +1 if values grow from edge_a towards edge_b
    if isinstance(val_b, tuple):
        sgn = val_b[1] if edge_b > edge_a else -val_b[1]
        val_b = None
    else:
        sgn = 1 if (val_b - val_a) * (edge_b - edge_a) > 0 else -1
    pitch = float(np.median(np.diff(majors)))
    # tolerance for an edge to count as on the grid: a few pixels, or 6% of a step on coarse
    # rasters whose tick spacing itself wobbles by several pixels
    edge_tol = max(edge_tol, 0.06 * pitch) if edge_tol >= 0 else edge_tol
    used, note = [], []
    v0 = None
    for edge, v, nm in ((edge_a, val_a, "first"), (edge_b, val_b, "second")):
        if v is None:
            continue
        k = (edge - majors[0]) / pitch
        off = abs(k - round(k)) * pitch
        if off < edge_tol:
            used.append((edge, v))
            if v0 is None:
                v0 = v - sgn * step * round(k)
            note.append(f"{nm} edge on the grid")
        else:
            note.append(f"{nm} edge off the grid by {off:.0f} px, not used")
    if first_major is not None:
        # the caller matched the label under the first long tick
        if v0 is not None and abs(v0 - first_major) > 1e-9:
            raise ValueError(f"edge anchor gives {v0} for the first long tick, the label says {first_major}")
        v0 = first_major
        note.append(f"first long tick labelled {first_major:g}")
    if v0 is None:
        raise ValueError("neither frame edge lies on the tick grid")
    px = list(majors)
    vals = [v0 + sgn * step * round((c - majors[0]) / pitch) for c in majors]
    if not majors_only:
        for c in minors:
            k = (c - majors[0]) / pitch
            if abs(k - (np.floor(k) + 0.5)) < 0.1:
                px.append(c)
                vals.append(v0 + sgn * step * (np.floor(k) + 0.5))
    for e, v in used:
        px.append(e)
        vals.append(v)
    a, b, mis = fit(px, vals)
    return a, b, mis, f"{len(px)} marks ({', '.join(note)}), misfit {mis:.2f} px"


def hue_mask(img, name, min_sat=60, max_gray=235):
    f = np.asarray(img, dtype=float)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    s = f.max(axis=2) - f.min(axis=2)
    base = (s > min_sat) & (f.mean(axis=2) < max_gray)
    if name == "red":
        return base & (R > G + 40) & (R > B + 30)
    if name == "green":
        return base & (G > R + 30) & (G > B + 5)
    if name == "blue":
        return base & (B > R + 25) & (B > G + 20)
    if name == "cyan":
        return base & (B > R + 40) & (G > R + 40)
    if name == "black":
        return (f.mean(axis=2) < 90) & (s < 50)
    raise ValueError(name)


def blobs(mask, min_area, max_area=None, open_iter=0):
    m = ndi.binary_opening(mask, iterations=open_iter) if open_iter else mask
    lab, n = ndi.label(m)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        sub = lab[sl] == i
        area = int(sub.sum())
        if area < min_area or (max_area and area > max_area):
            continue
        rr, cc = np.nonzero(sub)
        out.append({"r": float(rr.mean() + sl[0].start), "c": float(cc.mean() + sl[1].start), "area": area,
                    "r0": sl[0].start, "r1": sl[0].stop, "c0": sl[1].start, "c1": sl[1].stop})
    return out


def follow(mask, r, c, dr, dc, gap=3, band=2, limit=100000):
    """Walk from (r, c) in direction (dr, dc) along a thin line in mask (checking +-band across);
    return the last position on the line (float), stopping after `gap` empty steps."""
    h, w = mask.shape
    last = None
    miss = 0
    k = 0
    rr, cc = float(r), float(c)
    while k < limit:
        rr += dr
        cc += dc
        ri, ci = int(round(rr)), int(round(cc))
        if not (0 <= ri < h and 0 <= ci < w):
            break
        if dr == 0:
            hit = mask[max(0, ri - band):ri + band + 1, ci].any()
        else:
            hit = mask[ri, max(0, ci - band):ci + band + 1].any()
        if hit:
            last = (rr, cc)
            miss = 0
        else:
            miss += 1
            if miss > gap:
                break
        k += 1
    return last
