CONFIG = {'dark': 128,
 'markers': [{'kind': 'circle_open', 'lw': 6, 'name': 'open circle', 'size': (92, 92), 'thr': 0.55},
             {'kind': 'tri_filled', 'lw': 6, 'name': 'filled triangle', 'size': (108, 89), 'thr': 0.7}],
 'read': 'filled triangle',
 'x': {'at_low_spine': 0, 'labels': [10, 20, 30, 40], 'tick_max': 70, 'tick_min': 12},
 'y': {'at_high_spine': 0,
       'labels': [0.2, 0.4, 0.6, 0.8, 1.0],
       'reverse': True,
       'tick_max': 70,
       'tick_min': 12}}

# ---- reading code (shared by this record's readings; only CONFIG above differs) ----
# Everything is found in the image: the plot box (the longest dark lines), the inward tick marks on
# the bottom and left spines (matched, in order, to the printed tick labels named in CONFIG; the
# mirror ticks on the top and right spines are used as a check), the markers (template matching
# of each marker shape on the dark-ink mask, the shape's size as drawn in the figure's own legend
# or plot) and the vertical error bars (caps found along the marker's column).
import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve


def _gray(image):
    return np.asarray(image, dtype=float)[..., :3].mean(axis=2)


def _runs(v):
    out, start = [], None
    for i, b in enumerate(list(v) + [False]):
        if b and start is None:
            start = i
        elif not b and start is not None:
            out.append((start, i))
            start = None
    return out


def _groups(xs):
    if not xs:
        return []
    xs = np.array(xs)
    return [(int(g[0]), int(g[-1])) for g in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)]


def _box(dark):
    """The plot box: rows and columns whose longest dark run spans most of the image."""
    H, W = dark.shape
    rowlen = np.array([max([e - s for s, e in _runs(dark[r])] or [0]) for r in range(H)])
    collen = np.array([max([e - s for s, e in _runs(dark[:, c])] or [0]) for c in range(W)])
    hs = _groups([r for r in range(H) if rowlen[r] > 0.55 * W])
    vs = _groups([c for c in range(W) if collen[c] > 0.55 * H])
    return hs[0], hs[-1], vs[0], vs[-1]   # top, bottom, left, right spines as (first, last) pixel


def _ticks(dark, spine, side, lo, hi, horizontal, min_len, max_len, max_w=16):
    """Tick marks leaving a spine on one side (side=-1 towards smaller pixel index).
    horizontal: the spine is a row (ticks are vertical runs), else a column."""
    lens = []
    for p in range(lo, hi):
        line = dark[:, p] if horizontal else dark[p, :]
        start = spine[0] - 1 if side < 0 else spine[1] + 1
        n, k, gap = 0, start, 0
        while 0 <= k < len(line):
            if line[k]:
                n, gap = abs(k - start) + 1, 0
            else:
                gap += 1
                if gap > 1:
                    break
            k += side
        lens.append(n if min_len <= n <= max_len else 0)
    lens = np.array(lens)
    out = []
    for s, e in _runs(lens > 0):
        if e - s <= max_w:
            out.append((lo + (s + e - 1) / 2.0 + 0.5, int(lens[s:e].max())))
    return out


def _regular(ps, n):
    """The n positions among candidates ps that are most nearly evenly spaced."""
    ps = sorted(ps)
    best, bres = None, None
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            for m in range(1, n):          # ps[i] and ps[j] are m ticks apart
                step = (ps[j] - ps[i]) / m
                if step < 20:
                    continue
                for k0 in range(n):        # ps[i] is tick k0
                    sel = []
                    for k in range(n):
                        t = ps[i] + (k - k0) * step
                        near = min(ps, key=lambda x: abs(x - t))
                        if abs(near - t) > max(4.0, 0.03 * step):
                            break
                        sel.append(near)
                    if len(sel) == n and len(set(sel)) == n:
                        res = float(np.ptp(np.diff(sel))) if n > 2 else 0.0
                        if bres is None or res < bres - 1e-9 or (abs(res - bres) < 1e-9 and sel[1] - sel[0] > best[1] - best[0]):
                            best, bres = sel, res
    return best


def _fit(pix, vals, log=False):
    p = np.array(pix, float)
    v = np.log10(np.array(vals, float)) if log else np.array(vals, float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs(p - (v - a) / b)))
    return a, b, mis


