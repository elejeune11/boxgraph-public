"""Shared reading code for the measured-data figures of panzetta2019 (Excel charts pasted as
raster images): MSD curves on log-log axes (Figs. 2, 4, 5, S4-S6), bar charts with error bars
(Figs. 3, 6, 7, S3-S5, S7, S8, S10) and histograms (Fig. S9). (Fig. S1 is read by _fig.py.)

Axes. The spines: the leftmost long dark grey vertical line (as in _fig.py) and, for bar charts,
the lowest row whose dark pixels of any colour run across 40% of the width (the bars stand on the
axis and hide it).
  * Log-log MSD panels: Excel draws a log axis' line from its minimum to its maximum, so the
    left spine's column is 0.1 s and the right end of the bottom spine 10 s; the bottom spine's
    row is 10^-5 um^2 and the top end of the left spine 10^-2 (the printed end labels). The small
    tick marks at the inner decades (left of the y spine, below the x spine) are the check: each
    must fall on its predicted pixel. The largest residual (at least 2 px, for a spine end on an
    antialiased raster) is the misfit, added to every interval.
  * Linear axes (bars, histograms): from the tick marks pointing left from the y spine when there
    are at least as many as printed labels and they fit within 3 px; otherwise from the printed
    labels' centres (Excel centres each label on its value), searched left of any ticks. Least
    squares; the misfit is the largest residual (at least 1 px). Where a panel has both (Fig. 3A),
    the label centres sit about 9 px (1200 dpi) below their ticks, so a label-calibrated axis adds
    9 px to its misfit.

Series (lines with small markers). The pixels nearest the series' colour, followed by
continuity (_fig._trace, at most 8 px of jump per column), so that a neighbouring line is not
followed; where a line is hidden under another for long stretches it is read without tracing
(every pixel of its colour). At x: the centre of the line's pixels in the columns within 2 px, or
an interpolation across a gap of at most 40 px; the 95% interval adds half the line's extent
there, half an interpolated jump, the y misfit, 1 px and the local slope times the x misfit.

Bars. In a band of 30 rows just above the baseline, averaged over 9 columns (so that a hatched
bar is still grey), the runs of non-white columns are the bars, split where the colour changes
(bars of a group touch). Bars are taken left to right as indices 1, 2, ... The value is the top
edge: per column away from the centre, going up from the baseline, the first stretch of
background (white on an image averaged over 9 rows and 15 columns, which bridges a hatch) ends
the bar; the edge is the centre of the dark grey outline if the bar has one, otherwise the first
bar row plus 3 px (half a pixel of the pasted raster); the median over the columns.
Error bars: the stem is the column, in the middle 40% of the bar, with the longest unbroken run
of dark ink going up from the top edge (an asterisk above is separated by white). The top of that
run (the cap) is the upper end; below the top edge, ink that is black or clearly darker than the
bar's own fill and that reaches past the outline gives the lower end. A lower end hidden in a
dark bar is taken as the mirror of the upper (and an upper end not found, as the mirror of the
lower); the note says which. SEM bars are symmetric: when the two halves read differ by more than
4 px and 25%, the outer interval covers the longer half on both sides.
Intervals (95%): value +-(1.5 px + misfit + half the spread of the edge over the columns); each
error-bar end +-(2 px + misfit) for the outer interval.
"""
import importlib.util
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("panzetta2019_fig_shared", Path(__file__).with_name("_fig.py"))
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def _groups(idx, gap=1):
    return F._groups(idx, gap)


# ------------------------------------------------------------------ log-log axes from the spines

