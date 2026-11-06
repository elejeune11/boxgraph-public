"""Shared reading code for the plotted figures of westerhof1969 (Figs. 3, 5, 6, 7, 10).

Everything is found in the rendered crop:
- figures printed sideways on the page (Figs. 5, 6, 7, 10) are first turned upright (np.rot90);
  every position returned is mapped back to the crop's own pixels for the overlay;
- the scan is slightly tilted: the tilt is measured on the longest straight line (an axis) and
  positions are taken in a frame (u, v) turned with it: u along the abscissa, v down the ordinate;
- the labelled abscissa is the lowest long straight line; its ticks are the short stubs on its
  chosen side, matched to the printed labels (the most evenly spaced set);
- the ordinate is the strongest straight line across the abscissa near the left of the plot; its
  ticks are the short stubs on its left, and a panel takes the evenly spaced run of stubs that
  matches its labels (top or bottom group);
- each axis is a straight-line fit of tick position to label; the worst misfit enters every
  interval;
- a bold curve is the ink that survives a morphological opening with a disk a little narrower
  than the bold stroke (thin lines vanish), followed column by column (boxgraph.digitize.trace);
- points (dots, circles, crosses) and error bars are found as connected ink of their own shape.
"""

import itertools
import math

import numpy as np
from scipy import ndimage

from boxgraph import digitize as D


# ------------------------------------------------------------------ basics

def ink_of(image):
    g = image[..., :3].astype(float).mean(axis=2)
    paper, darkest = np.percentile(g, 99), np.percentile(g, 0.5)
    return g < (paper + darkest) / 2


def runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r + 0.5


class Upright:
    """np.rot90(image, k) with the map back to the crop's own (column, row)."""

    def __init__(self, image, k):
        self.k = k % 4
        self.H, self.W = image.shape[:2]
        self.image = np.rot90(image, self.k)

    def back(self, col, row):
        """Upright (col, row) -> crop (col, row)."""
        H, W = self.H, self.W
        if self.k == 0:
            return col, row
        if self.k == 1:  # out[i, j] = a[j, W-1-i]
            return W - 1 - row, col
        if self.k == 3:  # out[i, j] = a[H-1-j, i]
            return row, H - 1 - col
        return W - 1 - col, H - 1 - row


def _line_angle(rr, cc, max_deg=2.0, step=0.01):
    best = None
    for deg in np.arange(-max_deg, max_deg + step / 2, step):
        t = math.tan(math.radians(deg))
        proj = np.round(rr - cc * t).astype(int)
        lo = proj.min()
        h = np.bincount(proj - lo)
        k = int(np.argmax(h))
        if best is None or h[k] > best[0]:
            best = (h[k], math.radians(deg), k + lo)
    return best[1], best[2]


class Frame:
    def __init__(self, theta):
        self.c, self.s = math.cos(theta), math.sin(theta)

    def uv(self, col, row):
        return col * self.c + row * self.s, -col * self.s + row * self.c

    def cr(self, u, v):
        return u * self.c - v * self.s, u * self.s + v * self.c


def _fit(pairs):
    p = np.array([a for a, _ in pairs], float)
    v = np.array([b for _, b in pairs], float)
    b, a = np.polyfit(p, v, 1)
    misfit = float(np.max(np.abs((v - a) / b - p)))
    return a, b, max(misfit, 0.5)


def match_ticks(cands, labels, increasing=True, tol=6.0, min_match=3):
    """Match tick candidates (pixel positions) to printed labels by the linear map that matches
    most labels (ties: smallest residual). increasing: pixel grows with the label value.
    Returns [(pixel, label)], a label without a stub is left out."""
    cands = sorted(cands)
    labels = sorted(labels)
    best = None
    for (i, a), (j, b) in itertools.combinations(enumerate(cands), 2):
        for la, lb in itertools.combinations(labels, 2):
            if not increasing:
                la, lb = lb, la
            s = (b - a) / (lb - la)
            step = min(abs(s * (y - x)) for x, y in zip(labels, labels[1:]))
            if step < 4 * tol:
                continue
            pairs, res, used = [], 0.0, set()
            for lab in labels:
                p = a + s * (lab - la)
                d = [abs(c - p) for c in cands]
                kk = int(np.argmin(d))
                if d[kk] <= tol and kk not in used:
                    used.add(kk)
                    pairs.append((cands[kk], lab))
                    res += d[kk]
            score = (len(pairs), -res)
            if best is None or score > best[0]:
                best = (score, pairs)
    if best is None or len(best[1]) < min_match:
        raise RuntimeError(f"could not match ticks {cands} to labels {labels}")
    return best[1]


