"""Fig. 5 (PDF p. 10): log(l) against log(r), Huang et al. (1996) points and two least-squares lines.

The figure is a raster image in the PDF (rendered at 1200 dpi it is soft). Calibration
(_common.calibrate): x labels -5, -4, -3, -2, -1, 0, 1 under the box, y labels 4, 3, 2, 1, 0, -1, -2
left of it; the end labels sit at the frame lines, which are added as two more points per axis.

Markers: blue diamonds (larger radii) and red squares (smaller radii), found as blobs of their
colour; blobs closer than 12 px are one marker (the black fit line crosses the diamonds and cuts
them in two). Centre = middle of the blob's row extent (top and bottom vertices are clear of the
line) and the mean column of its pixels. Interval: 3 px + the y misfit.

Error bars (dark grey, with caps): followed up and down from the marker in its centre columns as
a run of grey neutral pixels; a bar shorter than 6 px beyond the marker is hidden in it and is
reported as at most the marker.

Lines: dark neutral pixels. The solid line is the dark run in a column that continues through
+-60 columns either side (text glyphs, caps and frame do not); the dashed line is a straight-line
fit through the dark neutral pixels, away from the red markers, in a +-60 column window.
"""
import importlib.util
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
c_ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c_)


def calibrate(image):
    return c_.calibrate(image, [-5, -4, -3, -2, -1, 0, 1], [4, 3, 2, 1, 0, -1, -2],
                        x_gap=30, x_height=140, x_merge=60, y_gap=20, y_width=180, margin=80,
                        x_from_frame=(-5, 1), y_from_frame=(4, -2))


def groups_first(rows, last):
    """The group of consecutive cap rows nearest the marker: the last group above it (last=False
    means rows above, nearest is the last group) or the first group below it."""
    gs = c_.groups(sorted(int(r) for r in rows), gap=2)
    return gs[-1] if not last else gs[0]


def masks(image):
    im = image[..., :3].astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    blue = (b > r + 60) & (b > g + 60)
    red = (r > g + 50) & (r > b + 30)
    return blue, red


def markers(image, which):
    """Marker extent: the blob of the marker's colour (a soft threshold that keeps the blurred
    edges), with pieces cut apart by the black line joined (dilation 16 px); the line may hide the
    middle of a marker but not both its top and bottom."""
    cal = calibrate(image)
    im = image[..., :3].astype(int)
    r_, g_, b_ = im[..., 0], im[..., 1], im[..., 2]
    soft = ((b_ > r_ + 30) & (b_ > g_ + 30)) if which == "blue" else ((r_ > g_ + 30) & (r_ > b_ + 20))
    m = c_.inside(cal, soft, 12)
    lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=16))
    g = c_.gray(image)
    capable = (c_.chroma(image) < 50) & (g > 30) & (g < 180)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        sub = (lab[sl] == i) & m[sl]
        if sub.sum() < 600:
            continue
        rr, cc = np.where(sub)
        rr = rr + sl[0].start
        cc = cc + sl[1].start
        r0, r1 = rr.min(), rr.max()
        rc = 0.5 * (r0 + r1)
        cx = 0.5 * (cc.min() + cc.max())
        lo, hi, plo, phi = c_.interval(cal, rc, rc, pad=5.0)
        row = {"x": cal["x_of"](cx), "y": cal["val_of"](rc), "lo": lo, "hi": hi, "px": [cx, rc],
               "px_lo": plo, "px_hi": phi}
        if which == "blue":
            ci = int(round(cx))
            stempx = (c_.chroma(image) < 50) & (g < 180)
            # caps: rows whose dark run through column ci is 40-110 px wide and centred on ci; a group
            # of such rows at most 26 px tall with free ends (white 10 rows above and below at ci +- 24),
            # which a slanted line or text does not have
            cap_rows = []
            for r in range(max(0, int(r0) - 300), min(image.shape[0] - 1, int(r1) + 300)):
                if not stempx[r, ci]:
                    continue
                a = ci
                while a > ci - 60 and stempx[r, a - 1]:
                    a -= 1
                b = ci
                while b < ci + 60 and stempx[r, b + 1]:
                    b += 1
                w = b - a + 1
                if 40 <= w <= 110 and abs(0.5 * (a + b) - ci) <= 12:
                    cap_rows.append(r)
            caps = []
            for grp in c_.groups(cap_rows, gap=1):
                ra, rb = grp[0], grp[-1]
                if rb - ra + 1 > 26 or ra < 10 or rb + 10 >= image.shape[0]:
                    continue
                if any(stempx[rr, ci + dc] for rr in (ra - 10, rb + 10) for dc in (-24, 24)):
                    continue
                caps.append(grp)
            cap_rows = [r for grp in caps for r in grp]
            stem_col = stempx[:, ci - 6: ci + 7].any(axis=1)

            def stem_ok(a, b):
                """A continuous stem (gaps <= 2 rows) joins rows a < b in the marker's centre columns."""
                gap = 0
                for r in range(a, b + 1):
                    gap = 0 if stem_col[r] else gap + 1
                    if gap > 2:
                        return False
                return True

            above = [r for r in cap_rows if r0 - 300 < r < r0 + 12]
            below = [r for r in cap_rows if r1 - 12 < r < r1 + 300]
            notes = []
            top_r = bot_r = None
            if above:
                grp = groups_first(above, last=False)
                if stem_ok(grp[-1], int(r0)):
                    top_r = float(np.mean(grp))
            if below:
                grp = groups_first(below, last=True)
                if stem_ok(int(r1), grp[0]):
                    bot_r = float(np.mean(grp))
            if top_r is None and bot_r is None:
                top_r, bot_r = float(r0), float(r1)
                notes.append("no error bar cap outside the marker: bar, if any, at most the marker")
            elif top_r is None:
                top_r = rc - (bot_r - rc)
                notes.append("upper cap hidden: mirror of the lower")
            elif bot_r is None:
                bot_r = rc + (rc - top_r)
                notes.append("lower cap hidden: mirror of the upper")
            p = 3 + cal["ymis"]
            row.update({"bar_hi": cal["val_of"](top_r), "bar_lo": cal["val_of"](bot_r),
                        "bar_hi_outer": cal["val_of"](top_r - p), "bar_lo_outer": cal["val_of"](bot_r + p)})
            row["note"] = "; ".join(notes + [f"marker rows {r0}-{r1}", c_.note(cal)])
        else:
            row["note"] = f"marker rows {r0}-{r1}; " + c_.note(cal)
        out.append(row)
    return sorted(out, key=lambda d: d["x"])


