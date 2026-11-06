"""Shared reading code for Fig. 6 (p. 7): relative apparent viscosity against tube diameter, heavy
lines for fixed tube hematocrit (0.6 solid, 0.45 broken, 0.2 solid, top to bottom) and thin lines
for fixed discharge hematocrit (same order).

Calibration from the image (crop straightened by the tilt of its bottom axis):
- x: the ticks hanging below the bottom frame line, in order from the left frame, which is the
  labelled 2; then 3..9, 10 (long tick, labelled), 20..90, 100 (long, labelled), ..., 1000 (long,
  labelled), 2000; log scale. The ticks above the top frame line agree within 2 px.
- y: the nine ticks left of the left frame line, every 0.5 from 5 (top, labelled 5) to 1
  (labelled 1); the ticks right of the right frame line agree within 1 px.

A curve is chosen by thickness and rank: in each column the runs are split into heavy (at least
10 px tall) and thin (at most 9 px); only columns showing exactly three runs of the kind are used,
and the curve is the k-th of them from the top. Where the thin lines merge into the heavy ones
(large diameters) or the six lines crowd (the minimum, D < 10 um), the columns do not show three
runs of each kind and nothing is read.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _p92 as P  # noqa: E402

Y_LABELS = [5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0]


def x_values(n):
    out, k, dec = [], 2, 1.0
    while len(out) < n:
        out.append(k * dec)
        k += 1
        if k == 10:
            k, dec = 1, dec * 10
    return out


def calibrate(image):
    st = P.Straight(image)
    d = st.d
    bottom = P.long_rows(d, 0.6)[-1]
    left = P.long_cols(d, 0.6)[0]
    xt = P.ticks_off_hline(d, bottom, left[0] - 3, d.shape[1], +1, min_len=8)
    xa = P.Axis([c for c, _ in xt], x_values(len(xt)), log=True)
    yt = P.ticks_off_vline(d, left, 50, bottom[1] + 15, -1, min_len=8)
    if len(yt) != len(Y_LABELS):
        raise ValueError(f"found {len(yt)} y ticks: {yt}")
    ya = P.Axis([r for r, _ in yt], Y_LABELS)
    right = P.long_cols(d, 0.3, c0=d.shape[1] - 120)[-1]
    top = int(min(r for r, _ in yt)) - 230
    return st, xa, ya, (max(top, 5), bottom[0], left[1], right[0])


def read(image, at, heavy, rank, label):
    st, xa, ya, box = calibrate(image)

    def choose(runs, c):
        # specks (under 3 px) and anything within 20 px of the bottom frame are not lines
        runs = [r for r in runs if r[1] - r[0] + 1 >= 3 and r[1] < box[1] - 20]
        kind = [r for r in runs if (r[1] - r[0] + 1 >= 10) == heavy]
        if len(kind) != 3:
            return None
        return kind[rank]

    out = P.read_line(st, xa, ya, box, [float(a) for a in at], choose, window=25)
    for o in out:
        o["note"] = o.get("note", "") + f"; {label}; x misfit {xa.misfit:.1f} px, y misfit {ya.misfit:.1f} px"
    return out
