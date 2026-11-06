"""Shared reader for Supplementary Fig. 1d (average spreading speed vs substrate stiffness,
one curve per clutch number). Every value comes from the rendered crop:

- x axis (log10): the major tick marks are found above the x-axis line; they are evenly spaced
  and, left to right, carry 10^-2, 10^-1, 1 and 10. The printed label "1" sits under the third
  of them. (The printed "10^-2" and "10^2" labels sit at the two ends of the axis, which do not
  fall on ticks; see the record's reading question about this.)
- y axis (linear): 0 is the centre of the x-axis line and 120 is the top end of the y-axis line,
  where the printed label "120" is centred. The label "0" is centred about 10 px above the axis
  line, so a calibration uncertainty of that size is carried into every interval.
- a curve is the set of pixels whose colour is nearest to its own line colour, sampled from the
  image at the left end of the axis, and is traced column by column from the left so labels in
  the same colour are not mistaken for it.
"""

import numpy as np

# reference colours of the five lines, as sampled in the crop at the left end of each curve
PALETTE = {
    "1000": (30, 28, 24),
    "100": (55, 83, 120),
    "50": (61, 103, 155),
    "25": (88, 136, 174),
    "5": (133, 162, 192),
    "axis": (90, 84, 79),
}
DECADES = [-2, -1, 0, 1]   # exponents of the major ticks, left to right
CAL_PX = 10.0              # calibration uncertainty on y, in pixels (label "0" vs axis-line centre)


def _runs(idx):
    if len(idx) == 0:
        return []
    cuts = np.nonzero(np.diff(idx) > 1)[0] + 1
    return [(g[0], g[-1]) for g in np.split(idx, cuts)]