class _Axis:
    def __init__(self, a, b, log, mis, check):
        self.a, self.b, self.log, self.mis, self.check = a, b, log, mis, check

    def val(self, p):
        u = self.a + self.b * p
        return 10 ** u if self.log else u


def _axis(dark, box, which, cfg):
    top, bot, left, right = box
    if which == "x":
        lo, hi = left[1] + 2, right[0] - 1
        main = _ticks(dark, bot, -1, lo, hi, True, cfg["tick_min"], cfg["tick_max"])
        mirror = _ticks(dark, top, +1, lo, hi, True, cfg["tick_min"], cfg["tick_max"])
        ends = (left, right)
    else:
        lo, hi = top[1] + 2, bot[0] - 1
        main = _ticks(dark, left, +1, lo, hi, False, cfg["tick_min"], cfg["tick_max"])
        mirror = _ticks(dark, right, -1, lo, hi, False, cfg["tick_min"], cfg["tick_max"])
        ends = (top, bot)

    def pick(ticks):
        if cfg.get("log"):
            longest = max(n for _, n in ticks)
            major = sorted(p for p, n in ticks if n >= 0.75 * longest)
            minor = sorted(p for p, n in ticks if n < 0.75 * longest)
            return major, minor
        ps = [p for p, _ in ticks]
        return _regular(ps, len(cfg["labels"])), []

    if cfg.get("from_mirror"):  # the main spine's ticks are hidden by markers: calibrate on the mirror
        main, mirror = mirror, main
    pts, vals = [], []
    for ticks in (main,):
        major, minor = pick(ticks)
        if major is None or len(major) < len(cfg["labels"]):
            raise ValueError(f"{which} axis: found ticks {[round(p) for p, _ in ticks]}, need {len(cfg['labels'])}")
        major = major[:len(cfg["labels"])] if not cfg.get("reverse") else major[-len(cfg["labels"]):]
        lab = cfg["labels"][::-1] if cfg.get("reverse") else cfg["labels"]
        pts += list(major)
        vals += list(lab)
    for key, end in (("at_low_spine", ends[0]), ("at_high_spine", ends[1])):
        if cfg.get(key) is not None:  # a label printed at the corner, on the perpendicular spine
            pts.append((end[0] + end[1] + 1) / 2.0)
            vals.append(cfg[key])
    a, b, mis = _fit(pts, vals, cfg.get("log", False))
    check = None
    mm, _ = pick(mirror) if mirror else (None, None)
    if mm and len(mm) >= len(cfg["labels"]):
        mm = mm[:len(cfg["labels"])] if not cfg.get("reverse") else mm[-len(cfg["labels"]):]
        lab = cfg["labels"][::-1] if cfg.get("reverse") else cfg["labels"]
        u = np.log10(lab) if cfg.get("log") else np.array(lab, float)
        check = float(np.max(np.abs(np.array(mm) - (u - a) / b)))
    if cfg.get("log"):  # minor ticks of a log axis: 2..9 times each decade, as a check
        _, minor = pick(main)
        if minor:
            dec = [10 ** k * m for k in range(-4, 5) for m in range(2, 10)]
            res = []
            for p in minor:
                v = 10 ** (a + b * p)
                near = min(dec, key=lambda d: abs(np.log10(d) - np.log10(v)))
                res.append(abs(p - (np.log10(near) - a) / b))
            check = max(check or 0.0, float(np.max(res)))
    return _Axis(a, b, cfg.get("log", False), max(mis, 0.5), check)