def loglog_axes(img, xlim=(0.1, 10.0), ylim=(1e-5, 1e-2), spine_thr=200):
    sp = F.spines(img, spine_thr)
    L, B = sp["left"], sp["bottom"]
    xl = 0.5 * (L["c0"] + L["c1"] + 1)
    xr = B["c1"] + 0.5
    yb = 0.5 * (B["r0"] + B["r1"] + 1)
    yt = L["r0"] - 0.5
    ux, uy = np.log10(xlim), np.log10(ylim)
    bx = (xr - xl) / (ux[1] - ux[0])
    by = (yt - yb) / (uy[1] - uy[0])
    xa = {"a": xl - bx * ux[0], "b": bx, "scale": "log10"}
    ya = {"a": yb - by * uy[0], "b": by, "scale": "log10"}
    checks = []
    # the small tick marks at the inner decades: outside the spines (left of the y spine, below
    # the x spine); each must fall on its predicted pixel
    g = F.gray(img)
    ty = g[:, max(L["c0"] - 10, 0):L["c0"] - 1].min(axis=1) < spine_thr
    for grp in _groups(np.where(ty[L["r0"] + 15:int(yb) - 15])[0] + L["r0"] + 15, gap=2):
        r = (grp[0] + grp[-1] + 1) / 2.0
        v = (r - ya["a"]) / ya["b"]
        k = round(v)
        if abs(v - k) < 0.25 and len(grp) <= 12:
            checks.append(("y tick", 10.0 ** k, r - F.to_px(ya, 10.0 ** k)))
    tx = g[B["r1"] + 2:B["r1"] + 11, :].min(axis=0) < spine_thr
    for grp in _groups(np.where(tx[int(xl) + 15:int(xr) - 15])[0] + int(xl) + 15, gap=2):
        c = (grp[0] + grp[-1] + 1) / 2.0
        v = (c - xa["a"]) / xa["b"]
        k = round(v)
        if abs(v - k) < 0.25 and len(grp) <= 12:
            checks.append(("x tick", 10.0 ** k, c - F.to_px(xa, 10.0 ** k)))
    res = max([2.0] + [abs(c[2]) for c in checks])
    xa["misfit"] = res
    ya["misfit"] = res
    box = (L["c1"] + 1, L["r0"], B["c1"], B["r0"])
    return {"x": xa, "y": ya, "box": box, "checks": checks}


def _y_digit_centres(img, sp, thr=130):
    m = (F.gray(img) < thr) & (F.sat(img) < 80)
    c_end = sp["left"]["c0"] - 6
    present = m[:, :c_end].any(axis=0)
    blk = F._block(present, c_end - 1, -1, 12, m.shape[1])
    if blk is None:
        return []
    w = blk[1] - blk[0] + 1
    # the "10" body is the left part of the label; the superscript sits right and higher
    cols = slice(blk[0], blk[0] + max(int(0.55 * w), 4))
    rows = m[:, cols].any(axis=1)
    out = []
    for g in _groups(np.where(rows)[0], gap=3):
        if g[-1] - g[0] + 1 >= 15:
            out.append((g[0] + g[-1] + 1) / 2.0)
    return out


