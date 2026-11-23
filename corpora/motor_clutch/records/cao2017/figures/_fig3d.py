"""Reading code for Fig. 3D of cao2017 (PDF p. 3, adapted from ref. 16): fibre recruitment (a.u.),
box plots for the soft, stiff and soft-weld networks. A blurred grey raster.

Everything is found in the image:
  y axis    the left spine is the longest vertical run of ink in the left quarter; the ticks are
            the ink rows a little left of it, each at its darkness-weighted centre, matched in order
            to the printed labels 6, 4, 2, 0 (the only paper values used). A linear fit gives the
            calibration and its misfit (largest residual, at least half a pixel).
  boxes     the category ticks below the x axis give each box's centre column. Two vertical profiles
            are taken beside the centre (the whisker stem runs along the centre): one through the
            box but outside the whisker caps, whose three lowest ink runs are the third quartile,
            the median and the first quartile; one through the caps, whose five lowest ink runs are
            the upper cap, the box (three) and the lower cap. Lines are the peaks of the profile
            (prominence over 15 grey levels), each at the darkness-weighted centre of its upper
            half, so that close lines (the narrow stiff box) stay apart.
  value     the median; the whisker ends are returned as the error bar (what they show is not
            stated); the quartiles are given in the note.

Intervals (95%): half the median line's width, the calibration misfit, and one pixel.
"""
import numpy as np


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def _runs(dark, thr):
    """Ink runs of a darkness profile: (centre, width, peak), centre darkness-weighted."""
    out = []
    for g in _groups(np.where(dark > thr)[0], gap=2):
        lo, hi = max(g[0] - 2, 0), min(g[-1] + 3, len(dark))
        w = np.clip(dark[lo:hi], 0, None)
        out.append((float((np.arange(lo, hi) * w).sum() / w.sum()) + 0.5, int(g[-1] - g[0] + 1), float(dark[g].max())))
    return out


def _lines(dark, prominence=15.0):
    """Lines crossed by a darkness profile: each peak, its centre the darkness-weighted centroid
    of the profile above half the peak's height over its base, and that width."""
    from scipy.signal import find_peaks
    peaks, props = find_peaks(dark, prominence=prominence, distance=8)
    out = []
    for p, base in zip(peaks, props["prominences"]):
        half = dark[p] - 0.5 * base
        lo = p
        while lo > 0 and dark[lo - 1] > half:
            lo -= 1
        hi = p
        while hi < len(dark) - 1 and dark[hi + 1] > half:
            hi += 1
        w = dark[lo:hi + 1] - half
        out.append((float((np.arange(lo, hi + 1) * w).sum() / w.sum()) + 0.5, int(hi - lo + 1), float(dark[p])))
    return out


def read(image, at):
    g = image.astype(float).mean(axis=2)
    dark = 255.0 - g
    H, W = g.shape
    ink = dark > 60
    best = (0, 0, 0, 0)
    for c in range(int(0.25 * W)):
        for grp in _groups(np.where(ink[:, c])[0], gap=2):
            if grp[-1] - grp[0] + 1 > best[0]:
                best = (grp[-1] - grp[0] + 1, c, grp[0], grp[-1])
    n, c, r0, r1 = best
    cols = [cc for cc in range(max(c - 20, 0), c + 20) if ink[r0 + n // 4:r1 - n // 4, cc].mean() > 0.9]
    c0, c1 = min(cols), max(cols)
    probe = c0 - 25
    prof = dark[:, probe - 2:probe + 3].mean(axis=1)
    ticks = [t for t, w, p in _runs(prof, 40) if w < 40]
    labels = np.array([6, 4, 2, 0], float)
    if len(ticks) != len(labels):
        raise ValueError(f"found {len(ticks)} y ticks for {len(labels)} labels")
    b, a = np.polyfit(labels, ticks, 1)
    misfit = max(float(np.max(np.abs(np.array(ticks) - (a + b * labels)))), 0.5)

    def val(p):
        return float((p - a) / b)

    axis_row = a  # the 0 tick is the x axis's own extension
    band = dark[int(axis_row + 20):int(axis_row + 50), :]
    tcols = [cc for cc in range(c1 + 20, W) if band[:, cc].mean() > 60]
    centres = [(gg[0] + gg[-1]) / 2.0 + 0.5 for gg in _groups(tcols) if len(gg) < 40]
    if len(centres) != 3:
        raise ValueError(f"found {len(centres)} category ticks, want 3")
    out = []
    for k, cx in enumerate(centres):
        ci = int(round(cx))
        top_limit = int(axis_row) - 30
        pa = dark[:top_limit, ci + 145:ci + 156].mean(axis=1)
        pb = dark[:top_limit, ci + 75:ci + 86].mean(axis=1)
        ra = _lines(pa)
        rb = _lines(pb)
        if len(ra) < 3 or len(rb) < 5:
            out.append({"x": float(k + 1), "y": None, "note": f"found {len(ra)} box lines and {len(rb)} whisker lines"})
            continue
        q3, med, q1 = [r for r in ra[-3:]]
        cap_hi, cap_lo = rb[-5], rb[-1]
        e = 0.5 * med[1] + misfit + 1.0
        y = val(med[0])
        v1, v2 = val(med[0] - e), val(med[0] + e)
        pp = (2.5 + misfit) / abs(b)
        hi_v, lo_v = val(cap_hi[0]), val(cap_lo[0])
        out.append({"x": float(k + 1), "y": y, "lo": min(v1, v2), "hi": max(v1, v2), "px": [cx, med[0]],
                    "px_lo": cap_hi[0], "px_hi": cap_lo[0],
                    "bar_lo": lo_v, "bar_hi": hi_v, "bar_lo_outer": lo_v - pp, "bar_hi_outer": hi_v + pp,
                    "note": f"median line ({med[1]} px); box (quartiles) {val(q1[0]):.3f} to {val(q3[0]):.3f}; "
                            f"whisker caps {lo_v:.3f} to {hi_v:.3f}; y misfit {misfit:.1f} px ({len(ticks)} ticks)"})
    return out