def _shape(kind, size, lw):
    """Masks (shape ink, interior, outside band) of a marker centred on the kernel's centre.
    Triangles are centred on their centroid, as the figure places them (see the notes)."""
    W, H = size
    R = int(max(W, H) / 2 + lw + 6)
    y, x = np.mgrid[-R:R + 1, -R:R + 1].astype(float)
    if kind.startswith("circle"):
        r = np.hypot(x, y)
        outer = r <= W / 2
        inner = r <= W / 2 - lw
        band = (r > W / 2 + 3) & (r <= W / 2 + 3 + lw)
    elif kind.startswith("tri"):
        # apex up, centroid at 0: apex at -2H/3, base at +H/3
        yy = y + 2 * H / 3
        def tri(w, h, off):
            return (yy >= off) & (yy <= h + off) & (np.abs(x) <= (yy - off) / h * w / 2)
        outer = tri(W, H, 0)
        inner = tri(W - 3.4 * lw, H - 2.6 * lw, 1.8 * lw)
        big = tri(W + 4 * lw + 6, H + 2 * lw + 6, -(1.4 * lw + 4))
        band = big & ~tri(W + 12, H + 6, -8)
    elif kind.startswith("square"):
        outer = (np.abs(x) <= W / 2) & (np.abs(y) <= H / 2)
        inner = (np.abs(x) <= W / 2 - lw) & (np.abs(y) <= H / 2 - lw)
        band = (np.abs(x) <= W / 2 + 3 + lw) & (np.abs(y) <= H / 2 + 3 + lw) & ~((np.abs(x) <= W / 2 + 3) & (np.abs(y) <= H / 2 + 3))
    else:  # diamond
        d = np.abs(x) / (W / 2) + np.abs(y) / (H / 2)
        outer = d <= 1
        inner = d <= 1 - 2 * lw / W
        band = (d > 1 + 6 / W) & (d <= 1 + (6 + 2 * lw) / W)
    filled = kind.endswith("filled")
    ink = outer if filled else outer & ~inner
    return ink.astype(float), (inner & ~np.zeros_like(inner)).astype(float), band.astype(float), filled


def _corr(mask, k):
    return fftconvolve(mask.astype(float), k[::-1, ::-1], mode="same") / max(k.sum(), 1)


def _markers(dark, box, m, exclude):
    ink, inner, band, filled = _shape(m["kind"], m["size"], m["lw"])
    s_ink = _corr(dark, ink)
    s_band = _corr(dark, band)
    score = s_ink - m.get("band_w", 0.6) * s_band
    if not filled:
        # interior: lines and error bars may cross it, so only a mostly empty interior is asked for
        score = score - m.get("inner_w", 0.5) * _corr(dark, inner)
    top, bot, left, right = box
    ok = score > m["thr"]
    inside = np.zeros_like(ok)
    mg = int(m.get("margin", 0.35) * min(m["size"]))  # a marker lies (nearly) inside the plot box
    inside[top[1] + mg:bot[0] - mg, left[1] + mg:right[0] - mg] = True
    for (c0, r0, c1, r1) in exclude:
        inside[r0:r1, c0:c1] = False
    ok &= inside
    rad = int(m.get("nms", 0.45) * min(m["size"]))
    peak = ndi.maximum_filter(np.where(ok, score, -9), size=2 * rad + 1) == score
    lab, n = ndi.label(ok & peak)
    pts = []
    for k in range(1, n + 1):
        rr, cc = np.nonzero(lab == k)
        r, c = int(round(rr.mean())), int(round(cc.mean()))
        w = np.clip(score[r - 3:r + 4, c - 3:c + 4] - (score[r, c] - 0.02), 0, None)
        if w.sum() > 0:
            yy, xx = np.mgrid[r - 3:r + 4, c - 3:c + 4]
            rf, cf = (yy * w).sum() / w.sum(), (xx * w).sum() / w.sum()
        else:
            rf, cf = r, c
        pts.append([cf + 0.5, rf + 0.5, float(score[r, c]), m["name"]])
    if m.get("by_base"):
        pts = _by_base(dark, pts, m)
    if m.get("by_rim"):
        pts = _by_rim(pts, m)
    return pts


_GRAY = {}


def _by_rim(pts, m):
    """Open circles stacked almost on top of each other merge in the template score, but each crosses
    its own column twice, at its top and its bottom. Along the column of each group of detections,
    find the dark crossings (peaks of darkness) and pair them one circle diameter apart (less a line
    width); each pair is one circle, centred half-way."""
    from scipy.signal import find_peaks
    g = _GRAY["g"]
    D, lw = m["size"][0], m["lw"]
    s, tol = D - lw, m.get("rim_tol", 5)
    out, seen = [], set()
    srt = sorted(pts)
    for i, p in enumerate(srt):
        if i in seen:
            continue
        grp = [j for j, q in enumerate(srt) if abs(q[0] - p[0]) < 0.2 * D]
        seen.update(grp)
        qs = [srt[j] for j in grp]
        col = int(round(np.mean([q[0] for q in qs]) - 0.5))
        a = max(int(min(q[1] for q in qs) - D), 0)
        b = int(max(q[1] for q in qs) + D)
        prof = 255 - g[a:b, col - 3:col + 4].mean(axis=1)
        pk, _ = find_peaks(prof, height=m.get("rim_height", 60), distance=4)
        rows = [a + k + 0.5 for k in pk]
        used, found = set(), []
        for t in rows:
            if t in used:
                continue
            cand = [r for r in rows if r not in used and r != t and abs(r - t - s) <= tol]
            if cand:
                bt = min(cand, key=lambda r: abs(r - t - s))
                used.update([t, bt])
                found.append((t + bt) / 2)
        if not found:
            out += qs
            continue
        sc = float(np.mean([q[2] for q in qs]))
        out += [[col + 0.5, c, sc, m["name"]] for c in found]
    return out


