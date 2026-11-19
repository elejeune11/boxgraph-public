"""Shared reading helpers for this paper's gnuplot panels (frame, inward ticks, coloured lines).

Everything is found in the rendered crop: the plot frame is the longest dark neutral line on each
side, the ticks are short dark runs that start at the frame's inner edge, and a curve is the set of
pixels close to its colour. Each reading module matches the ticks it finds to the printed labels.
"""
import numpy as np


def masks(img):
    f = img.astype(float)
    g = f.mean(axis=2)
    sat = f.max(axis=2) - f.min(axis=2)
    return g, sat, (g < 110) & (sat < 40)


def _longest(v):
    best, cur = 0, 0
    for x in v:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def frame(img):
    """Centres of the left, top, right and bottom frame lines, and the frame line half-width."""
    _, _, blk = masks(img)
    H, W = blk.shape
    colrun = np.array([_longest(blk[:, c]) for c in range(W)])
    rowrun = np.array([_longest(blk[r]) for r in range(H)])
    cols = np.where(colrun > 0.5 * colrun.max())[0]
    rows = np.where(rowrun > 0.5 * rowrun.max())[0]

    def groups(idx):
        out, cur = [], [idx[0]]
        for i in idx[1:]:
            if i - cur[-1] <= 2:
                cur.append(i)
            else:
                out.append(cur)
                cur = [i]
        out.append(cur)
        return out

    cg, rg = groups(cols), groups(rows)
    left, right = cg[0], cg[-1]
    top, bottom = rg[0], rg[-1]
    c = lambda g: (g[0] + g[-1]) / 2.0
    half = max(len(left), len(bottom)) / 2.0
    return dict(left=c(left), right=c(right), top=c(top), bottom=c(bottom), half=half,
                left_in=left[-1] + 1, right_in=right[0] - 1, top_in=top[-1] + 1, bottom_in=bottom[0] - 1)


def _tick_groups(lengths, positions, minlen):
    out, cur = [], []
    for p, n in zip(positions, lengths):
        if n >= minlen:
            cur.append((p, n))
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    res = []
    for gr in out:
        ps = [p for p, _ in gr]
        res.append(((ps[0] + ps[-1]) / 2.0, max(n for _, n in gr), len(gr)))
    return res


def _run(v):
    n = 0
    while n < len(v) and v[n]:
        n += 1
    return n


def y_ticks(img, fr, side="left", depth=120, minlen=10):
    """Inward ticks on the left (or right) frame line: (row, length, thickness), frame rows excluded."""
    _, _, blk = masks(img)
    if side == "left":
        c = int(fr["left_in"])
        band = blk[:, c:c + depth]
    else:
        c = int(fr["right_in"])
        band = blk[:, max(c - depth + 1, 0):c + 1][:, ::-1]
    rows = list(range(int(fr["top"] + 2 * fr["half"] + 2), int(fr["bottom"] - 2 * fr["half"] - 1)))
    return _tick_groups([_run(band[r]) for r in rows], rows, minlen)


def x_ticks(img, fr, side="bottom", depth=120, minlen=10):
    """Inward ticks on the bottom (or top) frame line: (column, length, thickness), frame columns excluded."""
    _, _, blk = masks(img)
    if side == "bottom":
        r = int(fr["bottom_in"])
        band = blk[max(r - depth + 1, 0):r + 1][::-1].T
    else:
        r = int(fr["top_in"])
        band = blk[r:r + depth].T
    cols = list(range(int(fr["left"] + 2 * fr["half"] + 2), int(fr["right"] - 2 * fr["half"] - 1)))
    return _tick_groups([_run(band[c]) for c in cols], cols, minlen)


def major(ticks, frac=0.75):
    longest = max(n for _, n, _ in ticks)
    return [p for p, n, _ in ticks if n >= frac * longest]


def fit(marks):
    """Linear fit value = a + b * pixel; the largest misfit in pixels."""
    P = np.array([m[0] for m in marks], float)
    V = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(P, V, 1)
    mis = float(np.max(np.abs(P - (V - a) / b)))
    return a, b, mis


def colour_mask(img, rgb, tol):
    f = img.astype(float)
    return np.sqrt(((f - np.array(rgb, float)) ** 2).sum(axis=2)) < tol