def read_line(img, at, cal, color, others, tol=80, max_jump=8, blank=(), inset=6, gap=40, trace=True):
    """trace=False: take every pixel of the colour per column (for a line that another line
    hides over long stretches, so that it cannot be followed); the extent then covers them all."""
    xa, ya = cal["x"], cal["y"]
    c0, r0, c1, r1 = cal["box"]
    oth = [o for o in others if tuple(o) != tuple(color)]
    m = F.colour_mask(img, [color], oth, tol)
    keep = np.zeros_like(m)
    keep[int(r0) + 2:int(r1) - inset, int(c0) + inset:int(c1)] = True
    for (a, b, c, d) in blank:
        keep[b:d, a:c] = False
    m &= keep
    if trace:
        cols = F._trace(m, 2, max_jump)
    else:
        cols = {c: v for c, v in F._columns(m).items() if m[:, c].sum() >= 3}
    out = []
    for x in at:
        col = float(F.to_px(xa, x))
        near = [c for c in cols if abs(c + 0.5 - col) <= 2]
        extra, how = 0.0, ""
        if near:
            top = min(cols[c][0] for c in near)
            bot = max(cols[c][1] for c in near)
            cen = 0.5 * (top + bot)
            ext = bot - top
        else:
            left = [c for c in cols if col - gap <= c + 0.5 < col]
            right = [c for c in cols if col < c + 0.5 <= col + gap]
            if not left or not right:
                out.append({"x": float(x), "y": None, "note": f"no pixel of this line within {gap} px on both sides"})
                continue
            cl_, cr_ = max(left), min(right)
            yl, yr = 0.5 * sum(cols[cl_]), 0.5 * sum(cols[cr_])
            w = (col - (cl_ + 0.5)) / (cr_ - cl_)
            cen = (1 - w) * yl + w * yr
            ext = max(cols[cl_][1] - cols[cl_][0], cols[cr_][1] - cols[cr_][0])
            extra = 0.5 * abs(yr - yl)
            how = f"; interpolated across a gap of {cr_ - cl_} columns"
        half = 0.5 * ext + extra + ya["misfit"] + 1.0
        side = sorted(c for c in cols if abs(c + 0.5 - col) <= 40)
        if len(side) > 2:
            ys_ = np.array([0.5 * sum(cols[c]) for c in side])
            half += abs(float(np.polyfit(np.array(side, float), ys_, 1)[0])) * xa["misfit"]
        a1, a2 = F.to_val(ya, cen - half), F.to_val(ya, cen + half)
        ck = ", ".join(f"{k}{'' if v is None else ' ' + format(v, 'g')} {r:+.1f}" for k, v, r in cal.get("checks", []))
        out.append({"x": float(x), "y": F.to_val(ya, cen), "lo": min(a1, a2), "hi": max(a1, a2),
                    "px": [col, cen], "px_lo": cen - half, "px_hi": cen + half,
                    "note": f"line extent {ext:.0f} px; axes from the spine ends, misfit {ya['misfit']:.1f} px "
                            f"(tick checks: {ck})" + how})
    return out


def read_msd(image, at, color, others, **kw):
    cal = loglog_axes(image, kw.pop("xlim", (0.1, 10.0)), kw.pop("ylim", (1e-5, 1e-2)))
    return read_line(image, at, cal, color, others, **kw)


# ------------------------------------------------------------------ linear y axis from labels

def bar_spines(img, thr=200, frac=0.4):
    """Spines of a bar chart: the left spine as in _fig.spines; the bottom one is the lowest row
    whose dark pixels (of any colour: the bars stand on the axis and hide it) run across 40% of
    the width."""
    g = F.gray(img)
    m = (g < thr) & (F.sat(img) < 60)
    H, W = m.shape
    vc = {}
    for c in range(W):
        n, s = F._longest(m[:, c], gap=80)
        if n >= frac * H and m[s:s + n, c].sum() >= 0.9 * n:
            vc[c] = (n, s)
    if not vc:
        raise ValueError("left spine not found")
    grp = _groups(list(vc), gap=2)[0]
    n, s = max(vc[c] for c in grp)
    left = {"c0": int(min(grp)), "c1": int(max(grp)), "r0": s, "r1": s + n}
    d = g < thr
    cnt = d[:, left["c1"] + 1:].sum(axis=1)
    rows = [r for r in np.where(cnt >= frac * W)[0] if F._longest(d[r, left["c1"] + 1:])[0] >= frac * W]
    if not rows:
        raise ValueError("bottom spine not found")
    grp = _groups(rows, gap=1)[-1]
    r1 = int(grp[-1])
    # the spine's own thickness: the dark grey run of the left spine's columns
    t = left["c1"] - left["c0"] + 1
    r0 = r1 - t + 1
    run = F._longest(d[r1, left["c1"] + 1:])
    bottom = {"r0": r0, "r1": r1, "c0": left["c1"] + 1 + run[1], "c1": left["c1"] + run[1] + run[0]}
    return {"left": left, "bottom": bottom}


def y_ticks(img, sp, thr=200, max_len=45):
    """Tick marks pointing left from the y spine: rows where a dark grey run starts at the spine and
    reaches 8 to max_len px left of it. Returns (row centres, tick length)."""
    m = (F.gray(img) < thr) & (F.sat(img) < 60)
    c0 = sp["left"]["c0"]
    rows, lens = [], []
    for r in range(sp["left"]["r0"] - 3, sp["bottom"]["r1"] + 3):
        n = 0
        while c0 - 1 - n >= 0 and m[r, c0 - 1 - n]:
            n += 1
        if 8 <= n <= max_len:
            rows.append(r)
            lens.append(n)
    cents = [(g[0] + g[-1] + 1) / 2.0 for g in _groups(rows, gap=1) if len(g) <= 14]
    return cents, (max(lens) if lens else 0)


