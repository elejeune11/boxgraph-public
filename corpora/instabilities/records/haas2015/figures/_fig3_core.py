"""Shared reading code for the second reading of Fig. 3(g) and 3(h) (PDF p. 4).

Everything is found in the rendered crop:
- dark = grey level below 128.
- y axis: the column with the longest dark run; x axis: the row with the longest dark run (in
  panel (h) this is the line y = 0). Axis line width lw: the number of neighbouring columns of
  the y axis whose longest run is at least half as long.
- x ticks: short dark runs (at most 3 lw wide) crossing the x axis row, dark both above and below
  it, away from the thick curve. They lie on a regular grid starting at the y axis (x = 0); the
  labels 5, 10 (and 15) are under every third tick, so the ticks are 5/3 apart. The x scale is
  the least-squares line through the y axis and the ticks at k * 5/3; its largest residual is the
  x misfit.
- y ticks: short dark runs crossing the y axis column, dark on both sides of it. The ticks with
  digits to their left are the labelled ones, matched in order from the top with the values the
  caller gives (those printed on the figure). The y scale is fitted through them; the largest
  distance of any tick from the regular grid of that spacing is the y misfit.
- thick solid curve: the largest connected part of the pixels deeper than 0.7 of the largest
  distance-to-background in the crop (the curve is by far the thickest line; axes, ticks, dashes
  and digits are thinner). Its centre row in a column is the middle of that core.
- dashed line (panel (h)): the dark runs of at most 4 lw that are not part of the curve or of the
  axes, between the top of the y axis and the x axis, pooled over +-60 columns.
Interval for each value: 2 px + a quarter of the core's run length in the column (curves that
are steep there are less sharply located), in y units, plus the y misfit, plus the local slope
times the x misfit.
"""
import numpy as np
from scipy import ndimage as ndi


def _groups(idx):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= 1:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def _longest(v):
    best = cur = 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def calibrate(image, y_labels, x_step=5.0 / 3.0):
    img = np.asarray(image).astype(float)
    dk = (img.mean(axis=2) if img.ndim == 3 else img) < 128
    H, W = dk.shape
    colrun = np.array([_longest(dk[:, c]) for c in range(W)])
    rowrun = np.array([_longest(dk[r, :]) for r in range(H)])
    c_axis = int(np.argmax(colrun))
    r_axis = int(np.argmax(rowrun))
    near = np.where(colrun[max(c_axis - 15, 0): c_axis + 16] >= 0.5 * colrun[c_axis])[0]
    lw = max(2, len(near))
    r_top = int(np.where(dk[:, c_axis])[0].min()) + 3 * lw   # below the arrow head

    edt = ndi.distance_transform_edt(dk)
    emax = float(edt.max())
    lab, n = ndi.label(edt > 0.7 * emax)
    sizes = ndi.sum(np.ones_like(edt), lab, range(1, n + 1))
    core = lab == (int(np.argmax(sizes)) + 1)
    curve_zone = ndi.distance_transform_edt(~core) < 0.3 * emax + 6   # the whole thick curve and its rim

    # x ticks
    a, b = 2 * lw, 4 * lw
    above = dk[r_axis - b: r_axis - a, :].mean(0) > 0.5
    below = dk[r_axis + a: r_axis + b, :].mean(0) > 0.5
    zone = curve_zone[r_axis - b: r_axis + b, :].any(0)
    cols = np.where(above & below & ~zone)[0]
    cols = cols[cols > c_axis + 3 * lw]
    cand = [float(np.mean(g)) for g in _groups(cols) if len(g) <= 3 * lw]
    d = np.diff([c_axis] + cand)
    sp = float(np.median(d))
    k = np.round((np.array(cand) - c_axis) / sp)
    ok = np.abs((np.array(cand) - c_axis) / sp - k) < 0.15
    xt, kt = np.array(cand)[ok], k[ok]
    xv = np.concatenate([[0.0], kt * x_step])
    xc = np.concatenate([[c_axis], xt])
    cpu, c0 = np.polyfit(xv, xc, 1)
    xmis = float(np.max(np.abs(c0 + cpu * xv - xc)) / cpu)

    # y ticks
    left = dk[:, c_axis - b: c_axis - a].mean(1) > 0.5
    right = dk[:, c_axis + a: c_axis + b].mean(1) > 0.5
    rows = np.where(left & right)[0]
    rows = rows[rows > r_top]
    yt = np.array([float(np.mean(g)) for g in _groups(rows) if len(g) <= 3 * lw])
    ysp = float(np.median(np.diff(yt)))
    # keep the ticks on the regular grid through the tick that puts the most others on it
    def _on(r):
        q = (yt - r) / ysp
        return int(np.sum(np.abs(q - np.round(q)) < 0.1))
    ref = max(yt, key=_on)
    kk = (yt - ref) / ysp
    yt = yt[np.abs(kk - np.round(kk)) < 0.1]
    lab_rows = []
    for t in yt:
        win = dk[int(t - ysp / 3): int(t + ysp / 3), int(c_axis - 1.2 * ysp): int(c_axis - 0.35 * ysp)]
        if win.sum() > 4 * lw * lw:
            lab_rows.append(t)
    assert len(lab_rows) == len(y_labels), (lab_rows, list(yt))
    slope, icpt = np.polyfit(np.array(lab_rows), np.array(y_labels, dtype=float), 1)
    # misfit: distance of every tick from the regular grid fitted through all ticks, in y units
    k = np.round((yt - yt[0]) / ysp)
    gsp, g0 = np.polyfit(k, yt, 1)
    ymis = float(np.max(np.abs(g0 + gsp * k - yt)) * abs(slope))
    ymis = max(ymis, float(np.max(np.abs(icpt + slope * np.array(lab_rows) - np.array(y_labels)))))
    return dict(dk=dk, core=core, curve_zone=curve_zone, c_axis=c_axis, r_axis=r_axis, lw=lw, r_top=r_top,
                c0=float(c0), cpu=float(cpu), xmis=xmis, a=float(icpt), b=float(slope), ymis=ymis,
                nxt=len(xt), nyt=len(yt), nlab=len(lab_rows))