def _by_base(dark, pts, m):
    """Open triangles stacked almost on top of each other merge in the template score, but each keeps
    its own base line. In each column of detections, find the base lines (dark runs as wide as a
    triangle, centred on the column) and place one triangle on each: centroid = base - H/3 + lw/2."""
    W, H = m["size"]
    lw = m["lw"]
    out, used = [], set()
    for i, p in enumerate(sorted(pts)):
        if i in used:
            continue
        grp = [j for j, q in enumerate(sorted(pts)) if abs(q[0] - p[0]) < 0.2 * W]
        used.update(grp)
        qs = [sorted(pts)[j] for j in grp]
        col = float(np.mean([q[0] for q in qs]))
        r0 = int(min(q[1] for q in qs) + H / 3 - 30)
        r1 = int(max(q[1] for q in qs) + H / 3 + 30)
        rows, cents = [], {}
        c0 = max(int(col - W), 0)
        for r in range(max(r0, 0), min(r1, dark.shape[0])):
            for s, e in _runs(dark[r, c0:int(col + W)]):
                s, e = s + c0, e + c0
                if s - 3 <= col <= e + 3:
                    if 0.85 * W <= e - s <= 1.12 * W and abs((s + e) / 2 - col) <= 0.1 * W:
                        rows.append(r)
                        cents[r] = (s + e) / 2
                    break
        bases = [(s, e) for s, e in _groups(rows) if e - s + 1 <= 2.5 * lw]
        if not bases:
            out += qs
            continue
        sc = float(np.mean([q[2] for q in qs]))
        for s, e in bases:
            b = (s + e + 1) / 2.0
            cc = float(np.mean([cents[r] for r in range(s, e + 1)])) + 0.5
            out.append([cc, b - H / 3 + lw / 2, sc, m["name"]])
    return out


def _caps(dark, col, r0, r1, eb, blocked):
    """Error-bar caps on column col between rows r0..r1: horizontal dark runs about as wide as a cap,
    centred on the column. Rows inside a filled marker (blocked: list of boxes) are not caps."""
    cap_w, lw = eb["cap_w"], eb["lw"]
    c0, c1 = max(int(col - 2.5 * cap_w), 0), int(col + 2.5 * cap_w)
    rows = []
    for r in range(max(r0, 0), min(r1, dark.shape[0])):
        if any(b0 <= r <= b1 and a0 <= col <= a1 for a0, b0, a1, b1 in blocked):
            continue
        for s, e in _runs(dark[r, c0:c1]):
            s, e = s + c0, e + c0
            if not (s - 3 <= col <= e + 3):
                continue
            whole = (eb.get("w_lo", 0.85) * cap_w <= e - s <= eb.get("w_hi", 1.12) * cap_w
                     and abs((s + e) / 2 - col) <= 0.12 * cap_w)
            # a cap merged on one side with a fit line crossing it: one clean end where a cap ends,
            # the run going on well past the other end
            right_clean = abs(e - col - cap_w / 2) <= 0.12 * cap_w and col - s > 0.62 * cap_w
            left_clean = abs(col - s - cap_w / 2) <= 0.12 * cap_w and e - col > 0.62 * cap_w
            if whole or right_clean or left_clean:
                rows.append(r)
            break
    return [(s + e + 1) / 2.0 for s, e in _groups(rows) if 0.5 * lw <= e - s + 1 <= 1.6 * lw]


def _marker_cfg(cfg, name):
    return next(m for m in cfg["markers"] if m["name"] == name)


