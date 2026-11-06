# Shared curve reader for the time plots of smith2004 (Figs. 5, 6, 7). A reading file gives
# its axis anchors (which frame edge or gridline carries which printed label, and the
# label step) and a rule for which run of ink in a column is its curve. Values are the
# centre of that run; the 95% interval is the run's extent (line thickness, slope, or two
# curves merged into one run) plus half a pixel and the calibration misfit.
import importlib.util
import os

import numpy as np

_s = importlib.util.spec_from_file_location("_grid", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_grid.py"))
G = importlib.util.module_from_spec(_s)
_s.loader.exec_module(G)


def calibrate(image, cfg):
    ink = G.ink_mask(image, cfg.get("ink_thr"))
    H, W = ink.shape
    cols, rows = G.frame(ink, cfg.get("frame_frac", 0.6), cfg.get("frame_mode", "run"))
    left, bottom = min(cols), max(rows)
    # a frame side drawn dotted (as in Fig. 7) is not a solid line: take it from the gridlines.
    # A long solid line inside the box (a constant pressure in Fig. 5) is not the frame: the
    # frame's top (right) edge lies at or beyond the outermost gridline.
    m = cfg.get("margin", 6)
    go = cfg.get("grid_opts", {})
    right = max(cols) if max(cols) - left > 0.3 * W else None
    hg = G.gridlines(ink, left + m, (right if right is not None else W) - m, m, bottom - m, axis=1, **go)
    top = min(rows) if (bottom - min(rows) > 0.3 * H and min(rows) <= min(hg) + m) else min(hg)
    hg = [h for h in hg if h > top + m]
    vg = G.gridlines(ink, top + m, bottom - m, left + m, W - m, axis=0, **go)
    if vg and (right is None or right < max(vg) - m):
        right = max(vg)
    if right is None:
        right = float(W - 1)  # no right edge and no vertical gridlines (Fig. 10)
    if cfg.get("open_top"):
        top = 0.0  # no top edge, and curves rise above the highest gridline (Fig. 10)
    vg = [v for v in vg if v < right - m]
    ya_name, ya_val, y_step = cfg["y_anchor"]
    ya_px = {"bottom": bottom, "top": top, "gridlow": max(hg) if hg else None}[ya_name]
    tol = cfg.get("lattice_tol", 0.06)
    X = None
    if cfg.get("x_anchor"):
        xa_name, xa_val, x_step = cfg["x_anchor"]
        xa_px = {"left": left, "right": right, "gridlow": min(vg) if vg else None}[xa_name]
        X = G.Axis(vg, [left, right], xa_px, xa_val, x_step, increasing_px=True, tol=tol)
    Y = G.Axis(hg, [top, bottom], ya_px, ya_val, y_step, increasing_px=False, tol=tol)
    box = (left, right, top, bottom)
    note = (f"frame cols {left:.0f}-{right:.0f}, rows {top:.0f}-{bottom:.0f}; "
            + (f"{X.describe('x')}; " if X else "x not calibrated (no ticks); ") + Y.describe("y"))
    return ink, box, X, Y, note


def _pick(rs, rule):
    if isinstance(rule, tuple) and rule[0] == "near":
        # the run nearest a given row
        return min(rs, key=lambda r: 0 if r[0] <= rule[1] <= r[1] else min(abs(r[0] - rule[1]), abs(r[1] - rule[1]))) if rs else None
    if rule == "only":
        return rs[0] if len(rs) == 1 else None
    if rule == "top":
        return rs[0] if rs else None
    if rule == "bottom":
        return rs[-1] if rs else None
    if rule == "second":
        return rs[1] if len(rs) >= 2 else None
    if rule == "second_bottom":
        return rs[-2] if len(rs) >= 2 else None
    raise ValueError(rule)


def trace(th, c_seed, rule, c_lo, c_hi, r0, r1, gap=3, max_skip=12, width=None, join_gap=0):
    """Follow one curve from the run picked by `rule` at column c_seed, column by column
    both ways. At each column the run that overlaps the previous one (within `gap` rows)
    and lies nearest the position extrapolated from the last two columns is taken; text
    that does not touch the curve never overlaps it. Columns with no such run are skipped
    (up to max_skip in a row). Returns {column: (top, bottom)}."""
    seed = _pick(G.column_runs(th, c_seed, r0, r1), rule)
    if seed is None:
        raise ValueError(f"no seed run for rule '{rule}' at column {c_seed}")
    path = {c_seed: seed}
    for step in (1, -1):
        prev = [seed]
        last = seed  # last recorded run (steering or merged): the next run must touch it
        c = c_seed + step
        skipped = 0
        while c_lo < c < c_hi:
            rs = G.column_runs(th, c, r0, r1)
            if width:
                # a line split by a gap under join_gap px (a raster seam) is one run
                joined = []
                for r in rs:
                    if joined and r[0] - joined[-1][1] - 1 < join_gap:
                        joined[-1] = (joined[-1][0], r[1])
                    else:
                        joined.append(r)
                # slivers left where lines cross are not the curve
                rs = [r for r in joined if r[1] - r[0] + 1 >= width / 3]
            t, b = prev[-1]
            lt, lb = last
            # across a gap (a dashed line) the reach grows with the curve's recent slope
            slope = abs(0.5 * (t + b) - 0.5 * sum(prev[-2])) if len(prev) >= 2 else 0.0
            reach = gap + skipped * (1.0 + 1.5 * slope)
            near = [r for r in rs if r[0] <= lb + reach and r[1] >= lt - reach]
            if near:
                ctr = 0.5 * (t + b)
                pred = ctr + (ctr - 0.5 * sum(prev[-2])) if len(prev) >= 2 else ctr
                best = min(near, key=lambda r: abs(0.5 * (r[0] + r[1]) - pred))
                path[c] = best
                last = best
                # a run far longer than the last is the curve merged with an arrow or another
                # curve: kept (its extent is the interval) but not used to steer the trace
                if (best[1] - best[0]) <= 2.5 * (b - t) + 6:
                    prev = (prev + [best])[-2:]
                skipped = 0
            else:
                skipped += 1
                if skipped > max_skip:
                    break
            c += step
    return path


def read_curve(image, at, cfg):
    ink, (left, right, top, bottom), X, Y, note0 = calibrate(image, cfg)
    th = G.thick(ink, cfg.get("open", 3))
    if cfg.get("close"):
        # bridge the gaps of a dashed line: a closing with a disk of this diameter
        from scipy import ndimage
        d = int(cfg["close"])
        yy, xx = np.mgrid[:d, :d]
        disk = (yy - (d - 1) / 2) ** 2 + (xx - (d - 1) / 2) ** 2 <= ((d - 1) / 2) ** 2
        th = ndimage.binary_closing(th, structure=disk)
    m = cfg.get("margin", 6)
    r0, r1 = top + m, bottom - m
    if cfg.get("drop_hlines"):
        # long horizontal lines inside the box (constant boundary pressures) are not the curve
        sub = th[int(r0):int(r1), int(left + m):int(right - m)]
        lr = G.longest_runs(sub, 1)
        for r in np.flatnonzero(lr >= 0.8 * sub.shape[1]):
            th[int(r0) + r, :] = False
    out = []
    pick = cfg["pick"]
    window = cfg.get("window", 0)
    if pick == "trace":
        seeds = cfg["seed"] if isinstance(cfg["seed"], list) else [cfg["seed"]]
        w = G.line_width(th, left + m, right - m, r0, r1)
        def seed_col(sx, srule):
            # with seed_window, the seed is the column within the window whose picked run lies
            # highest ('top') or lowest (otherwise): on a dashed curve, a column with a dash
            c0 = int(round(X.px(sx)))
            sw = cfg.get("seed_window", 0)
            if not sw:
                return c0
            cands = []
            for c in range(c0 - sw, c0 + sw + 1):
                r = _pick(G.column_runs(th, c, r0, r1), srule)
                if r is not None:
                    cands.append((r[0] if srule == "top" else -r[1], abs(c - c0), c))
            return min(cands)[2]

        # each column takes the trace from the nearest seed that reaches it
        traces = []
        for sx, srule in seeds:
            cs = seed_col(sx, srule)
            traces.append((cs, trace(th, cs, srule, left + m, right - m, r0, r1, width=w,
                                     join_gap=cfg.get("join_gap", 0), max_skip=cfg.get("max_skip", 12))))
        path = {}
        for cs, p in sorted(traces, key=lambda t: t[0]):
            for c, r in p.items():
                if c not in path or abs(c - cs) < path[c][1]:
                    path[c] = (r, abs(c - cs))
        path = {c: v[0] for c, v in path.items()}
        where = ", ".join(f"the {r} run at x = {x:g}" for x, r in seeds)
        note0 = f"traced from {where} (line width {w} px); " + note0
        for x in at:
            c = int(round(X.px(x)))
            note = note0
            if c in path:
                a, b = path[c]
                mid = 0.5 * (a + b)
            else:
                # a gap in a dashed line: the curve lies between the traced runs on either side
                # (within `window` columns); the value is their midpoint, the interval spans both
                win = cfg.get("window", 0)
                lft = [k for k in path if c - win <= k < c]
                rgt = [k for k in path if c < k <= c + win]
                if not lft or not rgt:
                    out.append({"x": x, "y": None, "note": "the trace does not reach this column; " + note0})
                    continue
                ra, rb = path[max(lft)], path[min(rgt)]
                a, b = min(ra[0], rb[0]), max(ra[1], rb[1])
                w0, w1 = c - max(lft), min(rgt) - c
                mid = (0.5 * (ra[0] + ra[1]) * w1 + 0.5 * (rb[0] + rb[1]) * w0) / (w0 + w1)
                note = f"in a gap of the dashed line, between columns {max(lft)} and {min(rgt)}; " + note0
            ya, yb = Y.val(a - 0.5), Y.val(b + 0.5)
            out.append({"x": x, "y": Y.val(mid), "lo": min(ya, yb) - Y.misfit, "hi": max(ya, yb) + Y.misfit,
                        "px": [float(c), mid], "px_lo": float(a), "px_hi": float(b), "note": note})
        return out
    if pick == "hline":
        # constant lines across the box: rows of thick ink whose longest run is at least 80%
        # of the box width; 'which' picks the lowest or highest such line
        sub = th[int(r0):int(r1), int(left + m):int(right - m)]
        lr = G.longest_runs(sub, 1)
        lines = [(float(g.min()) + r0, float(g.max()) + r0) for g in G.groups(np.flatnonzero(lr >= 0.8 * sub.shape[1]))]
        a, b = lines[-1] if cfg["which"] == "lowest" else lines[0]
        mid = 0.5 * (a + b)
        ya, yb = Y.val(a - 0.5), Y.val(b + 0.5)
        note = f"{len(lines)} long horizontal lines in the box, the {cfg['which']} read; " + note0
        return [{"x": x, "y": Y.val(mid), "lo": min(ya, yb) - Y.misfit, "hi": max(ya, yb) + Y.misfit,
                 "px": [X.px(x), mid], "px_lo": a, "px_hi": b, "note": note} for x in at]
    for x in at:
        c0 = X.px(x)
        chosen, used = None, None
        for off in sorted(range(-window, window + 1), key=abs):
            c = int(round(c0)) + off
            if c <= left + m or c >= right - m:
                continue
            rs = G.column_runs(th, c, r0, r1)
            if cfg.get("min_run"):
                rs = [r for r in rs if r[1] - r[0] + 1 >= cfg["min_run"]]
            sel = None
            if pick == "only":
                sel = rs[0] if len(rs) == 1 else None
            elif pick == "top":
                sel = rs[0] if rs else None
            elif pick == "bottom":
                sel = rs[-1] if rs else None
            elif pick == "top_of_two":
                sel = rs[0] if len(rs) == 2 else None
            elif pick == "bottom_of_two":
                sel = rs[-1] if len(rs) == 2 else None
            if sel is not None:
                chosen, used = sel, c
                break
        if chosen is None:
            out.append({"x": x, "y": None, "note": f"no unambiguous run for rule '{pick}' in this column; " + note0})
            continue
        a, b = chosen
        mid = 0.5 * (a + b)
        y = Y.val(mid)
        ya, yb = Y.val(a - 0.5), Y.val(b + 0.5)
        lo, hi = min(ya, yb) - Y.misfit, max(ya, yb) + Y.misfit
        note = note0
        if used != int(round(c0)):
            # a dashed line: the nearest column with the dash; widen by the curve's change there
            note = f"read {used - int(round(c0))} px beside the x position (dashed line); " + note0
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [float(used), mid],
                    "px_lo": float(a), "px_hi": float(b), "note": note})
    return out