def linear_y(img, labels, y_below=70, label_sat=80, spine_thr=200):
    """The y axis: from tick marks, when the chart has one per printed label; otherwise from the
    labels' centres (searched left of any tick marks)."""
    sp = bar_spines(img, spine_thr)
    ticks, tlen = y_ticks(img, sp, spine_thr)
    if len(ticks) >= len(labels):
        ya = F.fit_axis(ticks, labels, "linear")
        if ya["misfit"] <= 3.0:
            ya["how"] = f"tick marks ({len(ticks)} found)"
            return sp, ya
    sp2 = {"left": dict(sp["left"]), "bottom": sp["bottom"]}
    sp2["left"]["c0"] = sp["left"]["c0"] - tlen - 2
    ya = F.fit_axis(F.y_label_centres(img, sp2, below=y_below, smax=label_sat), labels, "linear")
    ya["how"] = "label centres"
    # Where a panel has both, the label centres sit up to about 9 px (at 1200 dpi) below their
    # tick marks (Fig. 3A, left: labels at 170, 545, ... against ticks at 161, 536, ...); a
    # label-calibrated axis carries that much more uncertainty, added to its misfit.
    ya["misfit"] = ya["misfit"] + 9.0
    return sp, ya


# ------------------------------------------------------------------ bars

def _is_black(img, thr=100):
    """Black ink (error bars): every channel dark. An error bar drawn over a blue bar shows as a very
    dark blue (about 0, 10, 60), so the test is the largest channel, not the saturation; the dark
    green fill (about 5, 90, 25) is kept out by its green excess."""
    f = img.astype(int)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    return (f.max(axis=2) < thr) & (g - np.maximum(r, b) < 40)


def find_bars(img, sp, row_up=12, min_w=25, white=232):
    """Bars: runs of non-white columns in a row just above the baseline, inside the plot."""
    B, L = sp["bottom"], sp["left"]
    r = B["r0"] - row_up
    g = F.gray(img)
    from scipy.ndimage import uniform_filter1d
    # a hatched bar is a pattern of thin lines on white: averaged over 30 rows and 9 columns it
    # is still grey
    band = uniform_filter1d(img[r - 30:r + 1].astype(float).mean(axis=0), 9, axis=0)
    nonwhite = band.mean(axis=1) < white
    nonwhite[:L["c1"] + 4] = False
    nonwhite[B["c1"] - 2:] = False
    runs = [(int(a[0]), int(a[-1]) + 1) for a in _groups(np.where(nonwhite)[0], gap=2)]
    # bars of a group touch: split a run where the (averaged) colour changes across 10 columns;
    # the cut is the middle of each stretch of change
    out = []
    for a, b in runs:
        ch = [c for c in range(a + 5, b - 5) if np.sqrt(((band[c + 5] - band[c - 5]) ** 2).sum()) > 40]
        cuts = [a] + [int(round(np.mean(grp))) for grp in _groups(ch, gap=2)] + [b]
        for s, e in zip(cuts[:-1], cuts[1:]):
            if e - s >= min_w:
                out.append((s, e))
    return out


