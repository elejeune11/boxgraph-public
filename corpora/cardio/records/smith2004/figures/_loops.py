# Shared reader for the pressure-volume loops (Figs. 8, 9, 11) and the aortic pressure
# curves (Fig. 10) of smith2004. The figures vary one parameter (P_th, R_sys, E_es) and
# draw one loop or curve per value; a reading returns one feature per loop, indexed by that
# parameter (the reading's `at`). Calibration is _curve.calibrate (frame and dotted
# gridlines matched to the printed labels). Features:
#   right_edges / left_edges: the loops' vertical sides (isovolumic phases), i.e. the
#     end-diastolic (right) and end-systolic (left) volumes, read on the x axis;
#   peaks: the tops of the loops' upper arcs (peak ventricular pressure), on the y axis;
#   curve_max / curve_min: the highest / lowest point of each curve that spans the box.
# Which feature belongs to which parameter value is the reading file's `order` (from the
# figure's labels and arrows): features are sorted left to right (edges) or top to bottom
# (peaks, curves) and matched to `order` in turn. A loop drawn in its own colour is read
# from that colour alone (`colors`), so no order is needed.
import importlib.util
import os

import numpy as np
from scipy import ndimage

_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("_curve", os.path.join(_d, "_curve.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)
G = C.G

COLORS = {
    "red": lambda r, g, b: (r > 170) & (g < 130) & (b < 120),
    "blue": lambda r, g, b: (b > 150) & (r < 110) & (g < 130),
    "magenta": lambda r, g, b: (r > 170) & (b > 170) & (g < 140),
}


def _mask(image, ink, cfg):
    if cfg.get("color"):
        im = image[:, :, :3].astype(int)
        mk = COLORS[cfg["color"]](im[:, :, 0], im[:, :, 1], im[:, :, 2])
    else:
        mk = ink
    return G.thick(mk, cfg.get("open", 5), disk=cfg.get("disk", False))


def _features(image, ink, box, X, Y, cfg):
    """Feature list [(value, lo, hi, col, row, row_lo, row_hi)] in the order of `order`."""
    left, right, top, bottom = box
    m = cfg.get("margin", 12)
    c0, c1, r0, r1 = left + m, right - m, top + m, bottom - m
    mk = _mask(image, ink, cfg)
    kind = cfg["feature"]
    feats = []
    if cfg.get("color") and kind == "right_edges":
        # the right side of the loop in this colour, or, when another loop's line hides it
        # (only one side of this colour is found), the colour's rightmost column: the side
        # lies there or under the hiding line, up to two line widths further right
        edges = G.vertical_edges(mk, c0, c1, r0, r1, cfg.get("min_len_frac", 0.08))
        sub = mk[int(r0):int(r1), int(c0):int(c1)]
        cols = np.flatnonzero(sub.any(axis=0))
        if len(edges) >= 2 or not cols.size:
            c, ca, cb, row = edges[-1]
            v, va, vb = X.val(c), X.val(ca - 0.5), X.val(cb + 0.5)
            return [(v, min(va, vb) - X.misfit, max(va, vb) + X.misfit, c, row, None, None)]
        w = G.line_width(mk, c0, c1, r0, r1)
        cmax = float(cols.max()) + c0
        rows = np.flatnonzero(sub[:, int(cmax - c0)])
        lo, hi = X.val(cmax - w), X.val(cmax + 2 * w)
        return [(X.val(cmax - 0.5 * w), lo - X.misfit, hi + X.misfit, cmax, float(rows.mean()) + r0, None, None)]
    if cfg.get("color") and kind == "peaks":
        # the top of the loop in this colour: its highest pixel (a black arrowhead may cover
        # the very top; the arc is flat there)
        sub = mk[int(r0):int(r1), int(c0):int(c1)]
        rows = np.flatnonzero(sub.any(axis=1))
        rt = int(rows.min())
        cs = np.flatnonzero(sub[rt])
        c = float(cs.mean()) + c0
        rs = [x for x in G.column_runs(mk, int(round(c)), r0, r1) if x[0] <= rt + r0 <= x[1]]
        a, b = rs[0] if rs else (rt + r0, rt + r0)
        ya, yb = Y.val(a - 0.5), Y.val(b + 0.5)
        return [(Y.val(0.5 * (a + b)), min(ya, yb) - Y.misfit, max(ya, yb) + Y.misfit, c, 0.5 * (a + b), a, b)]
    if kind in ("right_edges", "left_edges"):
        if cfg.get("edge_band"):
            # look for the sides only between these pressures (below the labels and arrows)
            lo_v, hi_v = cfg["edge_band"]
            r0, r1 = max(r0, Y.px(hi_v)), min(r1, Y.px(lo_v))
        edges = G.vertical_edges(mk, c0, c1, r0, r1, cfg.get("min_len_frac", 0.08))
        n = cfg.get("n", len(edges))
        edges = edges[-n:] if kind == "right_edges" else edges[:n]
        for c, ca, cb, row in edges:
            v, va, vb = X.val(c), X.val(ca - 0.5), X.val(cb + 0.5)
            feats.append((v, min(va, vb) - X.misfit, max(va, vb) + X.misfit, c, row, None, None))
    elif kind == "peaks":
        # each loop's upper arc starts at the top of its left side: traced from there to the
        # loop's right side; the peak is the highest run of single line width on the way
        # (runs merged with another loop's side are skipped)
        rb0, rb1 = r0, r1
        if cfg.get("edge_band"):
            lo_v, hi_v = cfg["edge_band"]
            rb0, rb1 = max(r0, Y.px(hi_v)), min(r1, Y.px(lo_v))
        edges = G.vertical_edges(mk, c0, c1, rb0, rb1, cfg.get("min_len_frac", 0.08))
        n = cfg["n"]
        lefts, rights = edges[:n], edges[-n:]
        w = G.line_width(mk, c0, c1, r0, r1)
        paths = []
        for (cl, _, clb, _), (cr, cra, _, _) in zip(lefts, rights):
            runs = G.column_runs(mk, int(round(cl)), r0, r1)
            r_top = max(runs, key=lambda x: x[1] - x[0])[0]
            cs = int(round(clb + w))
            paths.append((cs, cra, C.trace(mk, cs, ("near", r_top), c0, c1, r0, r1, width=w)))
        for k, (cs, cra, path) in enumerate(paths):
            # where two loops' traces run on the same line (an arc crossing another), the line
            # belongs to the loop at whose right side it ends: the one with the furthest right
            # side that the trace reaches; the other loop leaves those columns out
            def owns(i, j):
                ri, rj = paths[i][1], paths[j][1]
                reach_i = max(paths[i][2]) >= ri - 2 * w
                return reach_i and (ri > rj or max(paths[j][2]) < rj - 2 * w)
            shared = {c for j, (_, _, p) in enumerate(paths) if j != k for c in path
                      if c in p and p[c][0] <= path[c][1] and p[c][1] >= path[c][0] and not owns(k, j)}
            ok = {c: r for c, r in path.items() if cs <= c < cra - w and r[1] - r[0] + 1 <= 1.5 * w + 2
                  and c not in shared}
            c = min(ok, key=lambda k: ok[k][0] + ok[k][1])
            a, b = ok[c]
            ya, yb = Y.val(a - 0.5), Y.val(b + 0.5)
            feats.append((Y.val(0.5 * (a + b)), min(ya, yb) - Y.misfit, max(ya, yb) + Y.misfit, c, 0.5 * (a + b), a, b))
        feats.sort(key=lambda f: -f[0])
    elif kind in ("curve_max", "curve_min"):
        lab, n = ndimage.label(mk[int(r0):int(r1), int(c0):int(c1)])
        spans = []
        for k in range(1, n + 1):
            cols = np.flatnonzero((lab == k).any(axis=0))
            if cols.size and cols.max() - cols.min() > 0.7 * (c1 - c0):
                rows = np.flatnonzero((lab == k).any(axis=1))
                spans.append((rows.mean(), k))
        for _, k in sorted(spans):
            comp = np.zeros_like(mk)
            comp[int(r0):int(r1), int(c0):int(c1)] = lab == k
            # the curve inside its component: traced from a column where it is one run
            cols = [c for c in range(int(c0) + 5, int(c1) - 5, 7) if len(G.column_runs(comp, c, r0, r1)) == 1]
            seed = min(cols, key=lambda c: abs(c - 0.5 * (c0 + c1)))
            w = G.line_width(comp, c0, c1, r0, r1)
            path = C.trace(comp, seed, "only", c0, c1, r0, r1, width=w)
            # the extreme of the curve: the run whose middle is highest (lowest); runs longer
            # than 1.5 line widths (the steep rise, or an arrow tip) are not extremes
            ok = {c: r for c, r in path.items() if r[1] - r[0] + 1 <= 1.5 * w + 2}
            pick = min if kind == "curve_max" else max
            c = pick(ok, key=lambda c: 0.5 * (ok[c][0] + ok[c][1]))
            a, b = ok[c]
            ya, yb = Y.val(a - 0.5), Y.val(b + 0.5)
            feats.append((Y.val(0.5 * (a + b)), min(ya, yb) - Y.misfit, max(ya, yb) + Y.misfit, c, 0.5 * (a + b), a, b))
    return feats


def read_loops(image, at, cfg):
    ink, box, X, Y, note0 = C.calibrate(image, cfg)
    out = []
    if cfg.get("colors"):
        # one loop per colour (`colors`: parameter value -> colour): its feature is the
        # outermost one of that colour (rightmost edge, leftmost edge, highest peak)
        pairs = []
        for x in at:
            col = cfg["colors"][min(cfg["colors"], key=lambda v: abs(float(v) - x))]
            feats = _features(image, ink, box, X, Y, {**cfg, "color": col})
            if not feats:
                out.append({"x": x, "y": None, "note": f"no {col} {cfg['feature']} found; " + note0})
                continue
            f = feats[-1] if cfg["feature"] == "right_edges" else feats[0]
            pairs.append((x, f))
        note = f"{cfg['feature']} of the loop in its colour ({cfg['colors']}); " + note0
    else:
        feats = _features(image, ink, box, X, Y, cfg)
        note = f"{cfg['feature']}: {len(feats)} found; " + note0
        order = [float(v) for v in cfg["order"]]
        if len(feats) != len(order):
            return [{"x": x, "y": None, "note": f"expected {len(order)} features; " + note} for x in at]
        pairs = []
        for x in at:
            k = min(range(len(order)), key=lambda i: abs(order[i] - x))
            pairs.append((x, feats[k]))
    for x, (v, lo, hi, c, r, ra, rb) in pairs:
        d = {"x": x, "y": v, "lo": lo, "hi": hi, "px": [float(c), float(r)], "note": note}
        if ra is not None:
            d["px_lo"], d["px_hi"] = float(ra), float(rb)
        out.append(d)
    return out
