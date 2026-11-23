"""Fig. S17 (PDF p. 41): v against alpha_c from eqn. 13. One dark-blue curve in a boxed MATLAB axis.

Calibration, all from the image:
- the box spines are the long dark (grey, not blue) lines; their centre lines are found from the
  column and row sums of the dark mask.
- x: the left spine is -1 and the right spine 0.5 (labels printed under them); the two short inner
  ticks on the bottom spine are -0.5 and 0. The four positions are fitted by a line.
- y: the short inner ticks on the RIGHT spine (the left-spine 0 tick is partly under the curve) are
  0, 20, 40, 60, 80 from the bottom, and the top spine is 100 (the y = 0 tick sits above the bottom
  spine, so the bottom spine is not used). Fitted by a line; the misfit is the largest residual.
- the curve is the blue stroke; at a column the value is the centre of the blue run (averaged over
  +-2 columns). Interval: a quarter of the stroke's run in that column (half-width of a stroke cut
  obliquely), the change of the centre over +-2 columns, twice the y misfit, and the x misfit
  carried through the local slope.
"""
import numpy as np


def _clusters(idx, gap=3):
    idx = sorted(int(i) for i in idx)
    if not idx:
        return []
    out, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - prev > gap:
            out.append((start, prev))
            start = i
        prev = i
    out.append((start, prev))
    return out


def _calib(image):
    img = image[..., :3].astype(float)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    blue = (b - r > 50) & (b - g > 30)
    dark = (img.mean(axis=2) < 110) & ~blue
    H, W = dark.shape
    vcols = _clusters(np.where(dark.sum(0) > 0.5 * H)[0])
    hrows = _clusters(np.where(dark.sum(1) > 0.5 * W)[0])
    (L0, L1), (R0, R1) = vcols[0], vcols[-1]
    (T0, T1), (B0, B1) = hrows[0], hrows[-1]
    Lc, Rc, Tc = (L0 + L1) / 2, (R0 + R1) / 2, (T0 + T1) / 2
    # y ticks: inner stubs left of the right spine
    band = dark[:, R0 - 25:R0 - 4].sum(1) > 8
    yt = [(a + c) / 2 for a, c in _clusters(np.where(band)[0]) if T1 + 10 < (a + c) / 2 < B0 - 10]
    yt = sorted(yt, reverse=True)
    rows = yt + [Tc]
    vals = [20.0 * i for i in range(len(yt))] + [100.0]
    py = np.polyfit(rows, vals, 1)
    ymis = float(np.max(np.abs(np.polyval(py, rows) - vals)))
    # x ticks: inner stubs above the bottom spine
    bandx = dark[B0 - 25:B0 - 4, :].sum(0) > 8
    xt = [(a + c) / 2 for a, c in _clusters(np.where(bandx)[0]) if L1 + 10 < (a + c) / 2 < R0 - 10]
    cols = [Lc] + sorted(xt) + [Rc]
    xv = [-1.0, -0.5, 0.0, 0.5]
    if len(cols) != 4:
        raise RuntimeError(f"expected 2 inner x ticks, found {len(xt)}")
    px = np.polyfit(cols, xv, 1)
    xmis = float(np.max(np.abs(np.polyval(px, cols) - xv)))
    return blue, py, px, ymis, xmis, len(yt)


def read(image, at):
    blue, py, px, ymis, xmis, nyt = _calib(image)
    dvdrow = abs(py[0])
    out = []
    for xs in at:
        x = float(xs)
        c = int(round((x - px[1]) / px[0]))
        centers = []
        for cc in range(c - 2, c + 3):
            rr = np.where(blue[:, cc])[0]
            if rr.size:
                centers.append(rr.mean())
        rr = np.where(blue[:, c])[0]
        if len(centers) < 5 or rr.size == 0:
            out.append({"x": x, "y": None, "note": "no blue curve pixels at this column (curve has left the box)"})
            continue
        row = float(np.mean(centers))
        y = float(np.polyval(py, row))
        thick = float(rr.max() - rr.min() + 1)
        spread = float(max(centers) - min(centers))
        slope_rows_per_col = spread / 4.0
        x_err_cols = xmis / abs(px[0])
        half = (0.25 * thick + 0.5 * spread + slope_rows_per_col * x_err_cols) * dvdrow + 2 * ymis + 0.2
        out.append({"x": x, "y": y, "lo": y - half, "hi": y + half, "px": [c, row],
                    "px_lo": row - half / dvdrow, "px_hi": row + half / dvdrow,
                    "note": f"stroke run {thick:.0f} px; y misfit {ymis:.2g}; x misfit {xmis:.2g}; {nyt} y ticks"})
    return out
