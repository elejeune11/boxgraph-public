"""Shared reading code for the figures of liu2025, read at 110 dpi.

The figures of this PDF are the publisher's web images; at 110 dpi a panel's plot box is
150-200 px high, which sets the precision (about one pixel per percent of the axis).

Calibration (all from the image):
  spines  the left axis is the column of the crop's left part with the longest dark vertical run;
          the bottom axis is the row of the lower part with the longest dark horizontal run.
  ticks   x: the dark runs hanging below the bottom spine, per column (grouped); y: the dark runs
          sticking out left of the left spine, per row. Major ticks are those at least `major`
          (default 0.75) of the longest. The spine itself counts as a tick where its line
          continues past the other axis.
  labels  the stub names which major tick (0 = leftmost / lowest) carries which printed label;
          a least-squares line (linear or log10) of pixel against label value is the calibration,
          and its largest residual (at least half a pixel) is the misfit.
Curves: pixels of the series' colour (a box in RGB given by the stub); per column the runs of
that mask inside the plot box; the stub says whether the series is the top or bottom run there
(two lines of one colour family that do not cross) or the run nearest a previous column's.
The value is the run's centre; where a run is thicker than the line (two lines merged, or a steep
part), the interval covers the whole run.
Intervals (95%): half the line thickness, half the run's excess over it, the y misfit, one pixel,
and the curve's slope times the x misfit.
"""
import numpy as np


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def dark(img, thr=200, smax=40):
    f = img.astype(float)
    return (f.mean(axis=2) < thr) & ((f.max(axis=2) - f.min(axis=2)) < smax)


def _longest(v):
    best, start, run, s = 0, 0, 0, 0
    for i, x in enumerate(v):
        if x:
            if run == 0:
                s = i
            run += 1
            if run > best:
                best, start = run, s
        else:
            run = 0
    return best, start


def spines(img, spec):
    m = dark(img, spec.get("dark", 200))
    H, W = m.shape
    best_c = max(range(int(W * 0.5)), key=lambda c: _longest(m[:, c])[0])
    n, s = _longest(m[:, best_c])
    cols = [c for c in range(max(best_c - 3, 0), min(best_c + 4, W)) if _longest(m[:, c])[0] >= 0.85 * n]
    best_r = max(range(int(H * 0.4), H), key=lambda r: _longest(m[r])[0])
    nr, sr = _longest(m[best_r])
    rows = [r for r in range(max(best_r - 3, 0), min(best_r + 4, H)) if _longest(m[r])[0] >= 0.85 * nr]
    return {"c0": min(cols), "c1": max(cols), "top": s, "r0": min(rows), "r1": max(rows), "right": sr + nr}


def _ticks_x(m, sp, region):
    lo, hi = region
    out = {}
    for c in range(lo, hi):
        n = 0
        r = sp["r1"] + 1
        while r < m.shape[0] and m[r, c] and n < 30:
            n += 1
            r += 1
        if n >= 1:
            out[c] = n
    return out


def _ticks_y(m, sp, region):
    lo, hi = region
    out = {}
    for r in range(lo, hi):
        n = 0
        c = sp["c0"] - 1
        while c >= 0 and m[r, c] and n < 30:
            n += 1
            c -= 1
        if n >= 1:
            out[r] = n
    return out


def _majors(runs, frac):
    if not runs:
        return []
    groups = _groups(list(runs))
    items = [((g[0] + g[-1]) / 2.0, max(runs[p] for p in g)) for g in groups]
    L = max(n for _, n in items)
    return [p for p, n in items if n >= frac * L]


def fit(pix, marks, scale):
    p = np.array([pix[i] for i, _ in marks], float)
    u = np.array([np.log10(v) if scale == "log10" else v for _, v in marks], float)
    b, a = np.polyfit(u, p, 1)
    res = float(np.max(np.abs(p - (a + b * u))))
    return {"a": a, "b": b, "scale": scale, "misfit": max(res, 0.5), "pix": list(p)}


def to_px(ax, v):
    return ax["a"] + ax["b"] * (np.log10(v) if ax["scale"] == "log10" else v)


def to_val(ax, p):
    u = (p - ax["a"]) / ax["b"]
    return float(10 ** u) if ax["scale"] == "log10" else float(u)


