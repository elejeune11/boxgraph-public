"""Shared reading code for Fig. 7(b, c) (PDF p. 7).

Axes are calibrated by `_colour_curves.calibrate` (its docstring says how: y axis, x axis and
ticks found in the black pixels, labelled y ticks matched from the top to the printed labels,
x ticks on a regular grid from the y axis with the caller's step per tick).

Curves:
- `thick(cal, mask, frac)`: the thick strokes of a colour mask. Hatching, crosses, arrows and
  letters of the same colour are thinner than the drawn curves (their largest half width is under
  0.8 of the curve's), so only the connected parts at least `frac` times as thick as the thickest
  are kept; gaps cut by a black curve drawn across them are closed vertically.
- `runs(mask, c)`: the vertical runs of a mask in column c, top to bottom.
- `read_runs(cal, mask, at, pick, what)`: the value at each x is the middle of the run chosen by
  `pick(runs)` in each of the 7 columns around x (median over the columns; at least 5 columns
  must give a run). The interval is as in `_colour_curves.read_mask`: 2 px + a quarter of the run
  length, in y units, plus the y misfit and the local slope times the x misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi


def cc():
    spec = importlib.util.spec_from_file_location("haas2015_colour_curves", Path(__file__).with_name("_colour_curves.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def colour(cal, rgb, tol=30):
    return np.abs(cal["img"] - np.array(rgb)).max(axis=2) < tol


def plot_box(cal, mask):
    """Keep the part of a mask right of the y axis and above the x axis (axes and ticks left out)."""
    out = mask.copy()
    m = 4 * cal["lw"]
    out[:, : cal["c_axis"] + m] = False
    out[cal["r_axis"] - m:, :] = False
    return out


def thick(cal, mask, frac=0.8):
    """The thickest strokes of a mask: the connected parts whose largest half width (distance
    transform) is at least `frac` times the largest in the mask. Gaps where another (black) curve
    crosses the stroke are then closed vertically, over 2.5 half widths."""
    edt = ndi.distance_transform_edt(mask)
    lab, n = ndi.label(mask)
    if n == 0:
        return mask, 0.0
    mx = np.asarray(ndi.maximum(edt, lab, range(1, n + 1)))
    half = float(mx.max())
    out = np.isin(lab, [i + 1 for i in range(n) if mx[i] >= frac * half])
    h = max(3, int(round(2.5 * half)))
    out = ndi.binary_closing(out, structure=np.ones((h, 1), bool))
    return out, half


def groups(idx):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= 1:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def runs(mask, c):
    if c < 0 or c >= mask.shape[1]:
        return []
    return [((g[0] + g[-1]) / 2.0, len(g)) for g in groups(np.where(mask[:, c])[0])]


def read_runs(cal, mask, at, pick, what):
    m = cc()
    out = []
    for x in at:
        col = cal["c0"] + cal["cpu"] * x
        ci = int(round(col))
        got = [g for g in (pick(runs(mask, c), c) for c in range(ci - 3, ci + 4)) if g is not None]
        if len(got) < 5:
            out.append({"x": float(x), "y": None, "note": f"{what}: the curve cannot be told apart in this column"})
            continue
        row = float(np.median([g[0] for g in got]))
        ln = float(np.median([g[1] for g in got]))
        y = cal["a"] + cal["b"] * row
        dc = 12
        s1, s2 = pick(runs(mask, ci - dc), ci - dc), pick(runs(mask, ci + dc), ci + dc)
        slope = 0.0 if s1 is None or s2 is None else abs(s2[0] - s1[0]) / (2 * dc) * cal["cpu"] * abs(cal["b"])
        half_px = 2.0 + 0.25 * ln
        dy = abs(cal["b"]) * half_px + cal["ymis"] + slope * cal["xmis"]
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy), "px": [float(col), row],
                    "px_lo": row - half_px, "px_hi": row + half_px, "note": m.note(cal, what)})
    return out


def dot(cal, rgb):
    """The deepest pixel of a colour mask (a filled dot) and its radius."""
    mask = colour(cal, rgb)
    edt = ndi.distance_transform_edt(mask)
    r, c = np.unravel_index(int(np.argmax(edt)), edt.shape)
    return mask, edt, int(r), int(c), float(edt[r, c])