def _stubs(ink, fr, H, W, base, along, across_offsets, kind):
    """Ink fraction of a short probe beside an axis, along the axis.

    kind 'x': base is v of the axis, along are u values, probe at v = base + offsets.
    kind 'y': base is u of the axis, along are v values, probe at u = base + offsets."""
    f = np.zeros(len(along))
    for i, t in enumerate(along):
        if kind == "x":
            cs, rs = fr.cr(np.full(len(across_offsets), float(t)), base + across_offsets)
        else:
            cs, rs = fr.cr(base + across_offsets, np.full(len(across_offsets), float(t)))
        cs, rs = np.round(cs).astype(int), np.round(rs).astype(int)
        ok = (cs >= 0) & (cs < W) & (rs >= 0) & (rs < H)
        f[i] = ink[rs[ok], cs[ok]].sum() / len(across_offsets)
    return f


def _cands(f, along, half, frac=0.8, merge=3):
    on = f >= frac
    rs = runs(on)
    # merge runs split by a pixel or two
    merged = []
    for a, b in rs:
        if merged and a - merged[-1][1] <= merge:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return [float(along[a] + along[b - 1]) / 2.0 for a, b in merged if b - a <= 4 * half + 4]


# ------------------------------------------------------------------ calibration

class Cal:
    pass