def solid_line(image, at, half=60):
    cal = calibrate(image)
    d = c_.inside(cal, c_.dark_neutral(image, level=90, max_chroma=50), 15)
    t, b = int(cal["top"]) + 15, int(cal["bot"]) - 15

    def continues(run, c0, step):
        r0, r1 = run
        for cc in range(c0 + step, c0 + step * (half + 1), step):
            nxt = [(a, bb) for a, bb in c_.column_runs(d, cc, t, b) if a <= r1 + 1 and bb >= r0 - 1]
            if not nxt:
                return False
            r0, r1 = min(a for a, _ in nxt), max(bb for _, bb in nxt)
        return True

    out = []
    for x in at:
        ci = int(round(cal["col_of"](x)))
        runs = [run for run in c_.column_runs(d, ci, t, b) if continues(run, ci, 1) and continues(run, ci, -1)]
        if len(runs) != 1:
            out.append({"x": x, "y": None, "note": f"{len(runs)} continuous dark runs in column {ci}"})
            continue
        r0, r1 = runs[0]
        rc = 0.5 * (r0 + r1)
        lo, hi, plo, phi = c_.interval(cal, r0, r1)
        out.append({"x": x, "y": cal["val_of"](rc), "lo": lo, "hi": hi, "px": [ci, rc], "px_lo": plo, "px_hi": phi,
                    "note": f"line rows {r0}-{r1}; " + c_.note(cal)})
    return out


def dashed_line(image, at, half=40):
    """Only rows within 60 px of the red markers' rows are searched (the dashed line joins them;
    the label text of the solid line sits far above)."""
    cal = calibrate(image)
    _, red = masks(image)
    d = c_.inside(cal, c_.dark_neutral(image, level=90, max_chroma=50), 15)
    d &= ~ndimage.binary_dilation(red, iterations=12)
    rr = np.where(c_.inside(cal, red, 12).any(axis=1))[0]
    band = np.zeros_like(d)
    band[max(0, rr.min() - 60): rr.max() + 60, :] = True
    return c_.read_color_curve(image, cal, at, d & band, half)