def read(image, at):
    cfg = CONFIG
    g = _gray(image)
    _GRAY["g"] = g
    dark = g < cfg["dark"]
    box = _box(dark)
    xa = _axis(dark, box, "x", cfg["x"])
    ya = _axis(dark, box, "y", cfg["y"])
    pts = []
    for m in cfg["markers"]:
        pts += _markers(dark, box, m, cfg.get("exclude", []))
    # one place, one marker: of overlapping detections keep the best-scoring kind
    pts.sort(key=lambda p: -p[2])
    kept = []
    same = cfg.get("same", 0.35)
    for p in pts:
        msize = min(_marker_cfg(cfg, p[3])["size"])
        if any(abs(p[0] - q[0]) < same * msize and abs(p[1] - q[1]) < same * msize for q in kept):
            continue
        kept.append(p)
    mine = sorted([p for p in kept if p[3] == cfg["read"]])
    if at:  # only the markers plotted at these x positions (within 5%)
        mine = [p for p in mine if any(abs(xa.val(p[0]) - float(a)) <= 0.05 * abs(float(a)) for a in at)]
    cal = (f"x misfit {xa.mis:.1f} px" + (f" (check ticks {xa.check:.1f} px)" if xa.check is not None else "")
           + f", y misfit {ya.mis:.1f} px" + (f" (check ticks {ya.check:.1f} px)" if ya.check is not None else ""))
    bars = _bars(dark, kept, cfg, ya) if cfg.get("error_bars") else {}
    out = []
    for c, r, s, name in mine:
        msz = min(_marker_cfg(cfg, name)["size"])
        covered = [q for q in kept if q[3] != name and abs(q[0] - c) < 0.8 * msz and abs(q[1] - r) < 0.8 * msz]
        e = cfg.get("centre_px", 3.0) * (3 if covered else 1) + ya.mis
        y0, y1 = sorted([ya.val(r - e), ya.val(r + e)])
        row = {"x": float(xa.val(c)), "y": float(ya.val(r)), "lo": float(y0), "hi": float(y1),
               "px": [float(c), float(r)], "note": f"{name} centre, score {s:.2f}; {cal}"}
        if cfg.get("marker_as_bar"):
            # no bar is drawn; the caption gives the uncertainty as about the size of a marker: the
            # marker's own height, measured as drawn (CONFIG size), centred on its centre
            hh = _marker_cfg(cfg, name)["size"][1] / 2
            pad = ya.mis + 2
            row.update(bar_lo=float(ya.val(r + hh)), bar_hi=float(ya.val(r - hh)),
                       bar_lo_outer=float(ya.val(r + hh + pad)), bar_hi_outer=float(ya.val(r - hh - pad)),
                       px_lo=float(r - hh), px_hi=float(r + hh))
            row["note"] += "; uncertainty bar = the marker's height (the caption: about the size of the markers)"
        if covered:
            row["note"] += f"; overlaps another marker ({covered[0][3]}): centre less certain (interval tripled)"
        if _marker_cfg(cfg, name).get("by_rim"):
            row["note"] = f"{name} centred half-way between its own top and bottom crossings of column {c:.0f}; " + row["note"]
        if _marker_cfg(cfg, name).get("by_base"):
            row["note"] = f"{name} centroid placed from its own base line (column {c:.0f}, row {r:.0f}); " + row["note"]
        b = dict(bars.get((c, r), {}))
        if b:
            note = b.pop("note", None)
            row.update(b)
            if note:
                row["note"] += "; " + note
        out.append(row)
    return out


