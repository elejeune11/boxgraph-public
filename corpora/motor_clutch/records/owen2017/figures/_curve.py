"""Shared code for the line plots of Owen et al. 2017 read at given x (Fig. 2D-H, 4F, S12): a line,
optionally inside a shaded band. Loaded with hash pinning by the reading files, which give a CONFIG.

Calibration (`_kit.calibrate`, all positions from the image): the axis lines are the longest dark
vertical and horizontal runs (dark = grey level below CONFIG["dark"]); tick stubs on either side
of each axis line are matched in order to CONFIG["xlabels"] / ["ylabels"] (the evenly spaced subset
when curves add stray candidates); CONFIG["x_pin"] / ["y_pin"] put a label on the other axis line.
For a panel whose axes are not at the plot's left and bottom (stacked panels), CONFIG["region"]
(c0, r0, c1, r1) restricts the search to the panel.
Line: colour mask of CONFIG["line"] (tolerance CONFIG["line_tol"]); band: colour mask of
CONFIG["band"]. With a band each value carries the band as its error bar (`_kit.curve_band`);
without, `_kit.curve_value` on the run nearest the previous reading.
"""
import numpy as np


def _calib_marks(k, d, C):
    """For panels with only two labelled y values (Fig. 2D-H): x as in `_kit.calibrate`; y from
    CONFIG["ymarks"], pairs (where, label) with where = "axis" (the x-axis line), "zero_line" (a
    long dark horizontal line inside the panel other than the axis) or "top_stub" (the topmost
    tick stub right of the y axis). Further stubs found are snapped to the nearest multiple of
    CONFIG["y_step"] by that first fit and added as marks, so the misfit includes them."""
    ycol, xrow = k.axis_lines(d)
    hy, hx = k.line_half_thickness(d, ycol, xrow)
    H, W = d.shape
    xc = k.tick_candidates(d, "x", xrow, hx, C.get("tick_len", 14), ycol + hy + 3, W - 1)
    xt = None
    for side in (-1, 1):
        if len(xc[side]) >= len(C["xlabels"]):
            xt = xt or k.even_subset(xc[side], len(C["xlabels"]))
    if not xt:
        raise RuntimeError(f"x ticks not found: {xc}")
    xm = list(zip(sorted(xt), C["xlabels"]))
    if C.get("x_pin") is not None:
        xm.append((ycol, C["x_pin"]))
    X = k.Lin(xm)
    stubs = sorted(k.tick_candidates(d, "y", ycol, hy, C.get("tick_len", 14), 0, xrow - hx - 3)[1])
    marks = []
    for where, val in C["ymarks"]:
        if where == "axis":
            marks.append((xrow, val))
        elif where == "top_stub":
            marks.append((stubs[0], val))
        elif where == "zero_line":
            rows = [r for r in range(int(xrow) - 8) if d[r, int(ycol) + 5:].mean() > 0.6]
            cl = k.clusters(rows)
            if not cl:
                raise RuntimeError("no zero line found")
            a, b = max(cl, key=lambda ab: ab[1] - ab[0])
            marks.append(((a + b) / 2, val))
    Y0 = k.Lin(marks)
    step = C["y_step"]
    used = {round(m[0]) for m in marks}
    for s in stubs:
        if any(abs(s - u) < 6 for u in used):
            continue
        v = Y0.val(s)
        snap = round(v / step) * step
        if abs(v - snap) < 0.25 * step:
            marks.append((s, snap))
    Y = k.Lin(marks)
    return X, Y, {"ycol": ycol, "xrow": xrow, "hy": hy, "hx": hx}


