"""Reading code for Fig. S1: five flow-cytometry histograms drawn as coloured lines (a raster image)
in a framed plot with a logarithmic x axis (decades 10^0 to 10^3 with minor ticks) and a linear y axis.

Everything is found in the rendered crop; a reading file supplies the printed y tick labels it matched
(bottom to top, the unlabelled tick at the x axis left out), the printed decade labels (as their
exponents), the curve's colour and the legend region not searched.

At a given x the curve's pixels in its colour form a vertical run (long where the curve is steep);
the value is the run's centre and the interval half the run plus 2 px and the tick misfit. Where
another curve is drawn over this one the colour is missing and nothing is reported at that x.
"""

import numpy as np

import _lt
import _s4


def colour_mask(img, colour):
    r, g, b = (img[..., i].astype(int) for i in range(3))
    if colour == "red":
        return (r > 220) & (g < 80) & (b < 80)
    if colour == "blue":
        return (r < 60) & (g > 80) & (g < 160) & (b > 190)
    if colour == "green":
        return (g > 120) & (g - r > 60) & (b < 80)
    if colour == "brown":
        return (r > 120) & (r < 175) & (g > 35) & (g < 80) & (b < 30)
    if colour == "magenta":
        return (r > 180) & (g < 60) & (b > 150)
    raise ValueError(colour)


def _x_ticks(black, ycols, xrows):
    """The x ticks below the axis: (centre column, length) of each."""
    r1 = xrows[1]
    W = black.shape[1]
    down = np.zeros(W, int)
    for c in range(ycols[0], W):
        k = 0
        while r1 + 1 + k < black.shape[0] and black[r1 + 1 + k, c]:
            k += 1
        down[c] = k
    groups = [(s, e) for s, e in _lt._runs(down >= 8) if e - s >= 2]
    return [((s + e - 1) / 2, int(down[s:e].max())) for s, e in groups]


def calibrate(img, y_labels, decades):
    black = _lt.mask_for(img, "black")
    ycols, xrows = _lt.find_axes(black)
    rows = sorted(_s4._y_ticks(black, ycols, xrows))  # top to bottom
    if len(rows) == len(y_labels) + 1:
        rows = rows[:-1]  # the unlabelled tick at the x axis
    ya = _lt.YAxis(rows, [list(y_labels)])
    ticks = _x_ticks(black, ycols, xrows)
    longest = max(n for _, n in ticks)
    major = [c for c, n in ticks if n >= 0.8 * longest]
    if len(major) < len(decades):
        raise ValueError(f"found {len(major)} major x ticks at {[round(c) for c in major]}, expected {len(decades)}")
    major = sorted(major)[:len(decades)]  # the decades labelled; any later major tick is unlabelled
    xa = _lt.Linear(list(zip(major, decades)))  # log10(x) against column
    # check: the minor ticks of the labelled decades should sit at log10(2..9)
    minor = [c for c, n in ticks if n < 0.8 * longest and major[0] < c < major[-1]]
    expect = [xa.px(d + np.log10(k)) for d in decades[:-1] for k in range(2, 10)]
    mis = max((min(abs(c - e) for c in minor) for e in expect), default=0.0)
    return black, ycols, xrows, ya, xa, mis


def read_curve(image, at, y_labels, decades, colour, exclude=()):
    black, ycols, xrows, ya, xa, minor_mis = calibrate(image, y_labels, decades)
    seg = ya.segs[0]
    H, W = black.shape
    m = colour_mask(image, colour)
    m[:, :ycols[1] + 2] = False
    m[xrows[0] - 1:, :] = False
    for (fx0, fy0, fx1, fy1) in exclude:
        m[int(fy0 * H):int(fy1 * H), int(fx0 * W):int(fx1 * W)] = False
    per_y = abs(seg.b)
    out = []
    for x in at:
        c = int(round(xa.px(np.log10(x))))
        runs = [(s, e) for s, e in _lt._runs(m[:, c]) if e - s >= 2]
        if not runs:
            continue  # hidden under another curve here: not read
        # one curve is one run; a second run (a stray pixel group of the same colour) is left out
        s, e = max(runs, key=lambda se: se[1] - se[0])
        row = (s + e - 1) / 2
        # the x calibration is good to a few pixels (the decade ticks fit to 2 px; see the note for the
        # minor ticks): the interval covers the curve over 3 px either side
        lo_r, hi_r = s, e
        for cc in range(c - 3, c + 4):
            rr = [(a, b) for a, b in _lt._runs(m[:, cc]) if b - a >= 2 and a <= e + 10 and b >= s - 10]
            if rr:
                lo_r = min(lo_r, min(a for a, _ in rr))
                hi_r = max(hi_r, max(b for _, b in rr))
        half = max(row - lo_r, hi_r - 1 - row) + 2 + ya.misfit_px
        y = float(seg.value(row))
        out.append({"x": x, "y": y, "lo": y - half * per_y, "hi": y + half * per_y,
                    "px": [float(c), row], "px_lo": row - half, "px_hi": row + half,
                    "note": f"{colour} run rows {s}-{e - 1} at column {c}; minor ticks within {minor_mis:.1f} px of log10(2..9)"})
    return out
