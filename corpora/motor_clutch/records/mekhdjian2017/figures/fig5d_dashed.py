# Reading of one model curve on a log10(x) / linear(y) panel. Generated from one template for every
# curve of the record; the settings block at the top says which curve this file reads.
# Everything below comes from the image except the tick labels matched to the tick marks.
import numpy as np
from scipy import ndimage

# ---- settings for this reading -------------------------------------------------------------
COLOR = "green"          # green | black | orange | blue
PICK = "dashes"            # lowest: the lowest run of the colour in a column, within long components
                          # dashes: the dashed line, from the short components (dashes) of the colour
                          # topmost: the topmost run of the colour in a column
                          # track: the curve followed leftwards from its right end, run nearest the last
Y_LABELS = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600]      # tick labels of the y axis, bottom to top
X_LABELS = ["0.01", "0.1", "1", "10", "100"]      # tick labels of the log x axis (decades), left to right
FRAME = True           # True when the plot has a full box (top and right lines)
MAXRUN = 2.5         # longest run kept in a column, in line thicknesses (longer: lines overlap;
                          # a steep curve alone gives long runs, so it gets a larger value)
# ---------------------------------------------------------------------------------------------


def _mask(img):
    r, g, b = (img[..., i].astype(int) for i in range(3))
    if COLOR == "green":
        return (g - r > 40) & (g - b > 25)
    if COLOR == "orange":
        return (r > 180) & (r - b > 120) & (g > 70) & (g < 190)
    if COLOR == "blue":
        return (b > 150) & (b - r > 80)
    if COLOR == "black":
        return (r < 90) & (g < 90) & (b < 90) & (np.abs(r - g) < 30) & (np.abs(g - b) < 30)
    raise ValueError(COLOR)


def _dark(img):
    return img[..., :3].astype(int).sum(axis=2) < 300


def _runs(idx):
    """consecutive runs of sorted integer indices -> list of (start, end)"""
    if len(idx) == 0:
        return []
    cuts = np.flatnonzero(np.diff(idx) > 1)
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]]
    return list(zip(starts, ends))


def _axes(img):
    dark = _dark(img)
    h, w = dark.shape
    col = int(np.argmax(dark[:, : int(0.35 * w)].sum(axis=0)))       # the y axis line
    row = int(h * 0.5) + int(np.argmax(dark[int(h * 0.5):, :].sum(axis=1)))  # the x axis line
    # axis line thickness
    colw = [c for c in range(max(col - 15, 0), min(col + 15, w)) if dark[:, c].sum() > 0.6 * dark[:, col].sum()]
    roww = [q for q in range(max(row - 15, 0), min(row + 15, h)) if dark[q, :].sum() > 0.6 * dark[row, :].sum()]
    c0, c1, r0, r1 = min(colw), max(colw), min(roww), max(roww)
    # y ticks: short marks just left of the y axis
    strip = dark[:r1 + 1, max(c0 - 16, 0):c0 - 3].mean(axis=1)
    ty = [(a + b) / 2 for a, b in _runs(np.flatnonzero(strip > 0.6))]
    # x ticks: short marks just below the x axis
    strip = dark[r1 + 3:r1 + 16, c0:].mean(axis=0)
    tx = [c0 + (a + b) / 2 for a, b in _runs(np.flatnonzero(strip > 0.6))]
    if len(ty) != len(Y_LABELS) or len(tx) != len(X_LABELS):
        raise ValueError(f"found {len(ty)} y ticks and {len(tx)} x ticks, expected {len(Y_LABELS)} and {len(X_LABELS)}")
    yv = np.array(Y_LABELS[::-1], float)          # rows grow downward: top tick is the largest label
    ay = np.polyfit(ty, yv, 1)
    my = float(np.max(np.abs(np.polyval(ay, ty) - yv)))
    xv = np.log10(np.array(X_LABELS, float))
    ax = np.polyfit(tx, xv, 1)
    mx = float(np.max(np.abs(np.polyval(ax, tx) - xv)))
    return dict(c0=c0, c1=c1, r0=r0, r1=r1, ay=ay, ax=ax, my=my, mx=mx)


