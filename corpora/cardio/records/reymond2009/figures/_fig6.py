"""Shared reading code for Fig. 6 (PDF p. 11): flow and pressure in the common carotid (A) and the
thoracic aorta (B) predicted by the 1-D model with the detailed cerebral tree ('With cerebral
arterial tree', the gray line) and by the model of Stergiopulos et al. without it ('Without
cerebral arterial tree', the dark line), rendered at 1500 dpi. In all four panels the labels'
leader lines point the gray line to 'With' and the dark line to 'Without'.

Calibration, all from the image (ink: mean RGB < 200):
- the time axis: the scale bar is the lowest row band whose longest ink run spans more than 40%
  of the crop's width; its end ticks are the short vertical runs within 40 px of its ends, 15 px
  above or below it; x is the time from the left end tick (0) to the right one (0.8 s). The
  figure gives no time origin; x is the time from the left end of the scale bar.
- the y axis: the leftmost column band (in the left 25% of the crop) whose longest ink run is
  longer than 30% of the crop's height; its ticks are the short horizontal ink runs (< 40 px
  tall) 12-25 px left of it, within 20 px of the axis line's ends; exactly two are required; the
  upper carries the larger label. Two marks: 1 px is allowed for each.

The lines: of the ink right of the axis + 30 px and above the scale bar - 30 px, only connected
components wider than 30% of that region are kept (the two lines and the leader lines touching
them; the labels' letters are separate small components). Of the kept ink, the dark mask is
gray < 62 (the dark line and the dark-gray leader lines); the gray mask is 62 <= gray < 125,
less everything within 3 px of the dark mask (the dark line's anti-aliased rim). In each column
the runs of each mask at least 0.3 t tall are the candidates, t being the line's thickness (the
median height of dark runs where the line is flat).

Each line is traced by continuity, from a seed in the middle of the longest stretch of columns
holding exactly one candidate of its class, and again from the middle of the longest such
stretch more than a quarter of the plot away. At each column the candidate nearest to the
position the recent slope predicts (within max(30, 3|slope| + 30) px) is taken; with none, the
other line's run is taken if it lies within one line thickness of the prediction (the lines
coincide and this one is drawn under the other; its interval is that run widened by half a
line); gaps of up to 150 columns are bridged. Where the two traces disagree by more than t (a
leader line joining the line), the column is not read. The value is the run's centre; the
interval is 1 px (centre) + 1 px (calibration) + |slope| x 1 px + half the difference between the
run and t*sqrt(1+slope^2), or the whole run where it is taller than 1.6 t*sqrt(1+slope^2).
"""

import numpy as np


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    rr = _runs(v)
    return max(rr, key=lambda r: r[1] - r[0]) if rr else (0, 0)