def calibrate(img, spec):
    m = dark(img, spec.get("dark", 200))
    sp = spines(img, spec)
    H, W = m.shape
    xr = spec["x"].get("region", (sp["c0"], W))
    yr = spec["y"].get("region", (0, sp["r1"] + 1))
    xt = _majors(_ticks_x(m, sp, xr), spec["x"].get("major", 0.75))
    yt = _majors(_ticks_y(m, sp, yr), spec["y"].get("major", 0.75))
    xa = fit(sorted(xt), spec["x"]["marks"], spec["x"].get("scale", "linear"))
    ya = fit(sorted(yt, reverse=True), spec["y"]["marks"], spec["y"].get("scale", "linear"))
    return {"x": xa, "y": ya, "sp": sp, "xt": sorted(xt), "yt": sorted(yt)}


def colour_mask(img, lo, hi):
    f = img.astype(int)
    return np.all((f >= np.array(lo)) & (f <= np.array(hi)), axis=2)


def _runs(col):
    return [(float(g[0]), float(g[-1] + 1)) for g in _groups(np.where(col)[0])]


def read_curve(img, spec, at):
    cal = calibrate(img, spec)
    xa, ya, sp = cal["x"], cal["y"], cal["sp"]
    mask = colour_mask(img, *spec["rgb"])
    r_top = spec.get("r_top", 0)
    mask[: r_top, :] = False
    mask[sp["r0"] - spec.get("above_axis", 1):, :] = False
    mask[:, : sp["c1"] + 1] = False
    for (a, b, c, d) in spec.get("blank", []):
        mask[b:d, a:c] = False
    which = spec.get("pick", "top")
    min_run = spec.get("min_run", 1)

    def run_at(c):
        rs = [(a, b) for a, b in _runs(mask[:, c]) if b - a >= min_run]
        if not rs:
            return None
        if isinstance(which, int):  # the n-th run from the top, only where there are n_runs of them
            return rs[which] if len(rs) == spec.get("n_runs", which + 1) else None
        return rs[0] if which == "top" else rs[-1]

    lens = [b - a for c in range(mask.shape[1]) for r in [run_at(c)] if r for a, b in [r]]
    thick = float(np.median(lens)) if lens else 2.0
    out = []
    xcols = spec.get("x_at_col", {})
    for x in at:
        fixed = [fn for k, fn in xcols.items() if abs(x - k) <= 1e-9 * abs(k)]
        col = float(fixed[0](cal)) if fixed else float(to_px(xa, x))
        ci = int(np.floor(col))
        r = run_at(ci)
        if r is None:
            for d in (1, -1, 2, -2):
                r = run_at(ci + d)
                if r is not None:
                    break
        if r is None:
            out.append({"x": float(x), "y": None, "note": "no pixel of this colour at this x"})
            continue
        a, b = r
        L = b - a
        if which == "top" or (isinstance(which, int) and which == 0):
            cen = a + 0.5 * min(L, thick)
        elif which == "bottom":
            cen = b - 0.5 * min(L, thick)
        else:
            cen = 0.5 * (a + b)
        neigh = [run_at(c) for c in range(ci - 2, ci + 3)]
        cens = [(rr[0] + rr[1]) / 2 for rr in neigh if rr]
        slope = (max(cens) - min(cens)) / 4.0 if len(cens) > 1 else 0.0
        half_lo = cen - a if L > thick else 0.5 * thick
        half_hi = b - cen if L > thick else 0.5 * thick
        pad = ya["misfit"] + 1.0 + slope * xa["misfit"]
        y = to_val(ya, cen)
        v1, v2 = to_val(ya, cen - half_lo - pad), to_val(ya, cen + half_hi + pad)
        out.append({"x": float(x), "y": y, "lo": min(v1, v2), "hi": max(v1, v2), "px": [col, cen],
                    "px_lo": cen - half_lo - pad, "px_hi": cen + half_hi + pad,
                    "note": f"run {L:.0f} px (line {thick:.0f} px); x misfit {xa['misfit']:.1f} px "
                            f"({len(xa['pix'])} labelled ticks), y misfit {ya['misfit']:.1f} px "
                            f"({len(ya['pix'])} labelled ticks)"})
    return out