def calibrate(img, ylabels, xlabels, xticks_side="bottom", y_from_frame=True, yside="left", tick_max=None):
    """Frame and tick calibration of a gnuplot panel.

    y: the major inward ticks on the left frame line, with the top and bottom frame lines, are
    matched top to bottom to `ylabels` (the printed labels, the frame carrying the first and last).
    x: `xlabels` is a list of (label value, kind), kind 'frame-left', 'frame-right' or 'tick:k'
    (the k-th major inward tick on the bottom frame line, from the left)."""
    fr = frame(img)
    # a long horizontal line (a reference line such as y = 1) is not a tick: drop rows where
    # dark pixels run across a third of the plot
    _, _, blk = masks(img)
    width = fr["right"] - fr["left"]
    cand = [t for t in y_ticks(img, fr, side=yside)
            if blk[int(round(t[0])), int(fr["left_in"]):int(fr["right_in"])].sum() < 0.3 * width
            and (tick_max is None or t[1] < tick_max)]  # a black data line touching the frame is not a tick
    yt = sorted(major(cand)) if cand else []
    if isinstance(ylabels[0], tuple):
        # explicit: (value, kind) with kind frame-top, frame-bottom, tick:k (k-th major tick from
        # the top) or hline (the long horizontal reference line drawn inside the plot)
        marks = []
        for v, kind in ylabels:
            if kind == "frame-top":
                marks.append((fr["top"], v))
            elif kind == "frame-bottom":
                marks.append((fr["bottom"], v))
            elif kind == "hline":
                lines = [r for r in range(int(fr["top_in"]) + 3, int(fr["bottom_in"]) - 3)
                         if blk[r, int(fr["left_in"]):int(fr["right_in"])].sum() > 0.6 * width]
                marks.append(((lines[0] + lines[-1]) / 2.0, v))
            else:
                marks.append((yt[int(kind.split(":")[1])], v))
    else:
        # the frame lines carry the first and last labels; each tick found is matched to the label
        # whose evenly spaced position it lies nearest to (within a tenth of a spacing)
        step = (fr["bottom"] - fr["top"]) / (len(ylabels) - 1)
        marks = [(fr["top"], ylabels[0]), (fr["bottom"], ylabels[-1])]
        for t in yt:
            k = int(round((t - fr["top"]) / step))
            if 0 < k < len(ylabels) - 1 and abs(t - (fr["top"] + k * step)) < 0.1 * step:
                marks.append((t, ylabels[k]))
    if len(marks) < 3:
        raise ValueError(f"only {len(marks)} y marks found")
    ay, by, my = fit(marks)
    rows = [m[0] for m in marks]
    need = 2 if isinstance(xlabels, dict) else \
        max([int(k.split(":")[1]) + 1 for _, k in xlabels if k.startswith("tick:")] + [0])
    xt = sorted(major(x_ticks(img, fr, side=xticks_side)))
    if len(xt) < need:  # curves lying on the bottom frame hide its ticks: use the mirrored ones on top
        xt = sorted(major(x_ticks(img, fr, side="top" if xticks_side == "bottom" else "bottom")))
    xm = []
    if isinstance(xlabels, dict):
        # evenly spaced labelled ticks, anchored on a labelled frame line: each major tick found
        # takes the label its distance from the anchor gives (the tick spacing measured)
        av, akind = xlabels["anchor"]
        apx = fr["right"] if akind == "frame-right" else fr["left"]
        sp = float(np.median(np.diff(xt)))
        xm.append((apx, av))
        for p in xt:
            k = (p - apx) / sp
            if abs(k - round(k)) < 0.1:
                xm.append((p, av + round(k) * xlabels["step"]))
        xlabels = []
    for v, kind in xlabels:
        if kind == "frame-left":
            xm.append((fr["left"], v))
        elif kind == "frame-right":
            xm.append((fr["right"], v))
        else:
            xm.append((xt[int(kind.split(":")[1])], v))
    ax, bx, mx = fit(xm)
    return dict(fr=fr, ay=ay, by=by, my=my, ax=ax, bx=bx, mx=mx, ny=len(rows), nx=len(xm), xt=xt, yt=yt)


def to_col(cal, x):
    return (x - cal["ax"]) / cal["bx"]


def to_val(cal, row):
    return cal["ay"] + cal["by"] * row


