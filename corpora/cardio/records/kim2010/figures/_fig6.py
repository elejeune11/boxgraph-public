"""Shared reading code for Fig. 6 (p. 11): mean LAD flow against diameter reduction.

The panel is vector art rendered at 1400 dpi. Grey gridlines mark the y labels 0..5 cc/s
(the bottom one is the x axis); short grey ticks below the axis mark the x labels
0, 20, ..., 100 %. Four series are drawn in black: open circles (Rest), filled circles
(Exercise), open squares (Rest, Gould et al.), filled squares (Hyperemia, Gould et al.).
A marker is found by matching its outline (open) or its body (filled) around the column
of the requested x; the sizes below were measured on this rendering.
"""
import numpy as np
from scipy import ndimage as ndi

# marker geometry in pixels at 1400 dpi, measured on the rendered crop
CIRCLE_OPEN_R = 35.5     # mid-stroke radius of an open circle (outer diameter 82, stroke 11)
SQUARE_OPEN_H = 25.0     # mid-stroke half side of an open square (outer side 61, stroke 11)
CIRCLE_FILL_R = 35.0     # radius of a filled circle (diameter 71)
SQUARE_FILL_H = 32.5     # half side of a filled square (side 66)
SEARCH_DX = 30           # columns searched either side of the requested x


def _runs(idx):
    out = []
    if len(idx) == 0:
        return out
    s = p = int(idx[0])
    for i in idx[1:]:
        i = int(i)
        if i != p + 1:
            out.append((s, p))
            s = i
        p = i
    out.append((s, p))
    return out


def masks(image):
    rgb = image[..., :3].astype(float)
    g = rgb.mean(axis=2)
    spread = rgb.max(axis=2) - rgb.min(axis=2)
    grey = (g > 100) & (g < 200) & (spread < 25)
    dark = g < 128
    return grey, dark


def calibrate(image):
    """Return (x_fit, y_fit, info): value = a + b * pixel for each axis, from the image."""
    grey, dark = masks(image)
    h, w = grey.shape
    # gridlines: rows that are grey (or covered by black data lines) over most of the width
    frac = (grey | dark).sum(axis=1) / w
    rows = [((a + b) / 2.0, b - a + 1) for a, b in _runs(np.where(frac > 0.6)[0])]
    rows = [r for r, t in rows if t < 20]
    bottom = max(rows)
    gaps = np.diff(sorted(rows))
    step = float(np.min(gaps[gaps > 50]))
    pts_y = [(r, round((bottom - r) / step)) for r in rows]
    # refine the step with every gridline found
    py = np.array([p for p, _ in pts_y])
    vy = np.array([v for _, v in pts_y], float)
    by, ay = np.polyfit(py, vy, 1)
    res_y = float(np.max(np.abs(py - (vy - ay) / by)))
    # x ticks: short grey marks just below the bottom gridline
    band = grey[int(bottom) + 8:int(bottom) + 40]
    # the y axis (x = 0) is the grey column running the full height of the plot
    vert = grey[int(min(rows)):int(bottom)].sum(axis=0)
    axis_runs = _runs(np.where(vert > 0.8 * (bottom - min(rows)))[0])
    yaxis = (axis_runs[0][0] + axis_runs[0][1]) / 2.0
    cols = [((a + b) / 2.0) for a, b in _runs(np.where(band.sum(axis=0) > 10)[0]) if b - a < 20]
    cols = sorted(c for c in cols if abs(c - yaxis) < 3 or c > yaxis + 3)
    # ticks are evenly spaced from the y axis, labelled 0, 20, 40, ...
    stepx = float(np.median(np.diff(cols)))
    px = np.array(cols)
    vx = np.array([20.0 * round((c - cols[0]) / stepx) for c in cols])
    bx, ax = np.polyfit(px, vx, 1)
    res_x = float(np.max(np.abs(px - (vx - ax) / bx)))
    return (ax, bx), (ay, by), {"res_x_px": res_x, "res_y_px": res_y, "ylabels": sorted(set(vy)),
                                "xlabels": sorted(set(vx)), "plot_top": min(rows), "plot_bottom": bottom}


def _ring_kernels(shape, size):
    """Point sets of a marker outline split into 8 sectors (offsets dy, dx)."""
    sectors = [[] for _ in range(8)]
    if shape == "circle":
        for t in np.linspace(0, 2 * np.pi, 720, endpoint=False):
            k = int(t / (2 * np.pi) * 8) % 8
            sectors[k].append((size * np.sin(t), size * np.cos(t)))
    else:
        for s in np.linspace(-size, size, 120):
            for (dy, dx) in ((-size, s), (size, s), (s, -size), (s, size)):
                t = np.arctan2(dy, dx) % (2 * np.pi)
                sectors[int(t / (2 * np.pi) * 8) % 8].append((dy, dx))
    return [np.round(np.array(sec)).astype(int) for sec in sectors]


def _body_kernels(shape, size):
    sectors = [[] for _ in range(8)]
    r = int(np.ceil(size))
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            inside = (dy * dy + dx * dx <= (0.8 * size) ** 2) if shape == "circle" else \
                (abs(dy) <= 0.8 * size and abs(dx) <= 0.8 * size)
            if inside and (dy or dx):
                t = np.arctan2(dy, dx) % (2 * np.pi)
                sectors[int(t / (2 * np.pi) * 8) % 8].append((dy, dx))
    return [np.array(sec) for sec in sectors]