def calibrate(image, k, x_labels, panels, xtick_side="up", x_axis="lowest", tick_len=None,
              x_window=None, x_zero_at_ordinate=False):
    """Calibrate the abscissa and the ordinate of each panel.

    panels: {name: (labels, (v0, v1))}: the printed ordinate labels and the band of the upright
    crop (pixel rows, a search window only) where that panel's ordinate ticks lie.
    xtick_side: 'up' (ticks point into the plot) or 'down'. tick_len: probe length (px)."""
    up = Upright(image, k)
    ink = ink_of(up.image)
    H, W = ink.shape
    rr, cc = np.nonzero(ink)
    if len(rr) > 400_000:
        pick = np.random.default_rng(0).choice(len(rr), 400_000, replace=False)
        rr, cc = rr[pick], cc[pick]
    theta, _ = _line_angle(rr, cc)
    fr = Frame(theta)
    r, c = np.mgrid[0:H, 0:W].astype(np.float32)
    U = c * fr.c + r * fr.s
    V = -c * fr.s + r * fr.c
    # long horizontal lines: peaks of the v-histogram of ink
    vv = np.round(V[ink]).astype(int)
    v0 = vv.min()
    hv = np.bincount(vv - v0)
    peak = hv.max()
    lines = [i + v0 for i in range(len(hv)) if hv[i] >= 0.5 * peak
             and hv[i] == hv[max(i - 8, 0): i + 9].max()]
    v_axis = float(max(lines) if x_axis == "lowest" else x_axis(lines))
    band = ink & (np.abs(V - v_axis) <= 15)
    cols_on = band.any(axis=0)
    xrun = max(runs(cols_on), key=lambda t: t[1] - t[0])
    th = []
    for col in range(xrun[0], xrun[1], 7):
        rs = runs(band[:, col])
        if rs:
            th.append(max(b - a for a, b in rs))
    half = max(float(np.median(th)) / 2.0, 2.0)
    L = tick_len or int(3 * half)
    offs = np.arange(int(half + 3), int(half + 3 + L), dtype=float)
    # the ordinate: strongest near-vertical line in the left part, above the abscissa
    reg = ink & (V < v_axis - 3 * half) & (U < np.percentile(U[ink], 30))
    uu = np.round(U[reg]).astype(int)
    hu = np.bincount(uu - uu.min())
    u_y = float(np.argmax(hu) + uu.min())
    # abscissa ticks
    u0, _ = fr.uv(xrun[0], v_axis)
    u1, _ = fr.uv(xrun[1], v_axis)
    along = np.arange(u0, u1, 1.0)
    sgn = -1.0 if xtick_side == "up" else 1.0
    fx = _stubs(ink, fr, H, W, v_axis, along, sgn * offs, "x")
    xc = [x for x in _cands(fx, along, half) if abs(x - u_y) > 4 * half]
    if x_zero_at_ordinate:
        # the printed 0 of the abscissa stands at the corner: the ordinate line is its tick
        xc.append(u_y)
    if x_window is not None:
        xc = [x for x in xc if x_window[0] <= x <= x_window[1]]
    xpairs = match_ticks(xc, x_labels, increasing=True, tol=max(6.0, half))
    xa, xb, xmis = _fit([(p, lab) for p, lab in xpairs])
    cal = Cal()
    cal.up, cal.ink, cal.frame, cal.theta, cal.half = up, ink, fr, theta, half
    cal.U, cal.V, cal.v_axis, cal.u_y = U, V, v_axis, u_y
    cal.x = (xa, xb, xmis)
    cal.xpairs = xpairs
    cal.xcands = xc
    cal.panels = {}
    for name, (labels, (pv0, pv1)) in panels.items():
        along = np.arange(pv0, pv1, 1.0)
        # ticks are stubs on the left, on the right, or across the ordinate: try each, keep the
        # set that matches most labels, then the smallest misfit
        sides = {s: _cands(_stubs(ink, fr, H, W, u_y, along, s * offs, "y"), along, half)
                 for s in (-1.0, 1.0)}
        merged = []
        for x in sorted(sides[-1.0] + sides[1.0]):
            if merged and x - merged[-1][0] <= 4 * half:
                merged[-1].append(x)
            else:
                merged.append([x])
        options = {"left": sides[-1.0], "right": sides[1.0],
                   "both": [float(np.mean(g)) for g in merged]}
        best = None
        for sname, cands in options.items():
            try:
                pairs = match_ticks(cands, labels, increasing=False, tol=max(6.0, half))
            except RuntimeError:
                continue
            ya, yb, ymis = _fit([(p, lab) for p, lab in pairs])
            score = (len(pairs), -ymis)
            if best is None or score > best[0]:
                best = (score, dict(y=(ya, yb, ymis), pairs=pairs, cands=cands, side=sname))
        if best is None:
            raise RuntimeError(f"panel {name}: no ordinate ticks matched {labels}")
        cal.panels[name] = best[1]
    return cal


def to_x(cal, u):
    a, b, _ = cal.x
    return a + b * u


def u_of_x(cal, x):
    a, b, _ = cal.x
    return (x - a) / b


def to_y(p, v):
    a, b, _ = p["y"]
    return a + b * v


def v_of_y(p, y):
    a, b, _ = p["y"]
    return (y - a) / b


def note_cal(cal, p):
    return (f"calibration misfit {cal.x[2]:.1f} px in x, {p['y'][2]:.1f} px in y; "
            f"tilt {math.degrees(cal.theta):.2f} deg")


# ------------------------------------------------------------------ bold curve