def level(img, cal, col, rgb, tol, win=25, rows=None):
    """The row of a horizontal stretch of a line of colour `rgb` around column `col`.
    Returns (centre row, half thickness, n columns used, touches_frame). `rows`: the value
    range the line lies in (to leave out a legend's sample line)."""
    m = colour_mask(img, rgb, tol)
    fr = cal["fr"]
    m[:int(fr["top_in"]) + 1] = False
    m[int(fr["bottom_in"]):] = False
    if rows:
        r0, r1 = (min(max(int(to_row(cal, v)), 0), m.shape[0]) for v in rows)
        m[:min(r0, r1)] = False
        m[max(r0, r1):] = False
    cs, hs, tops, touch, cols = [], [], [], False, []
    for c in range(int(col - win), int(col + win) + 1):
        runs = [r for r in column_runs(m[:, c]) if r[1] - r[0] >= 2]
        if not runs:
            continue
        r = max(runs, key=lambda q: q[1] - q[0])
        cols.append(c)
        cs.append((r[0] + r[1]) / 2.0)
        hs.append((r[1] - r[0] + 1) / 2.0)
        tops.append(r[0])
        if r[1] >= fr["bottom_in"] - 2:
            touch = True
    if not cs:
        return None
    slope = float(np.polyfit(cols, cs, 1)[0]) if len(cs) >= 5 else 0.0
    return dict(row=float(np.median(cs)), half=float(np.median(hs)), top=float(np.median(tops)),
                n=len(cs), touch=touch, slope=slope)


def read_lines(img, at, spec):
    """Read one coloured line (a step profile or a curve) at the x positions `at`.

    The value is the centre of the line's colour run, the median over a window of columns
    around the position. Where the run reaches the bottom frame line (the line lies on the
    frame), its lower edge is hidden: the centre is taken as its upper edge plus the line's
    half thickness measured where it is clear, and the interval reaches down to the frame.
    95% interval: two pixels for placing the centre, plus the calibration misfit."""
    cal = calibrate(img, spec["ylabels"], spec["xlabels"], yside=spec.get("yside", "left"),
                    tick_max=spec.get("tick_max"))
    out = []
    clear = []
    raw = []
    for x in at:
        col = to_col(cal, float(x))
        lv = level(img, cal, col, spec["rgb"], spec.get("tol", 40), spec.get("win", 25), spec.get("rows"))
        raw.append((float(x), col, lv))
        if lv and not lv["touch"]:
            clear.append(lv["half"])
    half_ref = float(np.median(clear)) if clear else None
    for x, col, lv in raw:
        if lv is None:
            out.append({"x": x, "y": None, "note": "no pixel of the line's colour near this position"})
            continue
        # placing the centre (2 px), the calibration misfit, and half the line's half-thickness
        # (a sloping or dashed line's centre is less sharp than a level one's)
        # and, on a sloping line, the rows that one pixel and the x misfit of position cover
        e = 2.0 + max(cal["my"], 0.5) + 0.5 * lv["half"] + abs(lv["slope"]) * (1.0 + max(cal["mx"], 0.5))
        row = lv["row"]
        note = (f"line centre over {lv['n']} columns; y {cal['ny']} marks misfit {cal['my']:.2f} px, "
                f"x {cal['nx']} marks misfit {cal['mx']:.2f} px")
        lo_row, hi_row = row + e, row - e
        if lv["touch"] and half_ref is not None:
            row = lv["top"] + half_ref
            lo_row = cal["fr"]["bottom"] + e
            hi_row = lv["top"] + half_ref - e
            note += "; the line lies on the bottom frame line: centre from its upper edge, interval down to the frame"
        y, lo, hi = to_val(cal, row), to_val(cal, lo_row), to_val(cal, hi_row)
        rec = {"x": x, "y": float(y), "lo": float(min(lo, hi)), "hi": float(max(lo, hi)),
               "px": [float(col), float(row)], "note": note}
        if spec.get("band_rgb"):
            # the shaded band around the line (its min-max range): the run of the band's colour,
            # or of any line drawn over it, through the line's centre, column by column over the
            # window; the band's ends are the medians of the runs' ends
            bm = colour_mask(img, spec["band_rgb"], spec.get("band_tol", 30))
            for o in spec.get("band_over", []):
                bm |= colour_mask(img, o, spec.get("tol", 40))
            bm = _inside(bm, cal["fr"])
            # antialiased edges between a line and the band match neither colour: close gaps of
            # up to 6 rows
            from scipy.ndimage import binary_closing
            bm = binary_closing(bm, structure=np.ones((7, 1), bool)) & _inside(np.ones_like(bm), cal["fr"])
            tops, bots = [], []
            for c in range(int(col - 10), int(col + 11)):
                r = _run_through(bm[:, c], int(round(row)))
                if r:
                    tops.append(r[0])
                    bots.append(r[1])
            if tops:
                t_r, b_r = float(np.median(tops)), float(np.median(bots))
                eb = 3.0 + max(cal["my"], 0.5)
                rec.update({"bar_hi": float(to_val(cal, t_r)), "bar_lo": float(to_val(cal, b_r)),
                            "bar_hi_outer": float(to_val(cal, t_r - eb)), "bar_lo_outer": float(to_val(cal, b_r + eb)),
                            "px_lo": t_r, "px_hi": b_r})
                rec["note"] += f"; shaded band rows {t_r:.0f}-{b_r:.0f}"
                fr = cal["fr"]
                if b_r >= fr["bottom_in"] - 2:
                    rec["bar_lo_outer"] = float(to_val(cal, fr["bottom_in"] + 400))
                    rec["note"] += "; the band runs past the bottom frame: its lower end is not shown (outer end set far below)"
                if t_r <= fr["top_in"] + 2:
                    rec["bar_hi_outer"] = float(to_val(cal, fr["top_in"] - 400))
                    rec["note"] += "; the band runs past the top frame: its upper end is not shown (outer end set far above)"
        out.append(rec)
    return out