def _core_centre(cal, c):
    r = np.where(cal["core"][:, c])[0]
    if len(r) == 0:
        return None
    g = max(_groups(r), key=len)
    return (g[0] + g[-1]) / 2.0, len(g)


def _note(cal, what):
    return (f"{what}; x: y axis + {cal['nxt']} ticks 5/3 apart, 1 unit = {cal['cpu']:.1f} px, misfit {cal['xmis']:.4f}; "
            f"y: {cal['nlab']} labelled of {cal['nyt']} ticks, misfit {cal['ymis']:.4f}")


def read_curve(image, at, y_labels, what):
    cal = calibrate(image, y_labels)
    out = []
    for x in at:
        col = cal["c0"] + cal["cpu"] * x
        ci = int(round(col))
        got = [_core_centre(cal, c) for c in range(ci - 3, ci + 4)]
        got = [g for g in got if g is not None]
        if len(got) < 5:
            out.append({"x": float(x), "y": None, "note": f"{what}: the curve's core is not in this column"})
            continue
        row = float(np.median([g[0] for g in got]))
        ln = float(np.median([g[1] for g in got]))
        y = cal["a"] + cal["b"] * row
        dc = 12
        s1, s2 = _core_centre(cal, ci - dc), _core_centre(cal, ci + dc)
        slope = 0.0 if s1 is None or s2 is None else abs(s2[0] - s1[0]) / (2 * dc) * cal["cpu"] * abs(cal["b"])
        half_px = 2.0 + 0.25 * ln
        dy = abs(cal["b"]) * half_px + cal["ymis"] + slope * cal["xmis"]
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy), "px": [float(col), row],
                    "px_lo": row - half_px, "px_hi": row + half_px, "note": _note(cal, what)})
    return out


def read_dashed(image, at, y_labels, what, half=60):
    cal = calibrate(image, y_labels)
    dk, lw = cal["dk"], cal["lw"]
    out = []
    for x in at:
        col = cal["c0"] + cal["cpu"] * x
        ci = int(round(col))
        centres, thick = [], []
        for c in range(ci - half, ci + half + 1):
            colm = dk[:, c] & ~cal["curve_zone"][:, c]
            colm[: cal["r_top"]] = False
            colm[cal["r_axis"] - 3 * lw:] = False
            for g in _groups(np.where(colm)[0]):
                if 0.5 * lw <= len(g) <= 4 * lw:
                    centres.append((g[0] + g[-1]) / 2.0)
                    thick.append(len(g))
        if len(centres) < 10:
            out.append({"x": float(x), "y": None, "note": f"{what}: no dash near this position"})
            continue
        row = float(np.median(centres))
        keep = np.abs(np.array(centres) - row) <= 2 * lw
        row = float(np.median(np.array(centres)[keep]))
        half_px = 2.0 + 0.5 * float(np.ptp(np.array(centres)[keep]))
        y = cal["a"] + cal["b"] * row
        dy = abs(cal["b"]) * half_px + cal["ymis"]
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy), "px": [float(col), row],
                    "px_lo": row - half_px, "px_hi": row + half_px,
                    "note": _note(cal, what) + f"; dash thickness {float(np.median(thick)):.0f} px"})
    return out
