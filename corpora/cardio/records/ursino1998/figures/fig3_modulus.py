"""Fig. 3, middle (p. 6): normalized modulus of the baroreceptor transfer function against
frequency, log-log. The plot is a frame with dotted grid lines.

Calibration from the image: x, the frame's left and right sides (labels 0.001 and 1) and the two
dotted vertical grid lines (labels 0.01 and 0.1); y, the nine dotted horizontal grid lines
(1, 2, ..., 9 of the decade, the lowest labelled 10^0) and the frame's top side (10^1). The curve
is the one thick line: ink that survives an opening wider than the grid dots.
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
    off = [p for p in pts if min(abs(p[1] - r) for r in rows) > 8]  # dots not on a dotted row
    # (dotted lines are also drawn along the frame's sides, at 0.001 and 1: those are skipped)
    cols = [c for c in u.grid_lines(off, 1, min_count=6) if left[1] + 25 < c < right[0] - 25]
    if len(rows) != 9 or len(cols) != 2:
        raise ValueError(f"expected 9 dotted rows and 2 dotted columns, found {rows} and {cols}")
    xcal = u.Cal([((left[0] + left[1]) / 2.0, 0.001), (cols[0], 0.01), (cols[1], 0.1),
                  ((right[0] + right[1]) / 2.0, 1.0)], log=True)
    ymarks = [(r, float(9 - i)) for i, r in enumerate(rows)] + [((top[0] + top[1]) / 2.0, 10.0)]
    ycal = u.Cal(ymarks, log=True)
    box = (left[1] + 15, top[1] + 15, right[0] - 15, bottom[0] - 15)  # the scanned frame is wavy
    return xcal, ycal, box


def read(image, at):
    m = u.ink(image)
    xcal, ycal, (c0, r0, c1, r1) = calibrate(m)
    curve = u.opened(m, 15)
    keep = curve.copy()
    keep[:, :] = False
    keep[r0:r1, c0:c1] = curve[r0:r1, c0:c1]
    out = u.read_line(keep, xcal, ycal, at)
    for d in out:
        d["note"] = (d.get("note", "") + f" calibration misfit x {xcal.misfit:.1f} px, y {ycal.misfit:.1f} px").strip()
    return out
