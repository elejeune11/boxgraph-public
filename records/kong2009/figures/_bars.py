"""Shared reading code for this record's bar charts (Fig. 2, Figs. S2 and S3).

The panels are vector plots: an L-shaped pair of axes, the y axis with outward
ticks on its left, and bars standing on the x axis, drawn as a dark outline that
is empty (open bars), filled black (closed bars) or filled with diagonal lines
(hatched bars). Bars may touch their neighbours. An SEM bar is a vertical stem
centred on the bar with a short horizontal cap at each end.

Everything is found in the rendered crop. A reading file supplies only the
printed y tick labels it matched (bottom to top), which kind of bar to report
and, optionally, regions (legends) where bars are not to be looked for.

A bar's value is the centre line of its top edge (the outline is drawn centred on
the value, as the x axis line is centred on the 0 tick); an error bar's end is the
centre line of its cap. x is the bar's position, numbered from 1 at the left
among the bars of the kind asked for.
"""

import numpy as np

import _lt


def _dark(img):
    return _lt.gray(img) < 110


def _line_width(black, ycols):
    return ycols[1] - ycols[0] + 1


def calibrate(img, y_labels):
    black = _dark(img)
    ycols, xrows = _lt.find_axes(black)
    yr, _ = _lt.y_ticks(black, ycols, xrows)
    ya = _lt.YAxis(yr, [list(y_labels)])
    return black, ycols, xrows, ya