def _bars(dark, kept, cfg, ya):
    """Error bars of every marker. Markers that share a column share its caps: each marker gets an
    upper and a lower cap (or none, when its bar end is hidden in the marker), each cap used once,
    choosing the assignment whose bars are most nearly symmetric and that leaves fewest caps unused."""
    import itertools
    eb = cfg["error_bars"]
    blocked = []
    for c, r, _, name in kept:
        m = _marker_cfg(cfg, name)
        if m["kind"].endswith("filled"):
            # rows where the filled marker is itself about as wide as a cap (or wider) cannot show a cap
            W, H = m["size"]
            wmin = 0.8 * eb["cap_w"]
            if wmin < W:
                if m["kind"].startswith("tri"):   # apex up, centroid at 0: width grows to W at the base (+H/3)
                    blocked.append((c - W / 2, r - 2 * H / 3 + wmin / W * H - 3, c + W / 2, r + H / 3 + 4))
                else:                             # diamond: width W at the centre
                    dy = (1 - wmin / W) * H / 2
                    blocked.append((c - W / 2, r - dy - 3, c + W / 2, r + dy + 3))
    groups, seen = [], set()
    for i, p in sorted(enumerate(kept), key=lambda t: t[1][0]):
        if i in seen:
            continue
        # markers in one column whose bars could reach each other share the caps found there
        grp = [j for j, q in enumerate(kept) if j not in seen and abs(q[0] - p[0]) < eb.get("same_col", 0.3) * eb["cap_w"]
               and abs(q[1] - p[1]) < eb["span"]]
        seen.update(grp)
        groups.append(sorted([kept[j] for j in grp], key=lambda q: q[1]))
    out = {}
    pad = eb["lw"] / 2 + ya.mis + 2
    for grp in groups:
        col = float(np.mean([q[0] for q in grp]))
        r0 = int(min(q[1] for q in grp) - eb["span"])
        r1 = int(max(q[1] for q in grp) + eb["span"])
        caps = _caps(dark, col, r0, r1, eb, blocked)
        # a cap nearer to a marker of another group in this column belongs to that one
        colmates = [q for q in kept if abs(q[0] - col) < eb.get("same_col", 0.3) * eb["cap_w"]]
        caps = [cp for cp in caps if min(colmates, key=lambda q: abs(q[1] - cp)) in grp]
        n = len(grp)
        half = [_marker_cfg(cfg, q[3])["size"][1] / 2 for q in grp]
        opts_up = [[k for k, cp in enumerate(caps) if cp < q[1] - 2] + [None] for q in grp]
        opts_dn = [[k for k, cp in enumerate(caps) if cp > q[1] + 2] + [None] for q in grp]
        best = None
        for ups in itertools.product(*opts_up):
            for dns in itertools.product(*opts_dn):
                chosen = [k for k in ups + dns if k is not None]
                if len(chosen) != len(set(chosen)):
                    continue
                cost = eb.get("unused_px", 60) * (len(caps) - len(chosen))
                for i, q in enumerate(grp):
                    du = q[1] - caps[ups[i]] if ups[i] is not None else half[i]
                    dd = caps[dns[i]] - q[1] if dns[i] is not None else half[i]
                    cost += abs(du - dd)
                if best is None or cost < best[0] - 1e-9:
                    best = (cost, ups, dns)
        _, ups, dns = best
        unused = [cp for k, cp in enumerate(caps) if k not in set(ups + dns)]
        for i, q in enumerate(grp):
            u = caps[ups[i]] if ups[i] is not None else q[1] - half[i]
            d = caps[dns[i]] if dns[i] is not None else q[1] + half[i]
            notes = []
            if ups[i] is None or dns[i] is None:
                side = " and ".join(s for s, k in (("upper", ups[i]), ("lower", dns[i])) if k is None)
                notes.append(f"no {side} cap outside the marker: that end is hidden in it and taken as at most its edge")
            hi_o, lo_o = u - pad, d + pad
            if n > 1:
                notes.append(f"{n} markers share this column; caps paired with markers so that each bar is as nearly "
                             "symmetric as possible (an assumption); the outer interval spans every cap on each side")
                hi_o = min([cp for cp in caps if cp < q[1]] + [u]) - pad
                lo_o = max([cp for cp in caps if cp > q[1]] + [d]) + pad
            if unused:
                notes.append(f"{len(unused)} more cap(s) on this column belong to no marker found (a marker hidden "
                             "behind this one?); the outer interval spans them too")
                hi_o = min([cp for cp in unused if cp < q[1]] + [hi_o + pad]) - pad
                lo_o = max([cp for cp in unused if cp > q[1]] + [lo_o - pad]) + pad
            res = {"bar_lo": float(ya.val(d)), "bar_hi": float(ya.val(u)),
                   "bar_lo_outer": float(ya.val(lo_o)), "bar_hi_outer": float(ya.val(hi_o)),
                   "px_lo": float(u), "px_hi": float(d)}
            if notes:
                res["note"] = "; ".join(notes)
            out[(q[0], q[1])] = res
    return out


