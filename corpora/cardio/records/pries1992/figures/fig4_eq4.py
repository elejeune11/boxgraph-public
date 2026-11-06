"""Fig. 4 (p. 6): index of curvature C against tube diameter; the broken (dashed) line, Eq. 4.

Calibration: the scan is straightened by the tilt of its frame. x: every tick hanging below the
bottom frame line, taken in order from the left frame (the long ticks are the labelled decades
1, 10, 100, 1000; the short ones between are 2..9 times a decade; the last two are 2000 and
3000), log scale. y: the seven ticks left of the left frame line, labelled 1.5 to -1.5 in steps
of 0.5 from the top.

Which run is the dashed line, by region (seen on the page): on the steep descent (D 7-8.5) the
dashed line lies right of the thin line joining the data letters, so in a column it is the upper
of the runs between the letters at C = 1 and the zero line (or below the zero line); at D = 12
and 40 it is the uppermost run below the zero line (the letters E, J lie below it); at D = 18 it
is the lowest run (the thin line to the letter E lies above); from D = 200 up it is the run
nearest the row on which the long straight dashed segment lies (the row with most ink across
the right part of the panel), so the letters H, W, F, Ch, Br above and below it are not taken.
Diameters next to letters or where the two lines cross are not read.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _p92 as P  # noqa: E402

Y_LABELS = [1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -1.5]


def x_values(n):
    vals, dec = [], 1.0
    while len(vals) < n:
        for k in range(1, 10):
            vals.append(k * dec)
            if len(vals) == n:
                break
        dec *= 10
    return vals


def calibrate(image):
    st = P.Straight(image)
    d = st.d
    rows = P.long_rows(d, 0.6)
    cols = P.long_cols(d, 0.6)
    top, bottom = rows[0], rows[-1]
    left, right = cols[0], cols[-1]
    zero = [r for r in rows if r not in (top, bottom)][0]
    xt = P.ticks_off_hline(d, bottom, left[0] - 3, right[1] + 4, +1, min_len=12)
    xt = [t for t in xt if t[0] >= left[0] - 3]
    xa = P.Axis([c for c, _ in xt], x_values(len(xt)), log=True)
    yt = P.ticks_off_vline(d, left, top[0] - 20, bottom[1] + 20, -1, min_len=12)
    if len(yt) != len(Y_LABELS):
        raise ValueError(f"found {len(yt)} y ticks: {yt}")
    ya = P.Axis([r for r, _ in yt], Y_LABELS)
    return st, xa, ya, (top[1], bottom[0], left[1], right[0]), zero


def read(image, at):
    st, xa, ya, box, zero = calibrate(image)
    top, bottom, left, right = box
    one = ya.pixel(1.0)
    # the row of the long straight dashed segment: most ink across D = 300..2500, below the zero line
    c0, c1 = int(xa.pixel(300)), int(xa.pixel(2500))
    counts = st.d[zero[1] + 10:bottom - 10, c0:c1].sum(axis=1)
    band = zero[1] + 10 + int(np.argmax(counts))

    def rule(x):
        if x < 8.0:
            return lambda runs, c: next((r for r in runs if r[0] > one + 30 and not (zero[0] - 3 <= r[0] <= zero[1] + 3)), None)
        if x < 9.0:
            return lambda runs, c: next((r for r in runs if r[0] > zero[1] + 3), None)
        if x in (12.0, 40.0):
            return lambda runs, c: next((r for r in runs if r[0] > zero[1] + 3), None)
        if x == 18.0:
            return lambda runs, c: runs[-1] if runs and runs[-1][0] > zero[1] + 3 else None

        def near(runs, c):
            cand = [r for r in runs if abs((r[0] + r[1]) / 2 - band) <= 15]
            return min(cand, key=lambda r: abs((r[0] + r[1]) / 2 - band)) if cand else None
        return near

    out = []
    for a in at:
        x = float(a)
        if x < 200 and x not in (7.0, 7.5, 8.5, 12.0, 18.0, 40.0):
            out.append({"x": x, "y": None, "note": "next to data letters or where the thin line crosses: not read"})
            continue
        win = 12 if x < 9 else 25
        out += P.read_line(st, xa, ya, box, [x], rule(x), window=win)
    for o in out:
        o["note"] = o.get("note", "") + f"; x misfit {xa.misfit:.1f} px, y misfit {ya.misfit:.1f} px"
    return out