def dp_path(m, c_lo, c_hi, bold_half, lam=1.0, mu=0.05):
    """The bold line as the best path through the ink runs of columns c_lo..c_hi.

    Each run scores the local stroke half-width at its thickest point (distance transform of the
    ink, capped at bold_half), so a thin line scores about half of the bold one; a step between
    runs of neighbouring columns costs lam per pixel of empty gap between them and mu per pixel
    the centre moves. Columns without ink are skipped. A run much longer than its neighbours on
    the path (a crossing or a symbol on the line) is flagged ambiguous."""
    dt = ndimage.distance_transform_edt(m)
    H, W = m.shape
    c_lo, c_hi = max(c_lo, 0), min(c_hi, W - 1)
    cols, states = [], []
    for c in range(c_lo, c_hi + 1):
        rs = runs(m[:, c])
        if not rs:
            continue
        st = [(a, b, (a + b - 1) / 2.0, min(float(dt[a:b, c].max()), bold_half)) for a, b in rs]
        cols.append(c)
        states.append(st)
    if not cols:
        return {}
    score = [np.array([s[3] for s in states[0]])]
    back = [None]
    for k in range(1, len(cols)):
        prev, cur = states[k - 1], states[k]
        pa = np.array([s[0] for s in prev], float)
        pb = np.array([s[1] for s in prev], float)
        pcen = np.array([s[2] for s in prev], float)
        sc = np.empty(len(cur))
        bk = np.empty(len(cur), int)
        for j, (a, b, cen, w) in enumerate(cur):
            gap = np.maximum(0.0, np.maximum(pa - b, a - pb))
            tot = score[-1] - lam * gap - mu * np.abs(pcen - cen)
            i = int(np.argmax(tot))
            sc[j] = tot[i] + w
            bk[j] = i
        score.append(sc)
        back.append(bk)
    j = int(np.argmax(score[-1]))
    chosen = [None] * len(cols)
    for k in range(len(cols) - 1, -1, -1):
        chosen[k] = j
        if k:
            j = int(back[k][j])
    lens = np.array([states[k][chosen[k]][1] - states[k][chosen[k]][0] for k in range(len(cols))], float)
    path = {}
    for k, c in enumerate(cols):
        a, b, cen, w = states[k][chosen[k]]
        ref = float(np.median(lens[max(k - 40, 0): k + 41]))
        path[c] = (cen, (b - a) / 2.0, bool(lens[k] > 1.8 * ref + 4), w)
    return path


def _readout(cal, p, fr, path, at, note):
    pc = np.array(sorted(path))
    centre = np.array([path[c][0] for c in pc])
    halfh = np.array([path[c][1] for c in pc])
    amb = np.array([path[c][2] for c in pc])
    uu = (pc + 0.5) * fr.c + centre * fr.s
    vv = -(pc + 0.5) * fr.s + centre * fr.c
    xmis, ymis = cal.x[2], p["y"][2]
    out = []
    for x in at:
        ut = u_of_x(cal, x)
        if ut < uu.min() or ut > uu.max():
            out.append({"x": x, "y": None, "note": "the bold line does not reach this abscissa"})
            continue
        i = int(np.argmin(np.abs(uu - ut)))
        j0, j1 = max(i - 4, 0), min(i + 5, len(uu))
        slope = float(np.polyfit(uu[j0:j1], vv[j0:j1], 1)[0]) if j1 - j0 >= 3 else 0.0
        v = vv[i] + slope * (ut - uu[i])
        hw = halfh[i] + 0.5 + abs(slope) * (xmis + abs(ut - uu[i])) + ymis
        y = to_y(p, v)
        y1, y2 = to_y(p, v - hw), to_y(p, v + hw)
        c0, r0 = cal.up.back(*fr.cr(ut, v))
        c1, r1 = cal.up.back(*fr.cr(ut, v - hw))
        c2, r2 = cal.up.back(*fr.cr(ut, v + hw))
        nt = note
        if amb[max(i - 2, 0): i + 3].any():
            nt = (nt + "; " if nt else "") + "another line or a symbol merges with the bold one here; interval covers both"
        rec = {"x": x, "y": float(y), "lo": float(min(y1, y2)), "hi": float(max(y1, y2)),
               "px": [float(c0), float(r0)],
               "note": (nt + "; " if nt else "") + note_cal(cal, p)}
        if cal.up.k == 0:
            rec["px_lo"], rec["px_hi"] = float(min(r1, r2)), float(max(r1, r2))
        out.append(rec)
    return out


