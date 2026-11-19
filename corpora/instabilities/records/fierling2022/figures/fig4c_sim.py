"""Fig. 4c (PDF p. 8): the blue open squares 'simulations', rate of furrow deepening at t = 3 min
against AP position.

Calibration from the image:
- the frame (gnuplot, see _gp.frame); y: the bottom frame line carries the printed 0 and the inward
  ticks on the left frame line carry 3, 2, 1 (top to bottom); the top frame line is not labelled;
- x: the ticks point outwards, below the bottom frame line ('xtics out'): dark columns running from
  34 to 39 px below the frame line's lower edge (the markers at zero cover the ticks' upper part),
  matched left to right to -200, -100, 0, 100, 200. The bottom frame line, cut by the markers drawn
  over it, is the row of the lower half with the most dark pixels.
A square near x: its outline's two vertical sides are runs of blue (0, 0, 255), 55-95 px tall, in two
columns 68-85 px apart (the outer width is about 72 px; a side cut by a goldenrod line gives a
narrower pair, which is not taken), with matching top and bottom rows (within 5 px), centred within 40 px of x (a
steep line segment also gives tall runs, but no such pair). The widest such pairs are the outer
edges; the centre row is the middle of their runs, the centre column the middle of the two sides.
95% interval: 2 px plus the calibration misfit.
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _gp  # noqa: E402

XLAB = [-200.0, -100.0, 0.0, 100.0, 200.0]
BLUE = (0, 0, 255)


def _cal(image):
    fr = _gp.frame(image)
    _, _, blk = _gp.masks(image)
    # the markers are drawn over the bottom frame line ('set border behind') and cut it: the bottom
    # line is found where the left frame line ends; its rows are those of the dark run along the
    # frame's first 20 columns inside the left line
    c = int(fr["left"])
    a, b = max(_gp.column_runs(blk[:, c]), key=lambda q: q[1] - q[0])
    seg = blk[:, int(fr["left_in"]) + 1:int(fr["left_in"]) + 21].all(axis=1)
    rows = [r for r in range(b - 20, b + 1) if seg[r]]
    fr["bottom"] = (rows[0] + rows[-1]) / 2.0
    fr["bottom_in"] = rows[0] - 1
    ticks = _gp.y_ticks(image, fr)
    if not ticks:
        raise ValueError(f"no y ticks; frame {fr}")
    yt = sorted(_gp.major(ticks))
    if len(yt) != 3:
        raise ValueError(f"found {len(yt)} y ticks, expected 3")
    ym = [(fr["bottom"], 0.0)] + list(zip(yt, [3.0, 2.0, 1.0]))
    ay, by, my = _gp.fit(ym)
    r0 = int(fr["bottom"] + fr["half"] + 2)
    # the markers at zero reach about 32 px below the frame line and cover the ticks' upper part:
    # the ticks (about 40 px long) are tested 34 to 39 px below the frame
    cols = [c for c in range(blk.shape[1]) if blk[r0 + 34:r0 + 39, c].all()]
    groups = []
    for c in cols:
        if groups and c - groups[-1][-1] <= 2:
            groups[-1].append(c)
        else:
            groups.append([c])
    xt = [(g[0] + g[-1]) / 2.0 for g in groups if len(g) < 30]
    if len(xt) != len(XLAB):
        prof = [(int(c), int(blk[r0:r0 + 60, c].sum())) for c in range(600, 640, 4)]
        raise ValueError(f"found {len(xt)} x ticks, expected {len(XLAB)}; r0 {r0}; fr {fr}; {prof}")
    ax, bx, mx = _gp.fit(list(zip(xt, XLAB)))
    return fr, ay, by, my, ax, bx, mx


def read(image, at):
    fr, ay, by, my, ax, bx, mx = _cal(image)
    m = _gp._inside(_gp.colour_mask(image, BLUE, 60), fr)
    mm = m | _gp._inside(_gp.colour_mask(image, (255, 192, 32), 60), fr)
    out = []
    for x in at:
        c0 = int(round((float(x) - ax) / bx))
        cand = []
        for c in range(c0 - 90, c0 + 91):
            # the MuVi markers and lines (goldenrod) are drawn over the squares: a side runs on
            # through them, if at least 40% of it is blue
            for r in set(_gp.column_runs(mm[:, c])) | set(_gp.column_runs(m[:, c])):
                if 55 <= r[1] - r[0] + 1 <= 95 and m[r[0]:r[1] + 1, c].sum() >= 0.4 * (r[1] - r[0] + 1):
                    cand.append((c, r))
        cand.sort()
        # a square: two tall runs 60-85 px apart whose top and bottom rows match (a steep line
        # segment also gives tall runs, but not a matching pair at the square's width)
        pairs = [(L, R) for L in cand for R in cand
                 if 68 <= R[0] - L[0] <= 85 and abs(L[1][0] - R[1][0]) <= 5 and abs(L[1][1] - R[1][1]) <= 5
                 and abs((L[0] + R[0]) / 2.0 - c0) < 40]
        if not pairs:
            out.append({"x": float(x), "y": None, "note": "square outline not found"})
            continue
        width = max(R[0] - L[0] for L, R in pairs)
        outer = [(L, R) for L, R in pairs if R[0] - L[0] >= width - 2]
        row = float(np.median([(L[1][0] + L[1][1] + R[1][0] + R[1][1]) / 4.0 for L, R in outer]))
        col = float(np.median([(L[0] + R[0]) / 2.0 for L, R in outer]))
        sides = [outer[0][0], outer[0][1]]
        e = 2.0 + max(my, 0.5)
        y = ay + by * row
        lo, hi = sorted([ay + by * (row + e), ay + by * (row - e)])
        out.append({"x": float(x), "y": float(y), "lo": float(lo), "hi": float(hi), "px": [col, row],
                    "note": f"square sides at columns {sides[0][0]}-{sides[-1][0]}; square centre at x = "
                            f"{ax + bx * col:.1f} um; y 4 marks misfit {my:.2f} px, x 5 ticks misfit {mx:.2f} px"})
    return out