def _inside(m, fr):
    m[:int(fr["top_in"])] = False
    m[int(fr["bottom_in"]) + 1:] = False
    m[:, :int(fr["left_in"])] = False
    m[:, int(fr["right_in"]) + 1:] = False
    return m


def _run_through(col, r):
    """Start and end of the run of True in a boolean column that contains row r, or None."""
    if not col[r]:
        return None
    a = r
    while a > 0 and col[a - 1]:
        a -= 1
    b = r
    while b < len(col) - 1 and col[b + 1]:
        b += 1
    return a, b


def read_markers(img, at, spec):
    """Read open markers (squares or triangles) of one colour with optional error bars.

    `at` lists the categories to read (here: rows of cells, the integer x labels). Each is
    searched for in a window of +-0.4 category around its tick: the marker is the connected
    blob of the colour whose outline has the tallest vertical extent away from the error bar;
    its centre row is the middle of its two vertical outline sides (the outline of the marker is
    found column by column: the outermost columns where the colour runs at least `edge_min`
    pixels tall). Pixels of colours drawn on top (`over`) count as the marker's colour when
    following an outline or a bar, so an overlying marker does not cut them.
    Error bar: the column through the marker's centre with the most colour pixels; the bar is
    the run of the colour (and of `over` colours) through the marker along that column; its
    ends are its first and last rows. 95% interval of the centre: 2 px plus the calibration
    misfit; bar ends are widened by 3 px plus the misfit."""
    if spec.get("shape", "").startswith("triangle") and "_hw" not in spec:
        # first pass: the height-to-width ratio of the triangles whose outline is whole
        hws, strokes = [], []
        read_markers(img, at, dict(spec, _hw=0.95, _collect=hws, _strokes=strokes))
        typ = (float(np.median([s[0] for s in strokes])), float(np.median([s[1] for s in strokes]))) if strokes else None
        spec = dict(spec, _hw=float(np.median(hws)) if hws else 0.95, _typical=typ)
    spec = dict(spec)
    cal = calibrate(img, spec["ylabels"], spec["xlabels"], yside=spec.get("yside", "left"))
    fr = cal["fr"]
    own = _inside(colour_mask(img, spec["rgb"], spec.get("tol", 60)), fr)
    any_ = own.copy()
    for o in spec.get("over", []):
        any_ |= _inside(colour_mask(img, o, spec.get("tol", 60)), fr)
    if spec.get("rows"):
        # the value range where the data lie: the legend's sample marker lies outside it
        r0, r1 = (min(max(int(to_row(cal, v)), 0), own.shape[0]) for v in spec["rows"])
        for m in (own, any_):
            m[:min(r0, r1)] = False
            m[max(r0, r1):] = False
    unit = abs(1.0 / cal["bx"])
    out = []
    for x in at:
        xv = float(x)
        c0 = to_col(cal, xv)
        lo_c, hi_c = int(c0 - 0.4 * unit), int(c0 + 0.4 * unit)
        sub = own[:, lo_c:hi_c]
        if sub.sum() < 50:
            out.append({"x": xv, "y": None, "note": "no marker of this colour near this category"})
            continue
        # the bar or the marker's centre column: the column with the most colour pixels
        counts = sub.sum(axis=0)
        # the marker's (and its bar's) centre column: the middle of the columns its colour covers
        # (markers drawn under others: the column with the most of the colour, which is the bar)
        on = np.where(counts >= 5)[0]
        if spec.get("centre") == "longest":
            cbar = lo_c + int(np.argmax(counts))
        else:
            cbar = lo_c + int(round((on[0] + on[-1]) / 2.0))
        shape = spec.get("shape", "square")
        left = right = []
        if shape == "square":
            # outline sides: columns whose longest run (own or overlying colour) is tall
            edge_min = spec.get("edge_min", 25)
            best = []
            for c in range(lo_c, hi_c):
                if abs(c - cbar) < spec.get("bar_half", 8):
                    continue
                col = any_[:, c]
                runs = [r for r in column_runs(col) if r[1] - r[0] + 1 >= edge_min]
                # keep runs that touch this colour (not only overlying colours)
                runs = [r for r in runs if own[r[0]:r[1] + 1, c].sum() >= 0.3 * (r[1] - r[0] + 1)]
                for r in runs:
                    best.append((c, r))
            if not best:
                out.append({"x": xv, "y": None, "note": "marker outline not found"})
                continue
            left = [b for b in best if b[0] < cbar]
            right = [b for b in best if b[0] > cbar]
        if shape == "square" and left and right:
            # the outer sides: the leftmost and rightmost tall runs that overlap in rows
            # the outer side on the bar's left, and the right side that mirrors it about the bar
            L = min(left, key=lambda b: b[0])
            R = min(right, key=lambda b: (abs(b[0] - (2 * cbar - L[0])), -b[0]))
            a = max(L[1][0], R[1][0])
            b = min(L[1][1], R[1][1])
            centre = (a + b) / 2.0 if b > a else (L[1][0] + L[1][1] + R[1][0] + R[1][1]) / 4.0
            ccent = (L[0] + R[0]) / 2.0
            how = f"square sides at columns {L[0]} and {R[0]}, rows {a}-{b}"
            mk_rows = (min(L[1][0], R[1][0]), max(L[1][1], R[1][1]))
        else:
            # a triangle or a one-sided outline: centre of the vertical extent of the blob near the bar
            rows = np.where(own[:, max(cbar - 40, 0):cbar + 41].any(axis=1))[0]
            centre = float(np.median(rows))
            ccent = float(cbar)
            how = "blob centre"
            mk_rows = None
        if shape in ("triangle_down", "triangle_up"):
            # gnuplot's triangle points: the point is the triangle's centroid, a third of the
            # height from the flat side, and the height equals the width. The flat side is the
            # widest feature of the marker (wider than the caps): the rows where this colour spans
            # the most columns around the bar. Centre = flat side's centre row + (width - 1.7 t)/3
            # towards the apex, t the line thickness (the outer width includes the mitred corners).
            win = own[:, cbar - 70:cbar + 71]
            ext = np.zeros(win.shape[0])
            for r in np.where(win.any(axis=1))[0]:
                cs = np.where(win[r])[0]
                ext[r] = cs[-1] - cs[0] + 1
            W = ext.max()
            flat = np.where(ext >= 0.85 * W)[0]
            # the flat side nearest to the bar's middle (one marker per category)
            groups = []
            for r in flat:
                if groups and r - groups[-1][-1] <= 2:
                    groups[-1].append(r)
                else:
                    groups.append([r])
            g0 = max(groups, key=len)
            strokes = spec.setdefault("_strokes", [])
            if spec.get("_typical") and (len(g0) < 0.7 * spec["_typical"][0] or W < 0.95 * spec["_typical"][1]):
                out.append({"x": xv, "y": None,
                            "note": f"the flat side is cut by an overlying marker (rows {g0[0]}-{g0[-1]}, "
                                    f"width {int(W)} px): not read"})
                continue
            strokes.append((len(g0), W))
            sgn = 1 if spec["shape"] == "triangle_down" else -1
            # the outer outline is a triangle with the same centroid: its flat side is the outer
            # edge of the flat stroke; its apex is where its width, falling linearly along the
            # slanted sides, reaches zero (a line fitted to the width row by row)
            a_out = g0[0] if sgn > 0 else g0[-1]
            start = (g0[-1] if sgn > 0 else g0[0]) + sgn * 3
            rr = [start + sgn * k for k in range(0, int(0.45 * W))]
            pts = [(r, ext[r]) for r in rr if 0 <= r < len(ext) and ext[r] > 0.25 * W]
            apex = None
            if len(pts) >= 5:
                b1, b0 = np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)
                apex = -b0 / b1
                if not 0.7 * W < sgn * (apex - a_out) < 1.2 * W:
                    apex = None  # the outline is cut by another marker: height from the others
            if spec.get("apex") == "typical" and "_collect" not in spec:
                # every triangle has the same size: the apex from the median height-to-width ratio
                # of the triangles whose outline is whole (a cap or marker over one apex then does
                # not move it)
                apex = None
            if apex is None:
                apex = a_out + sgn * spec.get("_hw", 0.95) * W
                fitted = False
            else:
                fitted = True
                if "_collect" in spec:
                    spec["_collect"].append(sgn * (apex - a_out) / W)
            # where the point lies in its triangle is not printed: at its centroid (a third of
            # the height from the flat side) or at the middle of its height. The value is taken
            # halfway between, and its interval spans both, plus the 2 px of placing them.
            c3 = a_out + (apex - a_out) / 3.0
            c2 = a_out + (apex - a_out) / 2.0
            centre = (c3 + c2) / 2.0
            tri_span = abs(c2 - c3) / 2.0
            if spec.get("point") == "centroid":
                # gnuplot draws its triangle points with the point a third of the height from the
                # flat side (vertices at +4/3 and -2/3 of the tick size): the centroid; the
                # interval adds 3 px for the outline's stroke at the flat side and apex
                centre = c3
                tri_span = 3.0
            ccent = float(cbar)
            mk_rows = (min(a_out, apex), max(a_out, apex))
            how = (f"triangle flat side at rows {g0[0]}-{g0[-1]}, width {int(W)} px, apex row {apex:.0f}"
                   + ("" if fitted else " (apex from the markers' median height-to-width ratio)"
                      if spec.get("apex") == "typical"
                      else " (outline cut: apex from the other markers' height-to-width ratio)")
                   + ("; the point at the triangle's centroid (gnuplot)" if spec.get("point") == "centroid"
                      else "; the point's place in the triangle (centroid or mid-height) spans the interval"))
        else:
            tri_span = 0.0
        e = 2.0 + max(cal["my"], 0.5) + tri_span
        y = to_val(cal, centre)
        rec = {"x": xv, "y": float(y), "lo": float(min(to_val(cal, centre + e), to_val(cal, centre - e))),
               "hi": float(max(to_val(cal, centre + e), to_val(cal, centre - e))),
               "px": [float(ccent), float(centre)],
               "note": f"{how}; y {cal['ny']} marks misfit {cal['my']:.2f} px, x {cal['nx']} marks misfit {cal['mx']:.2f} px"}
        if spec.get("error_bars"):
            # a bar of a dashed line style, partly under other markers: follow only this colour
            # and close the gaps (dashes, overlying markers) up to `dash_gap` rows
            src = own if spec.get("bar_own_only") else any_
            band = src[:, cbar - 2:cbar + 3].any(axis=1)
            gap = spec.get("dash_gap", 0)
            if gap:
                # a dashed bar: close the gaps between dashes, up to `gap` rows
                closed = band.copy()
                idx = np.where(band)[0]
                for p, q in zip(idx[:-1], idx[1:]):
                    if 1 < q - p <= gap + 1:
                        closed[p:q] = True
                band = closed
            r_c = int(round(centre))
            if not band[r_c]:
                near = np.where(band[max(r_c - 30, 0):r_c + 31])[0]
                if len(near):
                    r_c = max(r_c - 30, 0) + int(near[np.argmin(np.abs(near - 30))])
            run = _run_through(band, r_c)
            if run is not None and (run[1] - run[0]) > 0:
                top_r, bot_r = float(run[0]), float(run[1])
                cut_top = run[0] <= fr["top_in"] + 2
                # each end carries a cap: a horizontal stroke wider than the bar; the bar's end
                # is the middle of the cap's rows
                widths = any_[:, cbar - 40:cbar + 41].sum(axis=1)
                barw = float(np.median(widths[int(top_r) + 15:int(centre) - 45])) if centre - top_r > 70 else 8.0
                capped, hidden_under = [], []
                for end, sgn in ((top_r, 1), (bot_r, -1)):
                    cap, k = [], 0
                    while k < 25:
                        r = int(end) + sgn * k
                        wide = 0 <= r < len(widths) and widths[r] > 2.5 * max(barw, 4.0)
                        if wide:
                            cap.append(r)
                        elif cap or k > 6:
                            break
                        k += 1
                    beyond = int(end) - sgn * 3
                    overlay = any_ & ~own
                    if not cap and 0 <= beyond < overlay.shape[0] and overlay[beyond, cbar - 2:cbar + 3].any():
                        # the bar runs on under a marker drawn on top: its end is hidden somewhere
                        # under it; the outer interval reaches that marker's far edge
                        ob = overlay[:, cbar - 2:cbar + 3].any(axis=1)
                        far = _run_through(ob, beyond)
                        hidden_under.append((sgn, float(far[0] if sgn > 0 else far[1])))
                        capped.append(end)
                    elif cap:
                        capped.append(float(np.mean(cap)))
                    else:
                        # no wider cap row told apart: the end is half a stroke inside the
                        # outermost pixel (the stroke's thickness: the bar's own width)
                        ws = [int(src[r, cbar - 30:cbar + 31].sum()) for r in range(int(top_r), int(bot_r) + 1)
                              if 0 < src[r, cbar - 30:cbar + 31].sum() <= 40]
                        sw = float(np.median(ws)) if ws else 8.0
                        capped.append(end + sgn * sw / 2.0)
                top_r, bot_r = capped
                # an end inside the marker's outline is hidden by it: reported as the marker's edge
                hidden = []
                if mk_rows is not None:
                    a_m, b_m = mk_rows
                    if top_r >= a_m - 4:
                        top_r = float(a_m)
                        hidden.append("upper")
                    if bot_r <= b_m + 4:
                        bot_r = float(b_m)
                        hidden.append("lower")
                eb = 3.0 + max(cal["my"], 0.5)
                hi_v, lo_v = to_val(cal, top_r), to_val(cal, bot_r)
                rec.update({"bar_lo": float(lo_v), "bar_hi": float(hi_v),
                            "bar_lo_outer": float(to_val(cal, bot_r + eb)),
                            "bar_hi_outer": float(to_val(cal, top_r - eb)),
                            "px_lo": top_r, "px_hi": bot_r})
                rec["note"] += f"; error bar along column {cbar}, rows {int(top_r)}-{int(bot_r)}"
                if hidden:
                    rec["note"] += f"; {' and '.join(hidden)} end hidden inside the marker: reported as at most the marker's edge"
                for sgn, far in hidden_under:
                    if sgn > 0:
                        rec["bar_hi_outer"] = float(to_val(cal, far - eb))
                        rec["note"] += "; upper end runs under a marker drawn on top: outer end at that marker's far edge"
                    else:
                        rec["bar_lo_outer"] = float(to_val(cal, far + eb))
                        rec["note"] += "; lower end runs under a marker drawn on top: outer end at that marker's far edge"
                if cut_top:
                    # the cap lies under the top frame line: its middle may be hidden; the outer
                    # interval reaches the frame line's upper edge
                    rec["bar_hi_outer"] = float(to_val(cal, fr["top"] - fr["half"] - eb))
                    rec["note"] += "; the bar reaches the top frame line: its cap is partly hidden, outer end to the frame's upper edge"
        out.append(rec)
    return out


def to_row(cal, v):
    return (v - cal["ay"]) / cal["by"]


def column_runs(col):
    """Runs of True in a boolean column: list of (start, end_inclusive)."""
    idx = np.where(col)[0]
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i != p + 1:
            out.append((s, p))
            s = i
        p = i
    out.append((s, p))
    return out
