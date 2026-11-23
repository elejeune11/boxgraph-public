"""Shared code for the left column of Supp. Fig. 2 of Owen et al. 2017 (PDF p. 25): one example
cell, seven stacked profiles against distance from the protrusion tip,
each a dark line (median) inside a grey band (the SD, as the caption says). Loaded with hash
pinning by the reading files, which give a CONFIG.

Only the left column is read. Its y tick labels are printed; the other five columns have tick
marks without labels at rows and spacings that differ from the left column's (each panel has its
own y limits), so no value can be assigned to them from the image.

Everything is found in the image; typed in are only the printed tick labels and which tick
stub each labels (CONFIG["yticks"]: [stub index from the top, value], or ["top", value] for a
label at the top end of the axis line).
- dark: grey level below 150 (the tick stubs are thin and lighter than the axis).
- panel (CONFIG["panel"] = c0, r0, c1, r1, a generous box around one panel): the y axis line is
  the column with the longest dark vertical run in the left third; its top and bottom rows are
  the y limits. Tick stubs: rows where 2-5 px right of the axis line is at least 70% dark.
- y: straight-line fit through the labelled stubs; misfit = the largest residual in px.
- x: the bottom panel of the column (CONFIG["xpanel"]) carries the printed x labels 0, 50, 100.
  0 is at its y axis line (the label sits under it); its one tick stub above the x axis line
  is 50 (labelled under it). The printed "100" has no tick: it sits at the end of the axis line,
  which by the 0-50 tick scale is at about 87.5 um (q_figS2_x_labels). The scale is taken from
  the ticks. All panels of the column share the axis column and width, so the same x scale is
  used for each; the difference of their y-axis columns is added to the x misfit, and 1.5 px for
  locating a tick with only two marks.
- value: in the column of x, the runs of band (grey 200-232, unsaturated) or line (dark) pixels,
  gaps up to 3 px bridged; of those holding line pixels, the one with most band pixels is the band
  (the cell rendering above the top panel reaches into it with dark streamlines and no band).
  `_kit.curve_value` on the line run nearest the band's centre gives y; the band's ends are the
  error bar (bar_lo/bar_hi; outer ends 1 px and twice the y misfit wider). If the band touches the top or bottom end of the axis it is
  cut by the axis limits there and its bar is dropped (noted).
"""
import numpy as np


def _axis(k, dark, c0, r0, c1, r1):
    best = (0, None, None, None)
    for c in range(c0, c0 + (c1 - c0) // 3):
        for a, b in k.runs(dark[r0:r1, c], 2):
            if b - a > best[0]:
                best = (b - a, c, a + r0, b + r0)
    _, c, top, bot = best
    cols = [cc for cc in range(c - 3, c + 4) if dark[top + 20:bot - 20, cc].mean() > 0.9]
    return float(np.mean(cols)), max(cols), top, bot


def _stubs(k, dark, right, top, bot):
    frac = dark[:, right + 2:right + 6].mean(axis=1)
    idx = [i for i in np.where(frac > 0.7)[0] if top - 3 <= i <= bot + 3]
    return [(a + b) / 2 for a, b in k.clusters(idx, 1) if b - a < 12]


def read(k, image, C, at):
    img = k.rgb(image)
    g = img.mean(axis=2)
    sat = img.max(axis=2) - img.min(axis=2)
    dark = g < 150
    band = (g > 200) & (g < 232) & (sat < 12)
    # x from the bottom panel
    bc0, br0, bc1, br1 = C["xpanel"]
    bx, bright, btop, bbot = _axis(k, dark, bc0, br0, bc1, br1)
    xrow = max(range(br0, br1), key=lambda r: dark[r, int(bright) + 3:bc1].sum())
    frac = dark[xrow - 5:xrow - 2, :].mean(axis=0)
    xst = [(a + b) / 2 for a, b in k.clusters([i for i in np.where(frac > 0.7)[0] if bright + 10 < i < bc1], 1) if b - a < 12]
    if not xst:
        raise RuntimeError("no x tick above the bottom panel's axis")
    # the panel
    c0, r0, c1, r1 = C["panel"]
    ycol, right, top, bot = _axis(k, dark, c0, r0, c1, r1)
    st = sorted(_stubs(k, dark, right, top, bot))
    marks = []
    for which, val in C["yticks"]:
        marks.append((float(top) if which == "top" else st[which], val))
    Y = k.Lin(marks)
    shift = ycol - bx
    X = k.Lin([(bx + shift, 0.0), (xst[0] + shift, 50.0)])
    X.misfit_px = abs(shift) + 1.5
    line = dark.copy()
    line[:, :right + 6] = False  # the axis line and its stubs
    out = []
    note = f"y marks {[(round(p, 1), v) for p, v in marks]}; y misfit {Y.misfit_px:.2g} px; x: 0 at col {bx:.1f}, 50 at col {xst[0]:.1f}"
    both = band | line
    e = 1 + 2 * Y.misfit_px
    for x in at:
        c = int(round(X.pix(float(x))))
        rs = [(a + top + 1, b + top + 1) for a, b in k.runs(both[top + 1:bot - 1, c], 3)]
        rs = [ab for ab in rs if line[ab[0]:ab[1] + 1, c].any()]
        if not rs:
            out.append({"x": float(x), "y": None, "note": f"no band with a line at this column; {note}"})
            continue
        ab = max(rs, key=lambda q: band[q[0]:q[1] + 1, c].sum())  # the band, not a stray dark drawing
        mid = (ab[0] + ab[1]) / 2
        r = k.curve_value(X, Y, line, float(x), lambda q: min(q, key=lambda u: abs((u[0] + u[1]) / 2 - mid)),
                          r0=ab[0] - 2, r1=ab[1] + 3, note=note)
        if r.get("y") is None:
            out.append(r)
            continue
        r.update({"bar_hi": float(Y.val(ab[0])), "bar_lo": float(Y.val(ab[1])),
                  "bar_hi_outer": float(Y.val(ab[0] - e)), "bar_lo_outer": float(Y.val(ab[1] + e))})
        if ab[0] <= top + 3 or ab[1] >= bot - 3:
            for key in ("bar_lo", "bar_hi", "bar_lo_outer", "bar_hi_outer"):
                r.pop(key, None)
            r["note"] += "; band cut by the axis limit: no bar"
        out.append(r)
    return out