def find_bars(black, ycols, xrows, exclude=(), min_w=120, gap=60):
    """Every bar standing on the x axis: dict(left, right, top, top_lw, kind).

    A bar's top is a long horizontal run of pixels that are dark with light above them
    (the error-bar stem, dark above, interrupts it: gaps up to `gap` px are bridged).
    Touching bars of different heights each keep their own top. Error-bar caps, text and
    legend boxes are shorter than `min_w`."""
    H, W = black.shape
    lw = _line_width(black, ycols)
    base = xrows[0]
    mask = black.copy()
    for (fx0, fy0, fx1, fy1) in exclude:
        mask[int(fy0 * H):int(fy1 * H), int(fx0 * W):int(fx1 * W)] = False
    mask[:, :ycols[1] + 3] = False
    top_px = mask[1:base - 2] & ~mask[:base - 3]  # row r + 1 is dark, row r is light
    bars = []
    for r in range(top_px.shape[0]):
        runs = _lt._runs(top_px[r])
        merged = []
        for s, e in runs:
            if merged and s - merged[-1][1] <= gap:
                merged[-1][1] = e
            else:
                merged.append([s, e])
        for s, e in merged:
            if e - s < min_w:
                continue
            # a bar stands on the axis: one of its sides runs dark from its top down to the axis
            near = list(range(s - lw, s + lw + 1)) + list(range(e - 1 - lw, e + lw))
            sides = [black[r + 1:base, c].mean() for c in near if 0 <= c < W]
            if max(sides) > 0.97:
                bars.append({"left": s, "right": e - 1, "top": r + 1})
    xl = xrows[1] - xrows[0] + 1
    for b in bars:
        w = b["right"] - b["left"]
        # the fill, judged left of the centre where an error-bar stem runs
        if w > 8 * lw:
            inner = black[b["top"] + 2 * lw:base - lw, b["left"] + 2 * lw:b["left"] + w // 3]
        else:  # a narrow bar (a histogram's), without a stem: all its inside
            inner = black[b["top"] + 2 * lw:base - lw, b["left"] + lw + 4:b["right"] - lw - 3]
        f = float(inner.mean()) if inner.size else 1.0
        b["fill"] = f
        b["kind"] = "open" if f < 0.03 else ("closed" if f > 0.85 else "hatched")
        if b["kind"] == "closed":
            b["top_lw"] = xl  # the outline of a filled bar cannot be seen: take the axis line's width
            continue
        # the top edge: the run of dark rows at the bar's top, at columns clear of the stem
        th = []
        for c in np.linspace(b["left"] + 2 * lw, b["left"] + w // 3, 7).astype(int):
            r = b["top"]
            while r < base and black[r, c]:
                r += 1
            th.append(r - b["top"])
        b["top_lw"] = int(np.min(th))  # hatching joins the edge in places; the thinnest is the edge
    # a filled bar's outline is drawn as the other bars' outlines in the panel
    seen = [b["top_lw"] for b in bars if b["kind"] != "closed"]
    if seen:
        for b in bars:
            if b["kind"] == "closed":
                b["top_lw"] = int(round(np.median(seen)))
    return sorted(bars, key=lambda b: b["left"]), lw


def _stem_col(black, b, lw):
    """The column of the error-bar stem above the bar, or None if none shows."""
    mid = (b["left"] + b["right"]) / 2
    half = (b["right"] - b["left"]) / 4
    row = b["top"] - 3
    cols = [c for c in range(int(mid - half), int(mid + half) + 1) if black[row, c]]
    if not cols:
        return None
    runs = _lt._runs(np.isin(np.arange(black.shape[1]), cols))
    s, e = min(runs, key=lambda se: abs((se[0] + se[1] - 1) / 2 - mid))
    return (s + e - 1) / 2, e - s


def _cap_centre(black, col, end_row, step, stem_w, stop):
    """Walking from `end_row` back towards the bar (row `stop` is not reached), the rows where
    the mark is wider than the stem form the cap; return the cap's centre row and thickness."""
    rows = []
    r = end_row
    c = int(round(col))
    while 0 <= r < black.shape[0] and black[r, c] and (r - stop) * step < 0:
        left = right = 0
        while black[r, c - left - 1]:
            left += 1
        while black[r, c + right + 1]:
            right += 1
        if left + right + 1 > 2.5 * stem_w:
            rows.append(r)
        elif rows:
            break
        r += step
    if not rows:
        return None
    return (min(rows) + max(rows)) / 2, max(rows) - min(rows) + 1


def read_panel(image, at, y_labels, kind, exclude=(), bars=True, hidden_lower="mirror", x_labels=None,
               min_w=120):
    """Read the bars of one kind. With `x_labels` (the printed x tick labels, left to right), x is the
    bar's centre on the calibrated x axis; without, x is its position, numbered from 1 at the left."""
    black, ycols, xrows, ya = calibrate(image, y_labels)
    found, lw = find_bars(black, ycols, xrows, exclude, min_w=min_w)
    xa = None
    if x_labels is not None:
        xc = _lt.x_ticks(black, ycols, xrows)
        if len(xc) != len(x_labels):
            raise ValueError(f"found {len(xc)} x ticks at columns {[round(c) for c in xc]}, expected {len(x_labels)}")
        xa = _lt.Linear(list(zip(sorted(xc), x_labels)))
    seg = ya.segs[0]
    per_px = abs(seg.b)
    cal = ya.misfit_px
    out = []
    mine = [b for b in found if b["kind"] == kind]
    for i, b in enumerate(mine, start=1):
        row = b["top"] + (b["top_lw"] - 1) / 2
        col = (b["left"] + b["right"]) / 2
        tol_px = 2.0 + cal  # the centre of a 12-16 px edge, and the tick misfit
        y = seg.value(row)
        x = float(i) if xa is None else round(float(xa.value(col)), 2)
        r = {"x": x, "y": float(y), "lo": float(y - tol_px * per_px), "hi": float(y + tol_px * per_px),
             "px": [float(col), float(row)], "px_lo": float(row - tol_px), "px_hi": float(row + tol_px),
             "note": f"{kind} bar {i} from the left, columns {b['left']}-{b['right']}; top edge {b['top_lw']} px thick"}
        if bars:
            eb = _error_bar(black, b, lw, seg, per_px, cal, hidden_lower)
            note = eb.pop("bar_note")
            r.update(eb)
            r["note"] += f"; SEM {eb['bar_lo']:.4f} to {eb['bar_hi']:.4f}" + (f" ({note})" if note else "")
        out.append(r)
    return out


def _error_bar(black, b, lw, seg, per_px, cal, hidden_lower):
    st = _stem_col(black, b, lw)
    top_c = b["top"] + (b["top_lw"] - 1) / 2
    y_top = seg.value(top_c)
    if st is None:
        # no stem above the top edge: the bar is hidden in the edge
        half = (b["top_lw"] / 2) * per_px
        return {"bar_lo": y_top - half, "bar_hi": y_top + half, "bar_lo_outer": y_top - half - per_px,
                "bar_hi_outer": y_top + half + per_px,
                "bar_note": "SEM bar hidden in the bar's top edge: at most half the edge's thickness"}
    col, sw = st
    # upper end: the topmost dark row of the stem, then its cap
    r = b["top"] - 1
    c = int(round(col))
    while r > 0 and black[r - 1, c]:
        r -= 1
    lo = None
    lo_note = ""
    if sw > 2 * lw:
        # what stands on the top edge is the cap itself (the stem is hidden): the cap's lower rows
        # merge with the edge, so its thickness is taken as the edge's
        up_row = r + (b["top_lw"] - 1) / 2
        lo_note = "the cap sits on the top edge, its stem hidden; the cap's thickness taken as the edge's"
    else:
        up = _cap_centre(black, col, r, 1, sw, b["top"])
        up_row = up[0] if up else r + 0.5 * sw
    hi = seg.value(up_row)
    if b["kind"] == "open":
        # the stem goes on below the top edge, inside the empty bar
        r = b["top"] + b["top_lw"]
        if black[r + 2, c]:
            while black[r + 1, c]:
                r += 1
            dn = _cap_centre(black, col, r, -1, sw, b["top"] + b["top_lw"] - 1)
            if dn:
                lo = seg.value(dn[0])
        else:
            lo_note = "no stem below the top edge: the lower half is hidden in the edge"
            lo = seg.value(top_c + b["top_lw"] / 2)
    if lo is None:
        lo = 2 * y_top - hi
        lo_note = "; ".join(n for n in (lo_note, f"lower half hidden in the {b['kind']} bar: taken as the mirror "
                                         "of the upper") if n)
    w = (1.5 + cal) * per_px
    return {"bar_lo": float(lo), "bar_hi": float(hi), "bar_lo_outer": float(lo - w), "bar_hi_outer": float(hi + w),
            "bar_note": lo_note}
