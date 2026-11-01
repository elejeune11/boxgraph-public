"""Fig. S2 D (PDF p. 9): normalized traction stress against normalized F-actin speed across
single FAs, one dark blue asterisk per point (the dotted lines are not read).

Calibration from the image: the frame; ticks on the bottom and left edges, all of one length,
evenly spaced; the bottom and left frame edges lie on the tick grid and carry the label 0. The
only other labels are "1" at the top and right frame edges, which do NOT lie on the tick grid:
the frame spans 5.5 tick steps. The ticks are read as steps of 0.2 (0.2 ... 1.0), so the frame
edges are at 1.1; this is an added reading choice, supported by the image: the points that
normalization puts at exactly 1 (several in each direction) lie on the fifth tick, not on the
frame edge. The check is reported in the notes.
Asterisks: dark blue pixels (the dotted lines are of the same colour but made of small dots);
connected pieces at least half an asterisk in size. An asterisk's centre is where its strokes
cross, the densest point: the mask is smoothed with a box a third of an asterisk wide and the
local maxima (one per asterisk-sized neighbourhood) are the centres; two touching asterisks give
two maxima.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

_spec = importlib.util.spec_from_file_location("gardel_lib", Path(__file__).with_name("_lib.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


def read(image, at):
    fr = L.frame(image)
    tx = L.ticks(image, fr["bottom"], (fr["left"] + 15, fr["right"] - 15), "x", -1, 80, lw=fr["lw_row"])
    ty = L.ticks(image, fr["left"], (fr["top"] + 15, fr["bottom"] - 15), "y", 1, 80, lw=fr["lw_col"])
    ax, bx, mx, dx = L.grid_axis(tx, fr["left"], fr["right"], 0.0, (None, 1), 0.2, all_major=True)
    ay, by, my, dy = L.grid_axis(ty, fr["bottom"], fr["top"], 0.0, (None, 1), 0.2, all_major=True)
    f = image.astype(float)
    m = (f[..., 2] > f[..., 0] + 30) & (f[..., 2] > f[..., 1] + 20) & (f.mean(axis=2) < 170)
    m[:int(fr["top"]) + 8] = False
    m[int(fr["bottom"]) - 8:] = False
    m[:, :int(fr["left"]) + 8] = False
    m[:, int(fr["right"]) - 8:] = False
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sls = ndi.find_objects(lab)
    sizes = [max(s[0].stop - s[0].start, s[1].stop - s[1].start) for s in sls]
    big = [s for s in sizes if s > 30]
    size = float(np.median(big))
    keep = np.zeros_like(m)
    for i, (s, z) in enumerate(zip(sls, sizes), start=1):
        if z >= 0.5 * size:
            keep[s] |= lab[s] == i
    w = max(3, int(size / 3))
    dens = ndi.uniform_filter(keep.astype(float), w)
    peak = (dens == ndi.maximum_filter(dens, int(0.6 * size))) & (dens > 0.5 * dens.max())
    pl, pn = ndi.label(peak)
    raw = ndi.center_of_mass(peak, pl, range(1, pn + 1))
    # a flat-topped maximum can give two peaks a few pixels apart: merge peaks closer than a
    # third of an asterisk
    cents = []
    for r, c in sorted(raw):
        for k, (r2, c2, nk) in enumerate(cents):
            if np.hypot(r - r2, c - c2) < size / 3:
                cents[k] = ((r2 * nk + r) / (nk + 1), (c2 * nk + c) / (nk + 1), nk + 1)
                break
        else:
            cents.append((r, c, 1))
    cents = [(r, c) for r, c, _ in cents]
    out = []
    for r, c in sorted(cents, key=lambda t: (t[1], t[0])):
        x = (c - ax) / bx
        y = (r - ay) / by
        e_px = 2.0 + my
        note = f"asterisk centre (asterisk {size:.0f} px)"
        if not out:
            note += (f"; x axis {dx}; y axis {dy}; frame top at y = {(fr['top'] - ay) / by:.3f}, "
                     f"right at x = {(fr['right'] - ax) / bx:.3f} (the '1' labels)")
        out.append({"x": float(x), "y": float(y), "lo": float(y - e_px / abs(by)), "hi": float(y + e_px / abs(by)),
                    "px": [float(c), float(r)], "note": note})
    return out