def _interior(img, A):
    m = _mask(img).copy()
    h, w = m.shape
    m[:, : A["c1"] + 4] = False
    m[A["r0"] - 3:, :] = False
    if FRAME:
        dark = _dark(img)
        top = int(np.argmax(dark[: int(0.3 * h), A["c1"]:].sum(axis=1)))
        right = A["c1"] + int(w * 0.6) + int(np.argmax(dark[:, A["c1"] + int(w * 0.6):].sum(axis=0)))
        m[: top + 6, :] = False
        m[:, right - 5:] = False
    return m


def _col_runs(m, c):
    return _runs(np.flatnonzero(m[:, c]))


def read(image, at):
    A = _axes(image)
    m = _interior(image, A)
    h, w = m.shape
    lab, n = ndimage.label(m)
    sl = ndimage.find_objects(lab)
    widths = np.array([s[1].stop - s[1].start for s in sl]) if n else np.array([])
    plotw = w - A["c1"]
    long_ids = {i + 1 for i in range(n) if widths[i] > 0.12 * plotw}
    short_ids = {i + 1 for i in range(n) if 0.008 * plotw < widths[i] <= 0.12 * plotw}
    keep = long_ids if PICK == "lowest" else short_ids if PICK == "dashes" else set(range(1, n + 1))
    mk = np.isin(lab, list(keep)) if keep else np.zeros_like(m)
    # line thickness: median run length of the kept pixels
    lens = [b - a + 1 for c in range(0, w, 7) for a, b in _col_runs(mk, c)]
    thick = float(np.median(lens)) if lens else 10.0
    dy_px = abs(A["ay"][0])               # data units per pixel (y)

    tracked = {}
    if PICK == "track":
        # follow the curve from its right end leftwards, keeping to the run nearest the last centre
        cols = [c for c in range(w - 1, -1, -1) if mk[:, c].any()]
        prev = None
        for c in cols:
            rs = [(a + b) / 2 for a, b in _col_runs(mk, c) if (b - a + 1) <= 2.5 * thick]
            if not rs:
                continue
            if prev is None:
                best = max(rs)
            else:
                best = min(rs, key=lambda q: abs(q - prev))
                if abs(best - prev) > 1.5 * thick:
                    continue
            tracked[c] = best
            prev = best

    def centre(c):
        if PICK == "track":
            return tracked.get(c)
        rs = _col_runs(mk, c)
        rs = [(a, b) for a, b in rs if (b - a + 1) <= MAXRUN * thick]   # drop blobs where lines overlap
        if not rs:
            return None
        a, b = max(rs) if PICK == "lowest" else min(rs)
        return (a + b) / 2

    out = []
    for xs in at:
        x = float(xs)
        c = int(round((np.log10(x) - A["ax"][1]) / A["ax"][0]))
        if c < 0 or c >= w:
            out.append({"x": x, "y": None, "note": "outside the crop"})
            continue
        note = ""
        row = centre(c)
        extra = 0.0
        if row is None:
            # gap (between dashes, or under an overlapping line): interpolate from the nearest columns
            left = next((k for k in range(c - 1, max(c - 300, 0), -1) if centre(k) is not None), None)
            right = next((k for k in range(c + 1, min(c + 300, w)) if centre(k) is not None), None)
            if left is None or right is None:
                out.append({"x": x, "y": None, "note": "no pixels of the curve near this x"})
                continue
            rl, rr = centre(left), centre(right)
            row = rl + (rr - rl) * (c - left) / (right - left)
            extra = abs(rr - rl) / 2 + 2
            note = f"interpolated across a gap of {right - left} px"
        y = float(np.polyval(A["ay"], row))
        # a steep stretch: a few columns of x uncertainty (calibration, line width) move y too
        ra, rb = centre(max(c - 8, 0)), centre(min(c + 8, w - 1))
        slope = abs(rb - ra) / 16 if ra is not None and rb is not None else 0.0
        half = (0.25 * thick + 2 + extra + slope * 4) * dy_px + A["my"]
        out.append({"x": x, "y": y, "lo": y - half, "hi": y + half, "px": [c, row],
                    "note": note or f"line {thick:.0f} px thick; y misfit {A['my']:.2g}"})
    return out
