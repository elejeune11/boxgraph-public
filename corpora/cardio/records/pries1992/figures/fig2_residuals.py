"""Fig. 2 inset (p. 4): residuals of the measured eta_rel (hematocrit 0.45) from Eq. 2 against tube
diameter, one filled circle per data point.

Calibration from the image (crop straightened by the tilt of its frame; the crop also holds part
of the main panel's right frame, so only its left 2,100 columns are searched):
- x: the 30 ticks hanging below the inset's bottom frame line, in order from its left frame:
  1 (labelled), 2..9, 10 (labelled), 20..90, 100, ..., 1000 (labelled), 2000, 3000; log scale;
- y: the seven ticks left of the left frame line and the seven right of the right one, 0.6 at
  the top to -0.6 at the bottom frame in steps of 0.2 (labelled 0.6, 0.2, -0.2, -0.6); y is
  interpolated between the left and right fits by column.
Markers: what survives an opening with a disk of radius 8 px inside the frame (the zero line and
the frame do not), split into disks greedily as in _fig3.read_filled.
"""

import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig3 as F3  # noqa: E402
import _fig5 as F5  # noqa: E402
import _p92 as P  # noqa: E402


class _Inset:
    def __init__(self, image):
        self.st = st = P.Straight(image)
        d = st.d
        self.bottom = P.long_rows(d, 0.6, c0=150, c1=2050)[-1]
        self.top = P.long_rows(d, 0.3, r1=300, c0=150, c1=2050)[0]
        cols = P.long_cols(d, 0.6, r0=80, r1=1700, c1=2100)
        self.left, self.right = cols[0], cols[-1]
        xt = P.ticks_off_hline(d, self.bottom, self.left[0] - 5, self.right[1] + 30, +1, min_len=12)
        self.xa = P.Axis([c for c, _ in xt], F5.decade_values(len(xt)), log=True)
        # the top frame line (0.8, unlabelled) is left out on both sides
        yl = [r for r, n in P.ticks_off_vline(d, self.left, self.top[0] + 20, self.bottom[1] + 10, -1, min_len=20)]
        yr = [r for r, n in P.ticks_off_vline(d, self.right, self.top[0] + 20, self.bottom[1] + 10, +1, min_len=20)]
        vals = [0.6 - 0.2 * k for k in range(7)]
        if len(yl) != 7 or len(yr) != 7:
            raise ValueError(f"{len(yl)} left and {len(yr)} right y ticks")
        self.yl, self.yr = P.Axis(yl, vals), P.Axis(yr, vals)
        self.lcol = (self.left[0] + self.left[1]) / 2.0
        self.rcol = (self.right[0] + self.right[1]) / 2.0
        inner = np.zeros_like(d)
        sub = (slice(self.top[1] + 3, self.bottom[0] - 2), slice(self.left[1] + 3, self.right[0] - 2))
        inner[sub] = d[sub]
        self.filled = P.dots_mask(inner, 8)

    ya_at = F3.Panel.ya_at


def read(image, at):
    p = _Inset(image)
    lab, n = ndi.label(p.filled)
    radii = [float(ndi.distance_transform_edt(np.pad(lab[sl] == k, 1)).max())
             for k, sl in enumerate(ndi.find_objects(lab), start=1)]
    R = float(np.median(radii))
    single = float(np.pi * R * R)
    out = []
    for row, col, merged in F3._disks(p.filled, R, 1.6 * single):
        out.append(F3._point(p, row, col, 0.5 * R if merged else 2.0,
                             ("split from a blob of merged markers" if merged else "single marker")
                             + f"; marker radius {R:.1f} px"))
    out.sort(key=lambda o: (o["x"], o["y"]))
    return out
