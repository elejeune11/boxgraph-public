"""Fig. 3, bottom (p. 6): phase of the baroreceptor transfer function against frequency (log x).

Calibration from the image: x as in fig3_modulus (frame sides at 0.001 and 1, dotted vertical
grid lines at 0.01 and 0.1); y, the frame's bottom side (label 0) and the one dotted horizontal
grid line (label 100). With two y marks the y misfit cannot be checked; the interval carries
half a pixel for it. The curve is the one thick line inside the frame.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_u98", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_u98.py"))
u = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(u)


def calibrate(m):
    H, W = m.shape
    v = u.long_lines(m, 1, int(0.6 * H))
    h = u.long_lines(m, 0, int(0.6 * W))
    left, right = v[0], v[-1]
    top, bottom = h[0], h[-1]
    inside = m.copy()
    inside[:, : left[1] + 3] = False
    inside[:, right[0] - 3:] = False
    inside[: top[1] + 3, :] = False
    inside[bottom[0] - 3:, :] = False
    pts = u.dots(inside, amax=600, dmax=30)
    rows = u.grid_lines(pts, 0, min_count=10)
    off = [p for p in pts if min([abs(p[1] - r) for r in rows] or [99]) > 8]
    cols = [c for c in u.grid_lines(off, 1, min_count=6) if left[1] + 25 < c < right[0] - 25]
    if len(rows) != 1 or len(cols) != 2:
        raise ValueError(f"expected 1 dotted row and 2 dotted columns, found {rows} and {cols}")
    xcal = u.Cal([((left[0] + left[1]) / 2.0, 0.001), (cols[0], 0.01), (cols[1], 0.1),
                  ((right[0] + right[1]) / 2.0, 1.0)], log=True)
    ycal = u.Cal([((bottom[0] + bottom[1]) / 2.0, 0.0), (rows[0], 100.0)])
    box = (left[1] + 15, top[1] + 15, right[0] - 15, bottom[0] - 15)
    return xcal, ycal, box


def read(image, at):
    m = u.ink(image)
    xcal, ycal, (c0, r0, c1, r1) = calibrate(m)
    curve = u.opened(m, 15)
    keep = curve & False
    keep[r0:r1, c0:c1] = curve[r0:r1, c0:c1]
    out = u.read_line(keep, xcal, ycal, at)
    for d in out:
        d["note"] = (d.get("note", "") + f" calibration misfit x {xcal.misfit:.1f} px; y from two marks").strip()
    return out