def find_bars(cal, panel, stem_len=60, v_top_label=None, v_bot_label=None):
    """Error bars: vertical stems at least stem_len px tall (a morphological opening with a
    vertical line keeps them and drops sloping lines), each with its column, its two ends and the
    marker on it (the thickest point of the ink along the stem, by distance transform, away from
    the caps). Returns a list of dicts in upright pixels, sorted by u."""
    p = cal.panels[panel]
    m = cal.ink & (cal.U > cal.u_y + 4 * cal.half) & (cal.V < cal.v_axis - 3 * cal.half)
    if v_top_label is not None:
        vt, vb = sorted([v_of_y(p, v_top_label), v_of_y(p, v_bot_label)])
        m &= (cal.V > vt) & (cal.V < vb)
    stems = ndimage.binary_opening(m, structure=np.ones((stem_len, 1), bool))
    lab, n = ndimage.label(stems, structure=np.ones((3, 3)))
    dt = ndimage.distance_transform_edt(m)
    fr = cal.frame
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        rr = rr + sl[0].start
        cc = cc + sl[1].start
        if cc.max() - cc.min() > 4 * cal.half + 6:
            continue  # not a thin vertical stem
        col = float(np.median(cc))
        r0, r1 = int(rr.min()), int(rr.max())
        # the caps: the widest horizontal ink runs near each end of the stem
        def cap_width(r):
            rs = runs(m[r, :])
            for a, b in rs:
                if a <= col <= b:
                    return b - a
            return 0
        top_w = max(cap_width(r) for r in range(r0, min(r0 + 8, r1)))
        bot_w = max(cap_width(r) for r in range(max(r1 - 8, r0), r1 + 1))
        # marker: largest distance-transform value within 3 px of the stem column, away from caps
        c0, c1 = int(col) - 3, int(col) + 4
        best, best_r = -1.0, None
        for r in range(r0 + 10, r1 - 9):
            d = float(dt[r, c0:c1].max())
            if d > best:
                best, best_r = d, r
        u_c, v_top = fr.uv(col, r0)
        _, v_bot = fr.uv(col, r1)
        mk = None
        if best_r is not None:
            mk = (best_r, best)
        out.append(dict(u=u_c, col=col, r0=r0, r1=r1, v_top=v_top, v_bot=v_bot,
                        cap_top=top_w, cap_bot=bot_w, marker=mk))
    out.sort(key=lambda b: b["u"])
    return out


def read_bars(cal, panel, at, tol_x, x_from="read", stem_len=60, note="", band=None, dot_r=None):
    """For each abscissa in `at`, the error bar nearest to it (within tol_x): its marker value and
    both ends. x_from 'read' reports the bar's own abscissa; 'at' reports the requested one (a
    printed abscissa such as a harmonic's frequency) and notes the read one."""
    p = cal.panels[panel]
    bars = find_bars(cal, panel, stem_len, *(band or (None, None)))
    fr = cal.frame
    xmis, ymis = cal.x[2], p["y"][2]
    used = set()
    out = []
    for x in at:
        if not bars:
            out.append({"x": x, "y": None, "note": "no error bar found"})
            continue
        d = [abs(to_x(cal, b["u"]) - x) for b in bars]
        order = np.argsort(d)
        k = next((int(j) for j in order if int(j) not in used), None)
        if k is None or d[k] > tol_x:
            out.append({"x": x, "y": None, "note": f"no error bar within {tol_x} of this abscissa"})
            continue
        used.add(k)
        b = bars[k]
        xr = float(to_x(cal, b["u"]))
        if b["marker"] is None:
            out.append({"x": x, "y": None, "note": "no marker found on the bar"})
            continue
        mr, mrad = b["marker"]
        _, v_m = fr.uv(b["col"], mr)
        y = to_y(p, v_m)
        hw = 4.0 + ymis  # the marker centre is found to a few px (lines through it can shift it)
        merged = dot_r is not None and mrad > 1.2 * dot_r
        if merged:
            hw = mrad + ymis
        yl, yh = sorted([to_y(p, v_m - hw), to_y(p, v_m + hw)])
        top, bot = to_y(p, b["v_top"]), to_y(p, b["v_bot"])
        ew = 4.0 + cal.half + ymis  # a bar end: half the cap thickness and the stroke end
        bar_hi, bar_lo = max(top, bot), min(top, bot)
        hi_outer = max(to_y(p, b["v_top"] - ew), to_y(p, b["v_top"] + ew))
        lo_outer = min(to_y(p, b["v_bot"] - ew), to_y(p, b["v_bot"] + ew))
        c0, r0 = cal.up.back(*fr.cr(b["u"], v_m))
        nt = (note + "; " if note else "") + f"bar read at x = {xr:.3f}; marker radius {mrad:.0f} px; "
        if merged:
            nt += "the dot merges with another marker or a thick line here; its interval covers the merged blob; "
        nt += note_cal(cal, p)
        rec = {"x": (float(x) if x_from == "at" else xr), "y": float(y), "lo": float(yl), "hi": float(yh),
               "bar_lo": float(bar_lo), "bar_hi": float(bar_hi),
               "bar_lo_outer": float(lo_outer), "bar_hi_outer": float(hi_outer),
               "px": [float(c0), float(r0)], "note": nt}
        out.append(rec)
    return out


