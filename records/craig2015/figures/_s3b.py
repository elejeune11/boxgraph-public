"""Calibration for supplemental figure 3(b) (PDF p. 22), whose axes have no top frame line: the legend box
covers the top left and its edges confuse the kit's frame finder (the kit needs the full box).

Found in the image instead: the bottom axis is the row with most dark pixels in the lower 60% of the
crop; the right frame is the column with most dark pixels in the right half and the left frame the one
in the left 30%; the top is where the right frame's dark run starts. x ticks are small dark blobs in a
45 px band just above the bottom axis (blobs closer than 30 px merged), matched to the printed inner
labels 2, 4, 6; y ticks are small dark blobs in a 45 px band just left of the right frame, matched to the
inner labels 2, 1 (the 0 and 3 ticks sit on the corners). The fit and its misfit are the kit's (_fit).
The curves are then read by the kit's read_curve with this calibration.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("craig2015_kit_s3b", Path(__file__).with_name("_kit.py"))
_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kit)


def _merge(vals, gap=30):
    out = []
    for v in sorted(vals):
        if out and v - out[-1][-1] < gap:
            out[-1].append(v)
        else:
            out.append([v])
    return [float(np.mean(g)) for g in out]


def calibrate(image, xlabels, ylabels, **_):
    a = np.asarray(image, dtype=float)[:, :, :3]
    g = a.mean(axis=2)
    dark = (g < 90) & ((a.max(axis=2) - a.min(axis=2)) < 60)
    h, w = dark.shape
    rs = dark.sum(axis=1)
    B = int(np.argmax(np.where(np.arange(h) > 0.4 * h, rs, 0)))
    cs = dark.sum(axis=0)
    R = int(np.argmax(np.where(np.arange(w) > 0.5 * w, cs, 0)))
    L = int(np.argmax(np.where(np.arange(w) < 0.3 * w, cs, 0)))
    T = int(np.nonzero(dark[:, R])[0].min())
    d = dark.copy()
    d[B - 1:B + 2, :] = False
    d[:, R - 1:R + 2] = False
    d[:, L - 1:L + 2] = False
    small = [b for b in _kit._blobs(d) if b["area"] < 500]
    xs = _merge([b["c"] for b in small if B - 45 <= b["r"] <= B and L + 12 < b["c"] < R - 12])
    ys = _merge([b["r"] for b in small if R - 45 <= b["c"] <= R and T + 12 < b["r"] < B - 12])
    kx, cx, mx = _kit._fit(np.array(xs), xlabels)
    ky, cy, my = _kit._fit(np.array(ys), ylabels)
    return {"frame": (L, T, R, B), "kx": kx, "cx": cx, "mx": mx, "ky": ky, "cy": cy, "my": my,
            "xticks": xs, "yticks": ys}


_kit.calibrate = calibrate  # this private copy of the kit reads with the calibration above


def read_curve(image, at, color):
    return _kit.read_curve(image, at, [2, 4, 6], [2, 1], color=color, legend_text=True)
