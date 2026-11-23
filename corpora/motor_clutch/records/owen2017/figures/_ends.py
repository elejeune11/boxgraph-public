"""Shared code for the force-displacement panels (Fig. 6B, S16B, S16D): where each line leaves the
plot. Loaded by the reading files through _kit-style hash pinning (see fig6b_ends.py).

The lines are straight segments from the origin, clipped at the top of the force axis or ending
at the right end of the displacement axis. Each line is read once, where it ends:
- top: in the row of force `f_top` (just below the top tick, so the tick itself is not crossed),
  each dark run is one line (or several coincident lines: a run wider than 1.8 times the median
  run is reported as one point and flagged). x = the run centre, y = f_top. The interval in y is
  zero-width in principle (the row is chosen); it is given as +-1 px and twice the y misfit. The
  uncertainty in x (half the run width) is in the note.
- right: in the column of displacement `u_right` (just left of the axis end), each dark run is
  a line; y = its centre, interval half its length + 1 px + twice the y misfit.
"""
import numpy as np


def ends(k, X, Y, d, f_top, u_right, r_top_excl, xrow, ycol):
    out = []
    row = int(round(Y.pix(f_top)))
    c_lo = int(ycol) + 6
    c_hi = int(round(X.pix(u_right))) - 4
    rr = [(a, b) for a, b in k.runs(d[row, c_lo:c_hi], 1)]
    widths = [b - a + 1 for a, b in rr]
    med = float(np.median(widths)) if widths else 0.0
    for a, b in rr:
        c = (a + b) / 2 + c_lo
        x = float(X.val(c))
        half = 1 + 2 * Y.misfit_px
        flag = " (wide run: probably two or more coincident lines)" if (b - a + 1) > 1.8 * med else ""
        out.append({"x": x, "y": float(f_top), "lo": float(Y.val(row + half)), "hi": float(Y.val(row - half)),
                    "px": [c, row], "note": f"top end; run {b - a + 1} px = +-{X.per_px(c) * (b - a + 1) / 2:.2g} um in x{flag}"})
    col = int(round(X.pix(u_right)))
    for a, b in k.runs(d[r_top_excl:int(xrow) - 4, col], 1):
        r = (a + b) / 2 + r_top_excl
        half = (b - a + 1) / 2 + 1 + 2 * Y.misfit_px
        out.append({"x": float(u_right), "y": float(Y.val(r)), "lo": float(Y.val(r + half)), "hi": float(Y.val(r - half)),
                    "px": [col, r], "px_lo": r - half, "px_hi": r + half,
                    "note": f"right end; run {b - a + 1} px"})
    out.sort(key=lambda p: (p["x"], p["y"]))
    return out