def calibrate(img):
    g = img.astype(float).mean(axis=2)
    ink = g < 160
    H, W = g.shape
    rows = ink.sum(axis=1)
    lower = np.arange(H) > H // 2
    xrows = np.nonzero(lower & (rows > 0.6 * W))[0]
    xr0, xr1 = _runs(xrows)[0]                       # the x-axis line band
    cols = ink[: xr0].sum(axis=0)
    ycols = np.nonzero((np.arange(W) < W // 2) & (cols > 0.6 * xr0))[0]
    yc0, yc1 = _runs(ycols)[0]                       # the y-axis line band
    ytop = int(np.nonzero(ink[:, (yc0 + yc1) // 2])[0].min())
    # major ticks: narrow columns of ink rising >= 15 px above the x-axis band
    band = ink[xr0 - 16:xr0 - 2, :].sum(axis=0) >= 13
    band[: yc1 + 5] = False
    ticks = [(a + b) / 2 for a, b in _runs(np.nonzero(band)[0]) if 6 <= b - a + 1 <= 18]
    # keep the evenly spaced set: the first four consecutive ticks spaced 380-480 px apart
    sel = []
    for i in range(len(ticks) - len(DECADES) + 1):
        cand = ticks[i:i + len(DECADES)]
        if all(380 <= b - a <= 480 for a, b in zip(cand, cand[1:])):
            sel = cand
            break
    if len(sel) != len(DECADES):
        raise ValueError(f"could not find {len(DECADES)} evenly spaced major ticks: {ticks}")
    slope, icpt = np.polyfit(DECADES, sel, 1)
    misfit = float(np.max(np.abs(np.polyval([slope, icpt], DECADES) - np.array(sel))))
    y0 = (xr0 + xr1) / 2
    y120 = float(ytop)
    return {"col_of_log": lambda lx: icpt + slope * lx, "log_of_col": lambda c: (c - icpt) / slope,
            "px_per_unit": (y0 - y120) / 120.0, "y0": y0, "xband": (xr0, xr1), "yband": (yc0, yc1),
            "x_misfit_px": misfit, "ticks": sel}


def classify(img):
    """Index of the nearest palette colour for every inked pixel; -1 for paper."""
    f = img.astype(float)
    keys = list(PALETTE)
    d = np.stack([((f - np.array(PALETTE[k])) ** 2).sum(axis=2) for k in keys])
    cls = d.argmin(axis=0)
    cls[f.mean(axis=2) > 215] = -1
    return cls, keys


def trace(img, name, cal, min_run=5, max_jump=45):
    cls, keys = classify(img)
    target = keys.index(name)
    H, W = cls.shape
    start = cal["yband"][1] + 12
    end = W - 1
    centres = np.full(W, np.nan)
    halfw = np.full(W, np.nan)
    prev, thick = None, None
    for c in range(start, end):
        col = np.nonzero(cls[: cal["xband"][0], c] == target)[0]
        runs = [(a, b) for a, b in _runs(col) if b - a + 1 >= min_run]
        # a major tick mark rising from the axis line is not the curve
        if any(abs(c - t) <= 10 for t in cal["ticks"]):
            runs = [(a, b) for a, b in runs if b < cal["xband"][0] - 22]
        if not runs:
            continue
        if prev is None:
            a, b = max(runs, key=lambda r: r[1] - r[0])
        else:
            a, b = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - prev))
            if abs((a + b) / 2 - prev) > max_jump:
                continue
        if thick is not None and b - a + 1 > 1.6 * thick:   # a label of the same colour touches the line
            lo = max(a, int(prev - thick / 2))
            hi = min(b, int(prev + thick / 2))
            a, b = lo, hi
        centres[c] = (a + b + 1) / 2
        halfw[c] = (b - a + 1) / 2
        if thick is None and prev is not None:
            thick = b - a + 1
        prev = centres[c]
    return centres, halfw


def read_curve(img, at, name):
    cal = calibrate(img)
    centres, halfw = trace(img, name, cal)
    s = cal["px_per_unit"]
    out = []
    for x in at:
        c = cal["col_of_log"](np.log10(x))
        ci = int(round(c))
        win = centres[max(ci - 3, 0):ci + 4]
        how = ""
        if np.isfinite(win).any():
            row = float(np.nanmedian(win))
            hw = float(np.nanmax(halfw[max(ci - 3, 0):ci + 4]))
        else:
            # hidden in this column (e.g. by a tick mark): interpolate between the nearest traced
            # columns within 16 px on each side
            left = [k for k in range(ci - 1, ci - 17, -1) if np.isfinite(centres[k])]
            right = [k for k in range(ci + 1, min(ci + 17, len(centres))) if np.isfinite(centres[k])]
            if not left or not right:
                out.append({"x": x, "y": None, "note": "no pixels of this line's colour near this column "
                            "(line merged into the axis line or a label)"})
                continue
            kl, kr = left[0], right[0]
            row = float(centres[kl] + (centres[kr] - centres[kl]) * (c - kl) / (kr - kl))
            hw = float(max(halfw[kl], halfw[kr])) + abs(centres[kr] - centres[kl]) / 2
            how = f"interpolated between columns {kl} and {kr} (a tick mark hides the line); "
        # slope of the traced line, to carry the x-calibration uncertainty into y
        nb = centres[max(ci - 15, 0):ci + 16]
        ok = np.isfinite(nb)
        slope = 0.0
        if ok.sum() > 5:
            slope = abs(np.polyfit(np.nonzero(ok)[0], nb[ok], 1)[0])
        dpx = hw + CAL_PX + slope * (cal["x_misfit_px"] + 2.0)
        y = (cal["y0"] - row) / s
        out.append({"x": x, "y": y, "lo": y - dpx / s, "hi": y + dpx / s, "px": [c, row],
                    "px_lo": row + dpx, "px_hi": row - dpx,
                    "note": how + f"line half-width {hw:.1f} px, y calibration {CAL_PX:.0f} px, "
                            f"x ticks misfit {cal['x_misfit_px']:.1f} px"})
    return out