def _score_map(field, kernels, r0, r1, c0, c1):
    """Minimum over sectors of the mean of `field` over each sector, for centres in the window."""
    best = None
    for k in kernels:
        acc = np.zeros((r1 - r0, c1 - c0))
        for dy, dx in k:
            acc += field[r0 + dy:r1 + dy, c0 + dx:c1 + dx]
        acc /= len(k)
        best = acc if best is None else np.minimum(best, acc)
    return best


def _interior_map(dark, size, r0, r1, c0, c1):
    """Mean darkness inside the marker's hole (radius 0.55 of the outline), for each centre."""
    rr = int(0.55 * size)
    acc = np.zeros((r1 - r0, c1 - c0))
    n = 0
    for dy in range(-rr, rr + 1, 2):
        for dx in range(-rr, rr + 1, 2):
            if dy * dy + dx * dx <= rr * rr:
                acc += dark[r0 + dy:r1 + dy, c0 + dx:c1 + dx]
                n += 1
    return acc / n


def find_marker(image, xcol, shape, filled, top, bottom):
    """Best centre (col, row, score) of a marker of the given kind near column xcol."""
    _, dark = masks(image)
    pad = 60
    d = np.pad(dark.astype(float), pad)
    dd = np.pad(ndi.binary_dilation(dark, iterations=2).astype(float), pad)
    c0, c1 = int(xcol - SEARCH_DX) + pad, int(xcol + SEARCH_DX) + 1 + pad
    r0, r1 = int(top - 40) + pad, int(bottom + 40) + pad
    if filled:
        size = CIRCLE_FILL_R if shape == "circle" else SQUARE_FILL_H
        body = _score_map(d, _body_kernels(shape, size), r0, r1, c0, c1)
        # just outside the body the paper is white except where lines leave the marker
        outer = np.mean([_score_map(d, [k], r0, r1, c0, c1) for k in _ring_kernels(shape, size * 1.35)], axis=0)
        score = body - 0.5 * outer
        # a filled square's corners are dark, a filled circle's are not
        # (points 27 px from the centre along both axes, 38 px away: inside a filled square of
        # half side 32.5, outside a filled circle of radius 35)
        k = int(round(0.83 * SQUARE_FILL_H))
        corners = np.array([(k * sy, k * sx) for sy in (-1, 1) for sx in (-1, 1)])
        cmap = np.mean([d[r0 + dy:r1 + dy, c0 + dx:c1 + dx] for dy, dx in corners], axis=0)
        score = score + (0.5 * cmap if shape == "square" else -0.5 * cmap)
    else:
        size = CIRCLE_OPEN_R if shape == "circle" else SQUARE_OPEN_H
        score = _score_map(dd, _ring_kernels(shape, size), r0, r1, c0, c1)
        inner = _interior_map(np.pad(dark.astype(float), pad), size, r0, r1, c0, c1)
        score = score - 2.0 * np.clip(inner - 0.7, 0, None)
    i = int(np.argmax(score))
    rr, cc = np.unravel_index(i, score.shape)
    return float(cc + c0 - pad), float(rr + r0 - pad), float(score.max())


def read_series(image, at, shape, filled, label):
    (ax, bx), (ay, by), info = calibrate(image)
    _, dark = masks(image)
    out = []
    px_per_y = 1.0 / abs(by)
    for x in at:
        col = (x - ax) / bx
        c, r, s = find_marker(image, col, shape, filled, info["plot_top"], info["plot_bottom"])
        y = ay + by * r
        # 95% interval: centre located to about 3 px, plus the y calibration misfit
        half = (3.0 + info["res_y_px"]) / px_per_y
        note = f"{label}: marker centre at column {c:.0f}, row {r:.0f}, match {s:.2f}; " \
               f"x calibration misfit {info['res_x_px']:.1f} px, y {info['res_y_px']:.1f} px"
        # a filled square scores about 1.4 (its dark corners add 0.5); a filled circle about 0.9
        if s < ((1.2 if shape == "square" else 0.6) if filled else 0.8):
            # the marker is hidden (at 100 % all series end under the exercise filled circle)
            fc, fr_, fs = find_marker(image, col, "circle", True, info["plot_top"], info["plot_bottom"])
            y = ay + by * fr_
            half = CIRCLE_FILL_R / px_per_y
            note = (f"{label}: marker not visible (best outline match {s:.2f}); it is hidden under the filled "
                    f"circle at column {fc:.0f}, row {fr_:.0f}, whose radius is taken as the interval")
            c, r = fc, fr_
        else:
            # a filled marker whose dark body is much taller than one marker is merged with others
            size = (CIRCLE_FILL_R if shape == "circle" else SQUARE_FILL_H) if filled else \
                (CIRCLE_OPEN_R + 5.5 if shape == "circle" else SQUARE_OPEN_H + 5.5)
            if filled:
                colv = dark[:, int(round(c))]
                a = b = int(round(r))
                while a > 0 and colv[a - 1]:
                    a -= 1
                while b < len(colv) - 1 and colv[b + 1]:
                    b += 1
                if b - a + 1 > 2.3 * size:
                    half = max(half, (b - a + 1) / 2.0 / px_per_y)
                    note += (f"; the marker is merged with others into a dark body {b - a + 1} px tall, "
                             f"whose half height is taken as the interval")
        out.append({"x": x, "y": y, "lo": y - half, "hi": y + half, "px": [c, r],
                    "px_lo": r - half * px_per_y, "px_hi": r + half * px_per_y, "note": note})
    return out