def calibrate(image):
    im = image[..., :3].astype(np.int16)
    g = (im[..., 0] + im[..., 1] + im[..., 2]) / 3.0
    ink = g < 200
    H, W = ink.shape
    rows = [r for r in range(H) if (lambda a: a[1] - a[0])(_longest(ink[r])) > 0.4 * W]
    if not rows:
        raise RuntimeError("no scale bar found")
    b0, b1 = _runs(np.isin(np.arange(H), rows))[-1]
    a, b = _longest(ink[(b0 + b1) // 2])
    ends = []
    for target in (a, b - 1):
        found = []
        for r in (b0 - 15, b1 + 15):
            if 0 <= r < H:
                found += [(s + e - 1) / 2.0 for s, e in _runs(ink[r]) if e - s < 40 and abs((s + e - 1) / 2.0 - target) < 40]
        if not found:
            raise RuntimeError(f"no end tick near column {target}")
        ends.append(float(np.mean(found)))
    lengths = np.array([(lambda q: q[1] - q[0])(_longest(ink[: b0 - 20, c])) for c in range(int(0.25 * W))])
    cols = _runs(lengths > 0.3 * H)
    if not cols:
        raise RuntimeError("no y axis")
    c0, c1 = cols[0]
    s, e = _longest(ink[: b0 - 20, (c0 + c1) // 2])
    rows_t = set()
    for off in (12, 16, 20, 25):
        for p, q in _runs(ink[:, c0 - off]):
            if q - p < 40 and (abs(p - s) < 20 or abs(q - e) < 20):
                rows_t.add((p + q - 1) / 2.0)
    ticks = []
    for v in sorted(rows_t):
        if ticks and v - ticks[-1][-1] <= 10:
            ticks[-1].append(v)
        else:
            ticks.append([v])
    ticks = [float(np.mean(t)) for t in ticks]
    if len(ticks) != 2:
        raise RuntimeError(f"y ticks {ticks}")
    return dict(g=g, ink=ink, t0=ends[0], t1=ends[1], ticks=ticks, x_from=c1 + 30, y_to=b0 - 30)


def read(image, at, which, labels):
    """which: 'dark' (without cerebral tree) or 'gray' (with it); labels: (lower, upper) printed tick labels."""
    from scipy import ndimage

    cal = calibrate(image)
    g = cal["g"]
    ink = cal["ink"].copy()
    ink[:, : cal["x_from"]] = False
    ink[cal["y_to"]:, :] = False
    # keep only the long components (the two lines, with the leader lines touching them); the
    # labels' letters are separate small components
    lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab)
    keep = np.zeros(n + 1, bool)
    for i, o in enumerate(objs, start=1):
        if o is not None and o[1].stop - o[1].start > 0.3 * (ink.shape[1] - cal["x_from"]):
            keep[i] = True
    ink = keep[lab]
    lab_lo, lab_hi = labels
    hi_row, lo_row = cal["ticks"]
    per = (lab_hi - lab_lo) / (hi_row - lo_row)

    darkm = ink & (g < 62)
    graym = ink & (g >= 62) & (g < 125) & ~ndimage.binary_dilation(g < 62, iterations=3)
    masks = {"dark": darkm, "gray": graym}

    def classed(c):
        out = []
        for k, m in masks.items():
            out += [(a, b, k) for a, b in _runs(m[:, c])]
        return out

    hs = []
    for c in range(cal["x_from"], ink.shape[1] - 12, 8):
        for a, b in _runs(darkm[:, c]):
            q = [r for r in _runs(darkm[:, c + 12]) if abs((r[0] + r[1]) - (a + b)) / 24.0 < 0.05]
            if q:
                hs.append(b - a)
    t = float(np.median(hs)) if hs else 20.0

    W = ink.shape[1]
    cands = {}
    allruns = {}
    for c in range(cal["x_from"], W):
        rr = [r for r in classed(c) if r[1] - r[0] >= 0.3 * t]
        allruns[c] = rr
        cands[c] = [r for r in rr if r[2] == which]
    # trace the line by continuity from the middle of the longest stretch of columns holding
    # exactly one run of its class; at each column take the candidate run nearest to the position
    # the recent slope predicts, within max(30, 3 x |slope| + 30) px; gaps up to 150 columns
    # (where the other line hides it) are bridged. Leader lines and other runs of the same class
    # are thereby passed over.
    single = np.array([len(cands[c]) == 1 for c in range(cal["x_from"], W)])
    stretches = sorted(_runs(single), key=lambda r: -(r[1] - r[0]))
    if not stretches:
        raise RuntimeError(f"no seed column for the {which} line")
    seeds = [cal["x_from"] + (stretches[0][0] + stretches[0][1]) // 2]
    far = [s for s in stretches[1:] if abs(cal["x_from"] + (s[0] + s[1]) // 2 - seeds[0]) > 0.25 * (W - cal["x_from"])]
    if far:
        seeds.append(cal["x_from"] + (far[0][0] + far[0][1]) // 2)
    paths = [_trace(cands, allruns, which, t, s, cal["x_from"], W) for s in seeds]
    path, disagree = {}, set()
    for c in set().union(*paths):
        got = [p[c] for p in paths if c in p]
        cs = [(r[0] + r[1]) / 2.0 for r in got]
        if max(cs) - min(cs) > t:
            disagree.add(c)
        else:
            path[c] = got[0]

    out = []
    for x in at:
        col = cal["t0"] + x * (cal["t1"] - cal["t0"]) / 0.8
        c = int(round(col))
        if c in disagree:
            out.append({"x": x, "y": None, "note": "the traces from the two seeds disagree here (a leader line joins)"})
            continue
        if c not in path:
            out.append({"x": x, "y": None, "note": f"the traced {which} line does not reach this column"})
            continue
        a, b, k = path[c]
        row = (a + b - 1) / 2.0
        nb = [(path[kk][0] + path[kk][1] - 1) / 2.0 if kk in path else None for kk in (c - 10, c + 10)]
        sl = abs(nb[1] - nb[0]) / 20.0 if None not in nb else 0.0
        merged = b - a > 1.6 * t * np.sqrt(1 + sl * sl)
        if k == "hidden":
            e = (b - a) / 2.0 + t / 2.0 + 2.0
            note = "drawn under the other line here (they coincide); the other line's run widened by half a line is the interval; "
        elif merged:
            e = (b - a) / 2.0 + 2.0
            note = "both lines in one run here (they overlap); the whole run is the interval; "
        else:
            e = 1.0 + 1.0 + sl + abs((b - a) - t * np.sqrt(1 + sl * sl)) / 2.0
            note = ""
        y = lab_lo + (row - lo_row) * per
        y1 = lab_lo + (row + e - lo_row) * per
        y2 = lab_lo + (row - e - lo_row) * per
        out.append({"x": x, "y": y, "lo": min(y1, y2), "hi": max(y1, y2), "px": [col, row],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": note + f"{which} run {b - a} px (line {t:.0f} px); slope {sl:.2f}; {len(seeds)} seeds; "
                                   "two-tick y calibration; time from the scale bar's left end"})
    return out


def _trace(cands, allruns, which, t, seed, x_from, W):
    path = {seed: cands[seed][0]}
    for step in (-1, 1):
        hist = [(seed, sum(cands[seed][0][:2]) / 2.0)]
        c, gap = seed + step, 0
        while x_from <= c < W and gap <= 150:
            rec = hist[-8:]
            sl = (rec[-1][1] - rec[0][1]) / (rec[-1][0] - rec[0][0]) if len(rec) > 1 else 0.0
            pred = hist[-1][1] + sl * (c - hist[-1][0])
            best = min(cands[c], key=lambda r: abs((r[0] + r[1]) / 2.0 - pred), default=None)
            if best is not None and abs((best[0] + best[1]) / 2.0 - pred) <= max(30.0, 3 * abs(sl) + 30) + (best[1] - best[0]) / 2.0:
                path[c] = best
                hist.append((c, (best[0] + best[1]) / 2.0))
                gap = 0
            else:
                # no run of its own: if the other line's run lies within one line thickness of the
                # prediction, the two lines coincide here and this one is drawn under the other
                under = [r for r in allruns[c] if r[2] != which
                         and r[0] - t <= pred <= r[1] + t and abs((r[0] + r[1]) / 2.0 - pred) <= t * (1 + abs(sl))]
                if under:
                    r = min(under, key=lambda r: abs((r[0] + r[1]) / 2.0 - pred))
                    path[c] = (r[0], r[1], "hidden")
                    hist.append((c, (r[0] + r[1]) / 2.0))
                    gap = 0
                else:
                    gap += 1
            c += step
    return path