def bar_top(img, a, b, sp, white=247, run=8):
    """Top edge of a bar: per column (away from the centre stem), going up from the baseline, the
    first stretch of `run` background rows (grey >= `white`; a pale bar's fill is darker, about
    242) ends the bar. If a dark outline (grey < 150) starts within 12 rows below that point, the
    edge is the outline's centre; otherwise the first bar row plus 3 px (half a pixel of the pasted
    raster, which is about 6 px here). The median over those columns."""
    from scipy.ndimage import uniform_filter
    g = F.gray(img)
    sat = F.sat(img)
    # a hatched bar's white gaps are bridged by averaging over 9 rows and 15 columns
    gs = uniform_filter(g, size=(9, 15))
    base = sp["bottom"]["r0"] - 3
    w = b - a
    cen = 0.5 * (a + b)
    cols = [c for c in range(a + max(3, w // 8), b - max(3, w // 8)) if abs(c + 0.5 - cen) > max(8, 0.18 * w)]
    tops = []
    for c in cols:
        r, bg = base, 0
        while r > 0:
            bg = bg + 1 if gs[r, c] >= white else 0
            if bg >= run:
                break
            r -= 1
        first = r + run
        # back on the unsmoothed image: the first non-background row near that point
        for k in range(max(first - 8, 0), first + 16):
            if g[k, c] < white:
                first = k
                break
        seg = np.where(sat[first:first + 16, c] < 50, g[first:first + 16, c], 255)
        dark = np.where(seg < 150)[0]
        if len(dark):
            d0 = dark[0]
            d1 = d0
            while d1 + 1 < len(seg) and seg[d1 + 1] < 150:
                d1 += 1
            tops.append(first + 0.5 * (d0 + d1 + 1))
        else:
            tops.append(first + 3.0)
    tops = np.array(tops, float)
    return float(np.median(tops)), float(np.percentile(tops, 90) - np.percentile(tops, 10))


def read_bars(image, at, labels, y_below=70, label_sat=80, n_expected=None, row_up=12, white=244,
              min_w=25, blank=(), stem_w=5, scale=1.0):
    """`scale`: the axis' printed multiplier (an "x10^-4" above the labels), applied to the labels."""
    labels = [v * scale for v in labels]
    img = image.copy()
    for (a, b, c, d) in blank:
        img[b:d, a:c] = 255
    sp, ya = linear_y(img, labels, y_below, label_sat)
    bars = find_bars(img, sp, row_up, min_w, white)
    if n_expected is not None and len(bars) != n_expected:
        raise ValueError(f"found {len(bars)} bars, expected {n_expected}: {bars}")
    blk = _is_black(img)
    # above a bar the background is white: a thin, antialiased stem or cap is dark grey there
    grey_ink = (F.gray(img) < 170) & (F.sat(img) < 50)
    gimg, simg = F.gray(img), F.sat(img)
    mis = ya["misfit"]
    lab = f"y axis from {ya['how']} at rows {[round(p) for p in ya['marks']]}, misfit {mis:.2f} px"
    out = []
    for x in at:
        i = int(round(float(x))) - 1
        if not 0 <= i < len(bars):
            out.append({"x": float(x), "y": None, "note": f"only {len(bars)} bars"})
            continue
        a, b = bars[i]
        top, spread = bar_top(img, a, b, sp)
        cen = 0.5 * (a + b)
        e1 = 1.5 + mis + 0.5 * spread
        rec = {"x": float(x), "y": F.to_val(ya, top), "lo": F.to_val(ya, top + e1), "hi": F.to_val(ya, top - e1),
               "px": [cen, top]}
        # error bar: black pixels in the central columns
        # the stem is near, not always at, the bar's centre: the column (within the middle 40% of
        # the bar) with the longest unbroken run of dark ink going up from just above the top edge
        # (an asterisk above the bar is separated from it by white; a hatched fill is below it)
        cand = range(int(cen - 0.2 * (b - a)), int(cen + 0.2 * (b - a)) + 1)
        ink = grey_ink | blk
        score = []
        for c in cand:
            r, n = int(top) - 7, 0
            while r > 0 and ink[r, c]:
                n += 1
                r -= 1
            score.append(n)
        sc = cand[int(np.argmax(score))] if max(score) > 0 else int(cen)
        cc = slice(sc - stem_w, sc + stem_w + 1)
        # inside the bar: ink is black, or grey clearly darker than the bar's own fill
        fill = float(np.median(gimg[int(top) + 20:sp["bottom"]["r0"] - 10, a + 5:b - 5]))
        inside = blk | ((gimg < fill - 50) & (simg < 70))
        rows = np.where(inside[:, cc].any(axis=1))[0]
        rows_a = np.where(grey_ink[:, cc].any(axis=1))[0]
        above = rows_a[(rows_a < top - 1) & (rows_a > sp["left"]["r0"] - 40)]
        if len(above):
            # the stem is continuous down to the bar: keep the group that touches the bar top
            gs = _groups(above, gap=3)
            gs = [gg for gg in gs if gg[-1] >= top - 6]
        else:
            gs = []
        below = rows[(rows >= top - 1) & (rows < sp["bottom"]["r0"] - 4)]
        bg = _groups(below, gap=3)
        bg = [gg for gg in bg if gg[0] <= top + 6]
        # a stem below the top edge must reach past the bar's outline (about 6 px) to count
        if gs:
            r_hi = float(gs[0][0]) + 1.0          # the cap's centre: about 1 px below its first row
            if bg and bg[0][-1] - top > 8:
                r_lo = float(bg[0][-1]) - 1.0
                how = "lower end read inside the bar"
            else:
                r_lo = 2 * top - r_hi
                how = "lower end hidden in the bar, taken as the mirror of the upper"
            eo = 2.0 + mis
            # mean +- SEM is symmetric: if the two halves read differ by more than 4 px and 25%, the
            # outer interval covers both halves mirrored (a half may be cut short where the ink
            # fades into the fill, or lengthened by an annotation touching the cap)
            up, dn = top - r_hi, r_lo - top
            wide = max(up, dn)
            if abs(up - dn) > max(4.0, 0.25 * wide):
                how += f"; the halves differ ({up:.0f} px up, {dn:.0f} px down): outer interval covers both mirrored"
                o_hi, o_lo = top - wide - eo, top + wide + eo
            else:
                o_hi, o_lo = r_hi - eo, r_lo + eo
            rec.update({"bar_hi": F.to_val(ya, r_hi), "bar_lo": F.to_val(ya, r_lo),
                        "bar_hi_outer": F.to_val(ya, o_hi), "bar_lo_outer": F.to_val(ya, o_lo),
                        "px_lo": r_lo, "px_hi": r_hi})
        elif bg and bg[0][-1] - top > 8:
            r_lo = float(bg[0][-1]) - 1.0
            r_hi = 2 * top - r_lo
            eo = 2.0 + mis
            how = "upper end not found above the bar; lower end read inside it, upper taken as its mirror"
            rec.update({"bar_hi": F.to_val(ya, r_hi), "bar_lo": F.to_val(ya, r_lo),
                        "bar_hi_outer": F.to_val(ya, r_hi - eo), "bar_lo_outer": F.to_val(ya, r_lo + eo),
                        "px_lo": r_lo, "px_hi": r_hi})
        else:
            how = "no error bar found: hidden within the top edge, at most the edge's width"
        rec["note"] = f"bar columns {a}-{b - 1}, top row {top:.1f} (spread {spread:.1f}); {how}; {lab}"
        out.append(rec)
    return out


def read_hist(image, at, labels, x_edges, y_below=70, label_sat=80, white=232):
    """Histogram bars touching each other: x positions are bin centres; the x axis is calibrated
    from the x labels (bin edges, printed), and the bar top is read in the bin's central columns."""
    sp, ya = linear_y(image, labels, y_below, label_sat)
    xa = F.fit_axis(F.x_label_centres(image, sp, col_gap=15, smax=label_sat), x_edges, "linear")
    out = []
    for x in at:
        col = F.to_px(xa, float(x))
        half_bin = 0.3 * abs(xa["b"]) * (x_edges[1] - x_edges[0])
        # the top edge as for a bar (bar_top: hatching bridged, outline centre)
        top, spread = bar_top(image, int(col - half_bin), int(col + half_bin), sp)
        e1 = 1.5 + ya["misfit"] + 0.5 * spread
        out.append({"x": float(x), "y": F.to_val(ya, top), "lo": F.to_val(ya, top + e1), "hi": F.to_val(ya, top - e1),
                    "px": [col, top], "px_lo": top + e1, "px_hi": top - e1,
                    "note": f"bin columns {int(col - half_bin)}-{int(col + half_bin)}, top row {top:.1f}; "
                            f"x labels misfit {xa['misfit']:.1f} px, y labels misfit {ya['misfit']:.2f} px"})
    return out