def markers_band(k, image, C):
    """Plotted round markers joined by a line, inside a shaded confidence band (Fig. 3G).
    Calibration by `_kit.calibrate` as for `read`. Markers: `_kit.read_disks` on the marker colour
    (the joining line is thinner than 0.6 of the marker radius); the radius is the deepest
    distance-transform value of the colour mask. The band's top and bottom in the marker's column
    (the run of band-or-marker colour containing the marker) are the error bar ends."""
    from scipy import ndimage
    d = k.dark_mask(image, C.get("dark", 110))
    mk = k.color_mask(image, C["marker"], C.get("marker_tol", 50))
    d &= ~mk
    X, Y, info = k.calibrate(image, C["xlabels"], C["ylabels"], dark=d, x_pin=C.get("x_pin"), y_pin=C.get("y_pin"),
                             tick_len=C.get("tick_len", 14))
    r = float(ndimage.distance_transform_edt(mk).max())
    box = (info["ycol"] + 3, 0, image.shape[1], info["xrow"] - 3)
    pts = k.read_disks(X, Y, mk, r, box, note=f"r {r:.0f} px; x misfit {X.misfit_px:.2g} px, y misfit {Y.misfit_px:.2g} px")
    band = k.color_mask(image, C["band"], C.get("band_tol", 30)) | mk
    e = 1 + 2 * Y.misfit_px
    for p in pts:
        c, row = int(round(p["px"][0])), p["px"][1]
        ab = k.band_extent(Y, band, c, row, gap=8)  # the marker's anti-aliased rim is bridged
        if ab is None:
            continue
        p.update({"bar_hi": float(Y.val(ab[0])), "bar_lo": float(Y.val(ab[1])),
                  "bar_hi_outer": float(Y.val(ab[0] - e)), "bar_lo_outer": float(Y.val(ab[1] + e))})
        if ab[1] - ab[0] < 2 * r + 2:
            p["note"] += "; band within the marker: bar is at most the marker"
    return pts


def scatter(k, image, C):
    """A scatter of round dots of one colour (Fig. S9B). Calibration by `_kit.calibrate`; the
    shaded band is excluded from the dark mask by colour. Dots: `_kit.read_disks` with r the median
    depth of the distance transform over the dot components; touching dots form one elongated
    component, reported once at its centre with the extra height in the interval and flagged."""
    from scipy import ndimage
    dots = k.color_mask(image, C["marker"], C.get("marker_tol", 60))
    d = k.dark_mask(image, C.get("dark", 110)) & ~dots
    X, Y, info = k.calibrate(image, C["xlabels"], C["ylabels"], dark=d, x_pin=C.get("x_pin"), y_pin=C.get("y_pin"),
                             tick_len=C.get("tick_len", 14))
    dt = ndimage.distance_transform_edt(dots)
    lab, n = ndimage.label(dt >= 2)
    tops = np.array(ndimage.maximum(dt, lab, range(1, n + 1)))
    r = float(np.median(tops))
    box = (info["ycol"] + 2, 0, image.shape[1], info["xrow"] - 2)
    return k.read_disks(X, Y, dots, r, box, note=f"r {r:.1f} px; x misfit {X.misfit_px:.2g} px, y misfit {Y.misfit_px:.2g} px")


def read(k, image, C, at):
    img = image
    if C.get("region"):
        c0, r0, c1, r1 = C["region"]
        img = image[r0:r1, c0:c1]
    else:
        c0 = r0 = 0
    d = k.dark_mask(img, C.get("dark", 110))
    if C.get("exclude_line_from_dark", True):
        d &= ~k.color_mask(img, C["line"], C.get("line_tol", 50))
        if C.get("band"):
            d &= ~k.color_mask(img, C["band"], C.get("band_tol", 30))
    if C.get("ymarks"):
        X, Y, info = _calib_marks(k, d, C)
    else:
        X, Y, info = k.calibrate(img, C["xlabels"], C["ylabels"], dark=d, x_pin=C.get("x_pin"), y_pin=C.get("y_pin"),
                                 tick_len=C.get("tick_len", 14))
    line = k.color_mask(img, C["line"], C.get("line_tol", 50))
    ymax = C.get("ytop", max(C["ylabels"]) if C.get("ylabels") else max(v for _, v in C["ymarks"]))
    top = int(Y.pix(ymax)) - C.get("above_top", 40)
    bot = int(info["xrow"] - info["hx"] - 1)
    out = []
    note = C.get("note", "")
    if C.get("band"):
        band = k.color_mask(img, C["band"], C.get("band_tol", 30))
        for x in at:
            out.append(k.curve_band(X, Y, line, band, float(x), r0=max(top, 0), r1=bot, note=note))
    else:
        prev = None
        for x in at:
            def pick(rs, prev=prev):
                if prev is None:
                    return max(rs, key=lambda ab: ab[1] - ab[0])
                return min(rs, key=lambda ab: abs((ab[0] + ab[1]) / 2 - prev))
            r = k.curve_value(X, Y, line, float(x), pick, r0=max(top, 0), r1=bot, note=note)
            if r.get("y") is not None:
                prev = r["px"][1]
            out.append(r)
    for r in out:  # back to the coordinates of the whole crop
        if "px" in r:
            r["px"] = [r["px"][0] + c0, r["px"][1] + r0]
            for key in ("px_lo", "px_hi"):
                if key in r:
                    r[key] += r0
    return out
