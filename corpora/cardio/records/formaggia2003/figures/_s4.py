"""Shared reading code for the Section 4 plots (Figs. 14-18, PDF pp. 20-24). The axes are
calibrated exactly as in _fig.py (plot box, inward tick marks matched to the printed labels and
the box corners; the largest misfit widens every interval). What is new here is how a curve is
told from another one in the same panel:

- 'line': the panel holds one line; read on all the ink in the box (less the tick marks of all
  four borders and the legend), track by track as in _fig.read_tracks.
Dots and line are told apart by shape. The ink is eroded by `erode` px, which breaks the thin
necks between touching dots; an eroded piece of extent dotmin..dot px (both sides) is a dot,
provided the unbroken ink it belongs to is at least 85% covered by dots (otherwise it is a bit of
the continuous line left by the erosion). The rest of the ink is the continuous line, together
with stretches where the dots touch the line or each other in long chains.

- 'solid': the continuous line: read on the ink that is not dots, as in _fig.read_tracks, with
  rules (x0, x1, rank, n) naming the track where there are several.
- 'dots': the dotted line. Each dot's centre is a point of the curve; the value at x is the
  linear interpolation between the dots on either side. Its interval is the dot's half height,
  one raster pixel of blur, the calibration misfit, and a quarter of the height step between the
  two dots (curvature between them). Where no separate dot lies within GAPF times their usual
  spacing (or on one side at all), the dots run as unbroken ink (on the continuous line or in a
  chain); the value is read there on the unbroken ink: on the track a reader's rule names
  (dot_rules), else on the track nearest the row the neighbouring dots point to; the note says so.
- 'extremes': no x positions; the highest and the lowest ink of the curve (the largest positive
  and negative excursion), as two points.
"""