def bold_vertices(cal, panel, at, bold_half, v_lo_label, v_hi_label, near=0.08, far=0.45, note=""):
    """Vertices of a bold polyline at the abscissas `at`: where markers and error bars pile up on a
    vertex, the line itself is read on each side (between `near` and `far` from the vertex, in
    abscissa units, where it is not merged with anything), a straight line is fitted to each side
    and evaluated at the vertex. The value is the mean of the sides; the interval covers both
    sides, the fit residual and the stroke half-width."""
    p = cal.panels[panel]
    fr = cal.frame
    vt, vb = sorted([v_of_y(p, v_lo_label), v_of_y(p, v_hi_label)])
    m = cal.ink & (cal.V > vt) & (cal.V < vb) & (cal.U > cal.u_y + 4 * cal.half)
    xs_ = [float(x) for x in at]
    c_lo = int(fr.cr(u_of_x(cal, min(xs_) - far), 0)[0]) - 5
    c_hi = int(fr.cr(u_of_x(cal, max(xs_) + far), 0)[0]) + 5
    path = dp_path(m, c_lo, c_hi, bold_half)
    pc = np.array(sorted(path))
    centre = np.array([path[c][0] for c in pc])
    halfh = np.array([path[c][1] for c in pc])
    amb = np.array([path[c][2] for c in pc])
    width = np.array([path[c][3] for c in pc])
    uu = (pc + 0.5) * fr.c + centre * fr.s
    vv = -(pc + 0.5) * fr.s + centre * fr.c
    xx = to_x(cal, uu)
    xmis, ymis = cal.x[2], p["y"][2]
    out = []
    for x in at:
        h = float(x)
        ut = u_of_x(cal, h)
        ests, notes = [], []
        for side, (a, b) in (("left", (h - far, h - near)), ("right", (h + near, h + far))):
            # the polyline starts at its first vertex and ends at its last
            if (side == "left" and h == min(xs_)) or (side == "right" and h == max(xs_)):
                continue
            sel = (xx >= a) & (xx <= b) & ~amb & (width >= 0.75 * bold_half)
            if sel.sum() < 15:
                notes.append(f"no clean bold line on the {side}")
                continue
            k, c0 = np.polyfit(uu[sel], vv[sel], 1)
            res = float(np.max(np.abs(vv[sel] - (k * uu[sel] + c0))))
            hh = float(np.median(halfh[sel]))
            v = k * ut + c0
            ests.append((v, res, hh, abs(k)))
        if not ests:
            out.append({"x": x, "y": None, "note": "; ".join(notes) or "no bold line here"})
            continue
        vs = [e[0] for e in ests]
        v = float(np.mean(vs))
        spread = (max(vs) - min(vs)) / 2.0
        hw = spread + max(e[1] for e in ests) + max(e[2] for e in ests) + 0.5 \
            + max(e[3] for e in ests) * xmis + ymis
        y = to_y(p, v)
        y1, y2 = to_y(p, v - hw), to_y(p, v + hw)
        c0_, r0_ = cal.up.back(*fr.cr(ut, v))
        nt = (note + "; " if note else "") + f"vertex from {len(ests)} side(s) of the line"
        if notes:
            nt += " (" + "; ".join(notes) + ")"
        out.append({"x": x, "y": float(y), "lo": float(min(y1, y2)), "hi": float(max(y1, y2)),
                    "px": [float(c0_), float(r0_)], "note": nt + "; " + note_cal(cal, p)})
    return out


