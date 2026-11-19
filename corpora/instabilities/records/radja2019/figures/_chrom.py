# Figs. S1 and S2 (PDF pp. 22-23): GC chromatograms (abundance against retention time), embedded
# as raster screenshots. Reads the apex of every peak of the trace that rises above a threshold.
#
# Calibration, from the image: the axis lines are the longest dark column (left part) and the
# longest dark row (lower part). The printed tick labels are found as blocks of dark pixels left
# of the y axis (one block of rows per label) and below the x axis (one block of columns per
# label, characters closer than `gap` px joined); each label's centre is matched, in order, to
# the printed values, and a straight line is fitted through them. The labels are centred on
# their ticks in these instrument plots; the misfit of the fit is part of the interval.
#
# Trace: in each column, from the baseline (the x axis row) upward, the run of dark pixels
# connected to the baseline (gaps of up to 2 px bridged) is the trace; its top is the signal.
# The peak labels printed above the trace are not connected to it and are not read.
import numpy as np
from scipy import ndimage


def _dark(image, thr=110):
    g = image[..., :3].astype(float).mean(-1)
    return g < thr


def _runs(v, gap=0):
    d = np.diff(np.r_[0, v.astype(int), 0])
    rs = list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))
    out = []
    for s, e in rs:
        if out and s - out[-1][1] <= gap:
            out[-1] = (out[-1][0], e)
        else:
            out.append((s, e))
    return out


def calibrate(image, x_labels, y_labels, x_gap, min_w=70):
    dk = _dark(image)
    h, w = dk.shape
    ycol = int(np.argmax(dk[:, : w // 3].sum(0)))
    xrow = h // 2 + int(np.argmax(dk[h // 2:, :].sum(1)))
    # y labels: dark rows in the band left of the axis (leave the tick marks out)
    band = dk[: xrow - 5, : max(ycol - 25, 1)]
    rows = _runs(band.sum(1) > 0, gap=3)
    rows = [(s, e) for s, e in rows if 12 <= e - s <= 60]
    # the axis title ("Abundance") sits above the top label: keep the last len(y_labels) blocks
    rows = rows[-len(y_labels):]
    if len(rows) != len(y_labels):
        raise ValueError(f"{len(rows)} y labels found, {len(y_labels)} expected")
    yc = [(s + e - 1) / 2 for s, e in rows]
    # x labels: dark columns in the band below the axis, right of the y axis
    band = dk[xrow + 15: xrow + 90, ycol - 40:]
    cols = _runs(band.sum(0) > 0, gap=x_gap)
    # a label is a block at least `min_w` px wide (shorter blocks are stray peak-label text)
    cols = [(s + ycol - 40, e + ycol - 40) for s, e in cols if e - s >= min_w]
    cols = cols[: len(x_labels)]
    if len(cols) != len(x_labels):
        raise ValueError(f"{len(cols)} x labels found, {len(x_labels)} expected")
    xc = [(s + e - 1) / 2 for s, e in cols]
    fx = np.polyfit(xc, x_labels, 1)
    fy = np.polyfit(yc, y_labels, 1)
    mis_x = float(np.max(np.abs(np.polyval(fx, xc) - np.array(x_labels))))
    mis_y = float(np.max(np.abs(np.polyval(fy, yc) - np.array(y_labels))))
    return dict(fx=fx, fy=fy, mis_x=mis_x, mis_y=mis_y, ycol=ycol, xrow=xrow, top=min(yc))


def trace_top(image, cal):
    dk = _dark(image, 170)  # the thin trace is anti-aliased grey
    xrow, ycol = cal["xrow"], cal["ycol"]
    # the trace's baseline lies on the axis line: the trace is the connected set of dark pixels
    # (gaps of one pixel closed) that contains the axis line
    dk = ndimage.binary_dilation(dk, structure=np.ones((3, 3), bool))
    lab, _ = ndimage.label(dk, structure=np.ones((3, 3), bool))
    ids = lab[xrow, ycol + 10: ycol + 400]
    tid = np.bincount(ids[ids > 0]).argmax()
    tr = lab == tid
    tops = {}
    for c in range(ycol + 12, dk.shape[1]):
        rows = np.flatnonzero(tr[: xrow + 1, c])
        if len(rows):
            tops[c] = int(rows.min()) + 1  # undo the dilation
    return tops


def read_peaks(image, x_labels, y_labels, x_gap, min_height, clip_top_row=None, exclude=()):
    """`exclude`: retention-time windows (lo, hi) where a printed peak label touches the trace on
    the image, so the trace cannot be told from the label; a peak found there is reported
    without a value."""
    cal = calibrate(image, x_labels, y_labels, x_gap)
    fx, fy = cal["fx"], cal["fy"]
    tops = trace_top(image, cal)
    cs = np.array(sorted(tops))
    t = np.array([tops[c] for c in cs], dtype=float)
    sig = np.polyval(fy, t)  # abundance at the top of the trace
    base = float(np.polyval(fy, cal["xrow"]))
    # local maxima of the signal over a window of 31 columns, higher than min_height above the axis
    mx = ndimage.maximum_filter1d(sig, 31)
    cand = np.flatnonzero((sig == mx) & (sig - base > min_height))
    out = []
    used = []
    dy = abs(fy[0])
    for i in cand:
        c = cs[i]
        if any(abs(c - u) <= 15 for u in used):
            continue
        # columns of the plateau at the apex: take its centre
        same = [j for j in range(max(i - 15, 0), min(i + 16, len(sig))) if sig[j] == sig[i]]
        cc = float(np.mean(cs[same]))
        used.append(c)
        x = float(np.polyval(fx, cc))
        y = float(sig[i])
        ex = cal["mis_x"] + abs(fx[0]) * 3
        ey = cal["mis_y"] + dy * 4  # line thickness and the blurred raster
        top_row = float(t[i])
        # left out (no point returned): peaks where a printed label touches the trace, and
        # peaks that run off the top of the plot (their height is not shown)
        if any(lo <= x <= hi for lo, hi in exclude):
            continue
        if top_row <= cal["top"] - 5 or (clip_top_row is not None and top_row <= clip_top_row):
            continue
        out.append({"x": round(x, 3), "y": y, "lo": y - ey, "hi": y + ey, "px": [cc, top_row],
                    "note": f"retention time {x:.2f} +/- {ex:.2f} min; calibration misfit x {cal['mis_x']:.3f} min, y {cal['mis_y']:.3g}"})
    out.sort(key=lambda d: d["x"])
    return out
