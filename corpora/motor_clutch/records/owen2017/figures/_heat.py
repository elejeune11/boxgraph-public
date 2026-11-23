"""Shared code for the density map of Fig. 4E of Owen et al. 2017 (PDF p. 7): counts of alpha-actinin-1
puncta pairs in bins of distance (x) and cos(theta) between their velocities (rows), shown in colour
with a colour bar labelled "bin counts x 10^-3", 0 to 3. Loaded with hash pinning by the reading
files, which give a CONFIG.

Everything is found in the image; typed in are only the printed labels: the colour bar's 0 and 3,
the x labels 0..100, the y labels 1, 0, -1, and the number of cos(theta) rows (CONFIG["rows"]).
- boxes: the colour bar and the map are the two blocks of rows with more than 300 saturated pixels
  (max-min of RGB > 60); each box's columns are its saturated columns.
- colour bar: its 0 and 3 labels sit at its two ends, so a bar column's value is 3 * (column - left)
  / (right - left); its colour is the median over the middle half of its rows.
- x: tick stubs (at least 80% of a 6-row band dark, < 90 grey) along the map's lower edge, evenly
  spaced; the first is the y axis (x = 0) and the last the frame (x = 100, labelled 100); the
  value is linear between them. Misfit: the largest residual of the stubs on that line.
- rows: the map is CONFIG["rows"] equal rows from the top edge to the bottom edge (the centres of
  the dark frame lines above and below the colour block: rows more than half dark, < 110 grey); the labels 1 and
  -1 sit at the centres of the top and bottom rows, so row k (from the top) is cos = 1 - 2k/(rows-1).
  This is checked: in the column at x = 20 the rows where the colour jumps (more than 25 in RGB
  distance from the row 3 px above; not within 0.4 row of the frame, whose line blurs up to ~12 px
  into the bright yellow top row) are compared with the grid's row boundaries; the largest
  distance from a jump to the nearest boundary is reported as the row misfit.
- value at x in row k: the median colour over columns x +-2 px and the middle half of the row; the
  bar column of nearest colour gives the value; the interval is the span of bar columns whose colour
  lies within 8 (RGB distance) of the nearest, widened by the x misfit through the local change of
  value along the row. Counts are returned in units of 1, the bar value times 10^3 (the bar is
  labelled "bin counts x 10^-3": the counts times 10^-3 are shown).
"""
import numpy as np


def _blocks(mask_rows):
    idx = np.where(mask_rows)[0]
    out = []
    for i in idx:
        if out and i - out[-1][1] <= 3:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def read(k, image, C, at):
    img = k.rgb(image)
    g = img.mean(axis=2)
    sat = img.max(axis=2) - img.min(axis=2)
    colm = sat > 60
    blocks = [b for b in _blocks(colm.sum(axis=1) > 300) if b[1] - b[0] > 10]
    (b0, b1), (m0, m1) = blocks[0], blocks[-1]
    bcols = np.where(colm[(b0 + b1) // 2])[0]
    bl, br = float(bcols.min()), float(bcols.max())
    q0, q1 = b0 + (b1 - b0) // 4, b1 - (b1 - b0) // 4
    bar = np.median(img[q0:q1 + 1, int(bl):int(br) + 1], axis=0)  # colour per bar column
    bar_val = 3.0 * (np.arange(int(bl), int(br) + 1) - bl) / (br - bl)
    # x ticks on the lower edge of the map
    band = (g[m1 - 7:m1 - 1, :] < 90).mean(axis=0) > 0.8
    st = [(a + b) / 2 for a, b in k.clusters(np.where(band)[0], 1) if b - a < 10]
    mcols = np.where(colm[(m0 + m1) // 2])[0]
    st = [s for s in st if mcols.min() - 8 <= s <= mcols.max() + 4]
    st = k.even_subset(st, C.get("xticks", 11)) or st
    X = k.Lin([(p, 100.0 * i / (len(st) - 1)) for i, p in enumerate(st)])
    # rows
    # the map's top and bottom edges are the centres of the dark frame lines next to the colour block
    mc0, mc1 = int(mcols.min()) + 20, int(mcols.max()) - 20

    def frame(r_from, r_to):
        rr = [r for r in range(r_from, r_to) if (g[r, mc0:mc1] < 110).mean() > 0.5]
        return float(np.mean(rr)) if rr else None
    top = frame(m0 - 12, m0 + 4)
    bot = frame(m1 - 4, m1 + 12)
    if top is None or bot is None:
        raise RuntimeError("map frame lines not found")
    n = C["rows"]
    h = (bot - top) / n
    cx = int(round(X.pix(20.0)))
    colr = img[:, cx]
    edge = int(0.4 * h)  # the frame line's blur reaches ~12 px into a bright (yellow) row
    jumps = [r for r in range(int(top) + edge, int(bot) - edge)
             if np.linalg.norm(colr[r] - colr[r - 3]) > 25]
    jumps = [(a + b) / 2 for a, b in k.clusters(jumps, 3)]
    bounds = [top + i * h for i in range(n + 1)]
    rmis = max([min(abs(j - b) for b in bounds) for j in jumps] or [0.0])
    kk = C["row"]
    r_c = top + (kk + 0.5) * h
    ra, rb = int(round(r_c - h / 4)), int(round(r_c + h / 4))
    out = []
    note0 = (f"row {kk} of {n} (cos {1 - 2 * kk / (n - 1):.2g}), rows {ra}-{rb}; {len(jumps)} colour steps at x = 20 "
             f"lie within {rmis:.1f} px of the {n}-row grid (row height {h:.1f} px); x misfit {X.misfit_px:.2g} px")
    for x in at:
        x = float(x)
        c = int(round(X.pix(x)))
        vals = []
        for cc in (c - 3, c, c + 3):
            colour = np.median(img[ra:rb + 1, cc - 2:cc + 3].reshape(-1, 3), axis=0)
            d = np.linalg.norm(bar - colour, axis=1)
            vals.append((float(d.min()), bar_val[int(np.argmin(d))], bar_val[d <= d.min() + 8]))
        dmin, v, near = vals[1]
        slope = abs(vals[2][1] - vals[0][1]) / 6.0  # value per px along the row
        lo = float(near.min()) - slope * X.misfit_px
        hi = float(near.max()) + slope * X.misfit_px
        out.append({"x": x, "y": 1000.0 * v, "lo": 1000.0 * max(lo, 0.0), "hi": 1000.0 * hi,
                    "px": [c, r_c], "px_lo": ra, "px_hi": rb,
                    "note": f"nearest bar colour at distance {dmin:.0f}; {note0}"})
    return out