def bold_curve(cal, panel, at, bold_r, v_lo_label, v_hi_label, seed_x=None, note="", max_gap=25,
               u_min_x=None, min_extent=150, method="trace"):
    """Read the bold line of a panel at the abscissa values `at`.

    bold_r: radius of the opening disk (px); v_lo_label/v_hi_label: ordinate values (top, bottom)
    bounding the panel's search band; seed_x: an abscissa where the bold line runs alone."""
    p = cal.panels[panel]
    fr = cal.frame
    vt, vb = sorted([v_of_y(p, v_lo_label), v_of_y(p, v_hi_label)])
    m = cal.ink & (cal.V > vt) & (cal.V < vb) & (cal.U > cal.u_y + 4 * cal.half)
    if u_min_x is not None:
        m &= cal.U > u_of_x(cal, u_min_x)
    b = ndimage.binary_opening(m, structure=disk(bold_r))
    # drop short pieces (where dashes, dots or crossings of thin lines happen to be thick)
    lab, n = ndimage.label(b, structure=np.ones((3, 3)))
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start) < min_extent:
            b[sl][lab[sl] == i] = False
    if method == "dp":
        xs_ = [float(x) for x in at]
        c_lo = int(fr.cr(u_of_x(cal, min(xs_)), 0)[0]) - 30
        c_hi = int(fr.cr(u_of_x(cal, max(xs_)), 0)[0]) + 30
        path = dp_path(m, c_lo, c_hi, bold_r)
        return _readout(cal, p, fr, path, at, note)
    # an opening keeps a stroke wider than the disk at its full width
    grown = b
    col = int(round(fr.cr(u_of_x(cal, seed_x), 0)[0]))
    rs = runs(grown[:, col])
    if not rs:
        raise RuntimeError(f"no bold ink at the seed x = {seed_x}")
    # seed on the run that belongs to the widest piece of bold ink
    lab, _ = ndimage.label(grown, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab)

    def width(t):
        k = lab[(t[0] + t[1]) // 2, col]
        sl = objs[k - 1] if k else None
        return (sl[1].stop - sl[1].start) if sl else 0

    a, bb = max(rs, key=lambda t: (width(t), t[1] - t[0]))
    path = D.trace(grown, (col + 0.5, (a + bb) / 2.0), max_gap=max_gap)
    pc = np.array(sorted(path))
    centre = np.array([path[c][0] for c in pc])
    halfh = np.array([path[c][1] for c in pc])
    amb = np.array([path[c][2] for c in pc])
    uu = (pc + 0.5) * fr.c + centre * fr.s
    vv = -(pc + 0.5) * fr.s + centre * fr.c
    xmis, ymis = cal.x[2], p["y"][2]
    out = []
    for x in at:
        ut = u_of_x(cal, x)
        if ut < uu.min() or ut > uu.max():
            out.append({"x": x, "y": None, "note": "the bold line does not reach this abscissa"})
            continue
        i = int(np.argmin(np.abs(uu - ut)))
        if abs(uu[i] - ut) > 3:
            out.append({"x": x, "y": None, "note": "the bold line is broken here"})
            continue
        j0, j1 = max(i - 4, 0), min(i + 5, len(uu))
        slope = float(np.polyfit(uu[j0:j1], vv[j0:j1], 1)[0]) if j1 - j0 >= 3 else 0.0
        v = vv[i] + slope * (ut - uu[i])
        hw = halfh[i] + 0.5 + abs(slope) * (xmis + abs(ut - uu[i])) + ymis
        y = to_y(p, v)
        y1, y2 = to_y(p, v - hw), to_y(p, v + hw)
        c0, r0 = cal.up.back(*fr.cr(ut, v))
        c1, r1 = cal.up.back(*fr.cr(ut, v - hw))
        c2, r2 = cal.up.back(*fr.cr(ut, v + hw))
        nt = note
        if amb[max(i - 2, 0): i + 3].any():
            nt = (nt + "; " if nt else "") + "another line merges with the bold one here; interval covers both"
        rec = {"x": x, "y": float(y), "lo": float(min(y1, y2)), "hi": float(max(y1, y2)),
               "px": [float(c0), float(r0)],
               "note": (nt + "; " if nt else "") + note_cal(cal, p)}
        if cal.up.k == 0:
            rec["px_lo"], rec["px_hi"] = float(min(r1, r2)), float(max(r1, r2))
        out.append(rec)
    return out