import importlib.util
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location("_fig", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

_DOT = 13      # a dot, once eroded, is at most this many px in extent ...
_DOTMIN = 5    # ... and at least this many (thinner bits are what erosion leaves of the continuous line)
_ERODE = 2     # px of erosion; all three can be set per reading (cfg keys dot, dotmin, erode)
GAPF = 2.6
EDGE = 26
SPECK = 40
STEP = 6


def _clear_edges(m, bx, edge=EDGE):
    """Remove the tick marks on the top and right borders (the calibration finds only those on
    the bottom and left ones): `edge` px inside those borders."""
    m = m.copy()
    m[: bx["t1"] + edge, :] = False
    m[:, bx["r0"] - edge:] = False
    return m


def _pieces(m, cfg=None):
    # erode first: neighbouring dots touch through thin necks, which erosion breaks, while the
    # continuous line (about 9 px thick) survives as long pieces
    cfg = cfg or {}
    ERODE, DOT, DOTMIN = cfg.get("erode", _ERODE), cfg.get("dot", _DOT), cfg.get("dotmin", _DOTMIN)
    er = ndimage.binary_erosion(m, structure=np.ones((3, 3), bool), iterations=ERODE) if ERODE else m
    lab, n = ndimage.label(er, structure=np.ones((3, 3), int))
    sl = ndimage.find_objects(lab)
    isdot = np.zeros(n + 1, bool)
    for i, s in enumerate(sl, start=1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if max(h, w) <= DOT and min(h, w) >= DOTMIN:
            isdot[i] = True
    # a dot-shaped piece counts only if the unbroken ink it belongs to is made of dots (a chain of
    # touching dots); a piece of the continuous line left by the erosion belongs to ink that is
    # mostly not dot-shaped
    near = ndimage.binary_dilation(isdot[lab], structure=np.ones((3, 3), bool), iterations=ERODE + 2)
    olab, on = ndimage.label(m, structure=np.ones((3, 3), int))
    tot = ndimage.sum(np.ones_like(m), olab, index=np.arange(on + 1))
    cov = ndimage.sum(near & m, olab, index=np.arange(on + 1))
    okc = cov >= 0.85 * np.maximum(tot, 1)
    dots = []
    keep = np.zeros(n + 1, bool)
    for i, s in enumerate(sl, start=1):
        if not isdot[i]:
            continue
        rr, cc = np.nonzero(lab[s] == i)
        r0, c0 = s[0].start + rr[0], s[1].start + cc[0]
        if okc[olab[r0, c0]]:
            keep[i] = True
            dots.append((s[1].start + cc.mean(), s[0].start + rr.mean(), s[0].stop - s[0].start + 2 * ERODE))
    xs = sorted(d[0] for d in dots)
    sp = float(np.median(np.diff(xs))) if len(xs) > 2 else 1e9
    # chains of touching dots (unbroken ink made only of dots, wider than one dot): their centre
    # row every STEP columns is a point of the dotted line too
    for j, s in enumerate(ndimage.find_objects(olab), start=1):
        if s is None or not okc[j] or s[1].stop - s[1].start <= DOT + 2 * ERODE + 4:
            continue
        sub = olab[s] == j
        for cc in range(0, sub.shape[1], STEP):
            rr = np.flatnonzero(sub[:, cc])
            if len(rr) and rr.max() - rr.min() < 2 * (DOT + 2 * ERODE):
                dots.append((s[1].start + cc, s[0].start + (rr.min() + rr.max()) / 2.0, rr.max() - rr.min() + 1))
    dmask = ndimage.binary_dilation(keep[lab], structure=np.ones((3, 3), bool), iterations=ERODE + 2)
    solid = m & ~(dmask | okc[olab] & (olab > 0))
    return solid, sorted(dots), sp


def _dot_row(dots, col):
    """The row of the dotted line at column col, interpolated between the separate dots on either side."""
    if not dots:
        return None
    left = [d for d in dots if d[0] <= col]
    right = [d for d in dots if d[0] > col]
    if not left or not right:
        return (right[0] if right else left[-1])[1]
    L, R = left[-1], right[0]
    return L[1] + (col - L[0]) / (R[0] - L[0]) * (R[1] - L[1])


def _value_on(m, c, row_hint, cal, rank=0, near=60):
    """The value on mask m at column c: the track nearest row_hint (or the track `rank`)."""
    ya, yb, ymis, _ = cal["y"]
    xa, xb, xmis, _ = cal["x"]
    tr = _f.tracks(m, c)
    if not tr:
        return None, "no ink of this line here"
    if row_hint is not None:
        a, b = min(tr, key=lambda t: abs((t[0] + t[1]) / 2.0 - row_hint))
        if abs((a + b) / 2.0 - row_hint) > near and not (a - 10 <= row_hint <= b + 10):
            return None, "no ink of this line near the expected row"
    else:
        if not (-len(tr) <= rank < len(tr)):
            return None, f"no track {rank} among {len(tr)}"
        a, b = tr[rank]
    nar = m[a:b, max(c - 2, 0): c + 3].any(axis=1)
    rows = np.flatnonzero(nar)
    a2, b2 = (a + rows.min(), a + rows.max() + 1) if len(rows) else (a, b)
    if b2 - a2 > _f.STEEP:
        return None, f"track {b2 - a2} px tall: a near-vertical stretch"
    row = (a2 + b2 - 1) / 2.0
    sl = 0.0
    nb = []
    for k in (c - 2 * _f.W, c + 2 * _f.W):
        tk = [t for t in _f.tracks(m, k) if t[0] - 30 <= row <= t[1] + 30]
        if len(tk) == 1:
            nb.append((tk[0][0] + tk[0][1]) / 2.0)
    if len(nb) == 2:
        sl = abs(nb[1] - nb[0]) / (4.0 * _f.W)
    e = (b - a) / 2.0 + _f.BLUR + ymis + sl * xmis
    return (row, e, f"{len(tr)} track(s), {b - a} px tall in the window"), None


def _row(x, y, row, e, col, cal, note):
    ya, yb, _, _ = cal["y"]
    lo, hi = ya + yb * (row + e), ya + yb * (row - e)
    return {"x": x, "y": float(ya + yb * row), "lo": float(min(lo, hi)), "hi": float(max(lo, hi)),
            "px": [float(col), float(row)], "px_lo": float(row - e), "px_hi": float(row + e), "note": note}


def masks(image, cfg):
    cal = _f.calibrate(image, cfg)
    m = _clear_edges(_f.interior(cal, cfg.get("legend")), cal["bx"], cfg.get("edge", EDGE))
    for c0, r0, c1, r1 in cfg.get("blank", []):   # other regions to ignore (e.g. labels inside the box)
        m[r0:r1, c0:c1] = False
    # specks of dust in the scan: unbroken ink of fewer than `speck` px
    lab, n = ndimage.label(m, structure=np.ones((3, 3), int))
    size = ndimage.sum(m, lab, index=np.arange(n + 1))
    m &= size[lab] >= cfg.get("speck", SPECK)
    return cal, m


def read(image, at, cfg):
    style = cfg.get("style", "line")
    cal, m = masks(image, cfg)
    xa, xb, xmis, _ = cal["x"]
    ya, yb, ymis, _ = cal["y"]
    solid, dots, sp = (m, [], 1e9) if style in ("line", "extremes") else _pieces(m, cfg)
    out = []
    if style == "extremes":
        rows = np.nonzero(m)
        for k, name in ((int(np.argmin(rows[0])), "highest ink"), (int(np.argmax(rows[0])), "lowest ink")):
            r, c = float(rows[0][k]), float(rows[1][k])
            e = _f.BLUR + ymis
            out.append(_row(float(xa + xb * c), None, r, e, c, cal, f"{name} of the curve (its extreme)"))
        return out
    if style in ("solid", "line"):
        what = "continuous line" if style == "solid" else "line"
        for x in at:
            x = float(x)
            col = (x - xa) / xb
            ntr = len(_f.tracks(solid, int(round(col))))
            rule = next((r for r in cfg.get("rules", [(-1e9, 1e9, 0, None)]) if r[0] - 1e-9 <= x <= r[1] + 1e-9
                         and (r[3] is None or r[3] == ntr)), None)
            if rule is None:
                out.append({"x": x, "y": None, "note": f"{ntr} tracks of the {what}'s ink here; no rule takes one"})
                continue
            rank = rule[2]
            pre = f"{what}: track {rank}; "
            if rank == "auto":
                # the track farthest from where the dotted line runs (its separate dots on either side)
                tr = _f.tracks(solid, int(round(col)))
                drow = _dot_row(dots, col)
                if len(tr) >= 2 and drow is not None:
                    rank = int(np.argmax([abs((a + b) / 2.0 - drow) for a, b in tr]))
                    pre = f"{what}: of {len(tr)} tracks, the one farthest from the dotted line (row {drow:.0f}); "
                else:
                    rank = 0
                    pre = f"{what}: track 0; "
            got, why = _value_on(solid, int(round(col)), None, cal, rank)
            if got is None and style == "solid" and ntr == 0 and len(_f.tracks(m, int(round(col)))) == 1:
                # the continuous line runs under the dots here (the two lines coincide): the one track of all the ink
                got, why = _value_on(m, int(round(col)), None, cal, 0)
                pre = "the continuous line is hidden under the dots here (one track of ink: the lines coincide); "
            if got is None:
                out.append({"x": x, "y": None, "note": why})
                continue
            row, e, note = got
            out.append(_row(x, None, row, e, col, cal, pre + note))
        return out
    # dotted line
    D = np.array([(d[0], d[1], d[2]) for d in dots]) if dots else np.zeros((0, 3))
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        left = D[D[:, 0] <= col]
        right = D[D[:, 0] > col]
        if not len(left) and not len(right):
            out.append({"x": x, "y": None, "note": "no separate dots in the panel"})
            continue
        if not len(left) or not len(right):
            # beyond the last separate dot: the dotted line runs on as unbroken ink (dots touching
            # each other or the continuous line), read nearest the row of the last dot
            N = right[0] if len(right) else left[-1]
            hint, gap = N[1], abs(N[0] - col)
        else:
            L, R = left[-1], right[0]
            w = (col - L[0]) / (R[0] - L[0])
            hint, gap = L[1] + w * (R[1] - L[1]), R[0] - L[0]
        if not len(left) or not len(right) or gap > cfg.get("gap", GAPF * max(sp, 1.0)):
            # the reader's rules (x0, x1, rank, n) may name the track where the unbroken dots run
            # beside the continuous line; otherwise the track nearest the dots' row
            ntr = len(_f.tracks(solid, int(round(col))))
            rule = next((r for r in cfg.get("dot_rules", []) if r[0] - 1e-9 <= x <= r[1] + 1e-9
                         and (r[3] is None or r[3] == ntr)), None)
            if rule is not None:
                got, why = _value_on(solid, int(round(col)), None, cal, rule[2])
                how = f"read on track {rule[2]} of the unbroken ink (reader's rule)"
            else:
                got, why = _value_on(solid, int(round(col)), hint, cal, near=cfg.get("near", 60))
                how = f"read on the ink nearest row {hint:.0f}"
                if got is None and ntr == 1:
                    got, why = _value_on(solid, int(round(col)), None, cal, 0)
                    how = "read on the one track of ink there (the dots run on the continuous line)"
            if got is None:
                out.append({"x": x, "y": None, "note": f"no separate dot within {gap:.0f} px and {why}"})
                continue
            r2, e, note = got
            out.append(_row(x, None, r2, e, col, cal,
                            f"no separate dot within {gap:.0f} px: the dots run as unbroken ink here (touching each "
                            f"other or the continuous line); {how}; " + note))
            continue
        row = hint
        e = max(L[2], R[2]) / 2.0 + _f.BLUR + ymis + 0.25 * abs(R[1] - L[1]) + abs(R[1] - L[1]) / max(R[0] - L[0], 1) * xmis
        out.append(_row(x, None, row, e, col, cal, f"between dots {R[0] - L[0]:.0f} px apart"))
    return out
