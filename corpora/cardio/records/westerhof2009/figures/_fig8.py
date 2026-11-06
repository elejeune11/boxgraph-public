"""Shared reading code for Fig. 8 (p. 6), adapted from Elzinga and Westerhof [15]: aortic pressure
and flow of single beats of an isolated cat heart pumping into a three-element windkessel, in a
3 x 3 grid of panels: columns C = 57, 19, 4.8 (10^-3 ml/mmHg), rows R = 22, 46, 103 (mmHg s/ml).

Everything is found in the image:
  the grid: the four long vertical and four long horizontal lines;
  the scales: two brackets left of the grid, the upper labelled 100 and 0 mmHg (beside the top row
    of panels), the lower 10 and 0 ml/s (beside the bottom row); their end ticks give the scale.
    The pressure bracket's 0 tick lies on the bottom edge of the top row (within a few px), so the
    pressure zero of every row is taken at the same offset from that row's bottom edge; the flow
    zero likewise at the bottom row's offset. The mmHg and ml/s per px are the same in every panel
    (the panels have equal heights). This carry-over is the reading's assumption; the paper draws
    the scales once.
  the two traces: pressure is drawn with a thicker line (about 10-12 px at 1200 dpi) than flow
    (about 8 px). Each ink pixel is classed by the largest inscribed half-width within 3 px; 9.5 px
    and above is pressure. Where the two lines cross or run together the ink is thick and counts
    as pressure; readings next to such places are widened (see notes).
  the x value of each point is the compliance label of its column (57, 19, 4.8, matched left to
    right to the three columns).
"""

import numpy as np
from scipy import ndimage

C_LABELS = [57.0, 19.0, 4.8]


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _bands(profile, thresh):
    return _runs(np.asarray(profile) > thresh)


def layout(image):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < 128
    H, W = ink.shape
    # grid lines: columns / rows that are ink over most of the grid's extent
    cols = _bands(ink.sum(axis=0), 0.25 * H)
    vlines = [b for b in cols if b[1] - b[0] < 20]
    rows = _bands(ink[:, vlines[0][0]: vlines[-1][1]].sum(axis=1), 0.8 * (vlines[-1][1] - vlines[0][0]))
    hlines = [b for b in rows if b[1] - b[0] < 20][:4]
    # brackets left of the grid: long vertical runs
    left = vlines[0][0]
    brackets = []
    for c in range(left - 120, left - 8):
        for a, b in _runs(ink[:, c]):
            if b - a > 150:
                brackets.append((a, b, c))
    groups = []
    for a, b, c in sorted(brackets):
        for gr in groups:
            if a <= gr["bot"] and b >= gr["top"]:
                gr["top"], gr["bot"] = min(gr["top"], a), max(gr["bot"], b)
                gr["cols"].append(c)
                break
        else:
            groups.append(dict(top=a, bot=b, cols=[c]))
    br = []
    for gr in sorted(groups, key=lambda x: x["top"]):
        a, b, cl = gr["top"], gr["bot"], min(gr["cols"])
        # end ticks: rows near the bracket's ends where ink extends left of it
        # (the flow bracket's ticks stand a few px apart from its vertical line)
        probe = ink[:, cl - 30: cl - 10].all(axis=1)
        ticks = [(s + e) / 2.0 for s, e in _runs(probe) if a - 15 <= s <= b + 15 and e - s < 20]
        br.append(dict(top=a, bot=b, col=cl, ticks=ticks))
    return g, ink, vlines, hlines, br


def calibration(image):
    g, ink, vlines, hlines, br = layout(image)
    p, f = br[0], br[1]                      # upper: pressure (100, 0 mmHg); lower: flow (10, 0 ml/s)
    p100, p0 = min(p["ticks"]), max(p["ticks"])
    f10, f0 = min(f["ticks"]), max(f["ticks"])
    mmhg_per_px = 100.0 / (p0 - p100)
    mls_per_px = 10.0 / (f0 - f10)
    bottoms = [(a + b) / 2.0 for a, b in hlines[1:]]
    p_off = p0 - bottoms[0]                  # pressure zero relative to the top row's bottom edge
    f_off = f0 - bottoms[2]                  # flow zero relative to the bottom row's bottom edge
    return dict(g=g, ink=ink, vlines=vlines, hlines=hlines, mmhg_per_px=mmhg_per_px, mls_per_px=mls_per_px,
                p_off=p_off, f_off=f_off, ticks=dict(p100=p100, p0=p0, f10=f10, f0=f0))


def classify(ink_panel):
    dt = ndimage.distance_transform_edt(ink_panel)
    width = 2 * ndimage.maximum_filter(dt, size=7)
    thick = ink_panel & (width >= 9.5)
    thin = ink_panel & (width < 9.5)
    return thick, thin, width


def _main(mask, min_px):
    lab, n = ndimage.label(mask, structure=np.ones((3, 3), bool))
    keep = np.zeros_like(mask)
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() >= min_px:
            keep |= comp
    return keep


def _extreme(mask, width, which):
    """Column-wise line centres; the highest (min row) or lowest (max row) centre, with the local
    line thickness there."""
    best = None
    for c in range(mask.shape[1]):
        rs = _runs(mask[:, c])
        if not rs:
            continue
        a, b = (rs[0] if which == "top" else rs[-1])
        centre = (a + b) / 2.0
        if best is None or (centre < best[1] if which == "top" else centre > best[1]):
            best = (c, centre, b - a)
    return best


def read_row(image, row, what):
    """what: 'p_max', 'p_min' or 'q_max'. Returns one point per column of the given row (0..2)."""
    cal = calibration(image)
    ink = cal["ink"]
    vl, hl = cal["vlines"], cal["hlines"]
    r0, r1 = hl[row][1] + 6, hl[row + 1][0] - 6
    bottom = (hl[row + 1][0] + hl[row + 1][1]) / 2.0
    out = []
    for k in range(3):
        c0, c1 = vl[k][1] + 6, vl[k + 1][0] - 6
        sub = ink[r0:r1, c0:c1]
        thick, thin, width = classify(sub)
        if what.startswith("p"):
            m = _main(thick, 1500)
            zero = bottom + cal["p_off"]
            scale = cal["mmhg_per_px"]
        else:
            m = _main(thin, 1500)
            zero = bottom + cal["f_off"]
            scale = cal["mls_per_px"]
        c, centre, th = _extreme(m, width, "top" if what.endswith("max") else "bottom")
        row_px = centre + r0
        col_px = c + c0
        y = (zero - row_px) * scale
        # interval: half the line, the tick centring (2 px) and, where the line is thicker than one
        # trace (the two traces run together), the excess thickness
        typical = 11.0 if what.startswith("p") else 8.0
        excess = max(0.0, th - typical - 2)
        e = th / 2.0 + 2.0 + excess
        note = f"line {th} px thick at the extreme"
        if excess:
            note += "; thicker than one trace: the two traces run together here, interval widened"
        if what == "q_max":
            # the flow peak can be hidden where the flow line meets the pressure line
            touch = thick[max(0, int(centre) - 14): int(centre) + 15, max(0, c - 14): c + 15].any()
            if touch:
                e += 10.0
                note += "; the flow peak touches the pressure line, interval widened by 10 px"
        out.append({"x": C_LABELS[k], "y": y, "lo": (zero - (row_px + e)) * scale, "hi": (zero - (row_px - e)) * scale,
                    "px": [col_px, row_px], "px_lo": row_px - e, "px_hi": row_px + e,
                    "note": note + f"; zero taken {cal['p_off' if what.startswith('p') else 'f_off']:+.1f} px from this row's bottom edge"})
    return out
