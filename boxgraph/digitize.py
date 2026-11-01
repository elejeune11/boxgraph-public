"""Reading values from figures (02-boxgraph.md, Values read from figures).

Coordinates are continuous image coordinates: pixel (row i, column j) spans
[j, j+1) x [i, i+1), so its centre is (j + 0.5, i + 0.5). Rows grow downward.

The pieces:
  render / load_image   a page region as an RGB array
  find_axes             axis lines, tick marks and the plot box, to the pixel
  Axis                  a calibration: marks (pixel, printed value), linear or log10
  read_curve            a curve of one colour, read at given x values
  read_markers          plotted points of one colour
  overlay               what was read, drawn over the figure, for a person to check

Every reading carries an interval [lo, hi]: the precision the reading
supports, from the line's thickness in that column, half a pixel of
quantisation, and the curve's slope across the offset to the pixel column.
"""

from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


class CalibrationError(ValueError):
    pass


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------


def load_image(path: str | Path) -> np.ndarray:
    from PIL import Image

    with Image.open(path) as im:
        return np.asarray(im.convert("RGB")).copy()


def render(pdf: str | Path, page: int, dpi: int = 300, crop: tuple[int, int, int, int] | None = None) -> np.ndarray:
    """Render a PDF page, or a region (x0, y0, x1, y1) in pixels at this dpi, as RGB."""
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("pdftoppm (poppler) is required")
    with tempfile.TemporaryDirectory() as td:
        stem = Path(td) / "page"
        cmd = ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi), "-png", "-singlefile"]
        if crop:
            x0, y0, x1, y1 = (int(round(v)) for v in crop)
            cmd += ["-x", str(x0), "-y", str(y0), "-W", str(x1 - x0), "-H", str(y1 - y0)]
        subprocess.run(cmd + [str(pdf), str(stem)], check=True, capture_output=True)
        return load_image(stem.with_suffix(".png"))


def parse_color(color: str | tuple) -> np.ndarray:
    if isinstance(color, str):
        c = color.lstrip("#")
        return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)
    return np.array(color, dtype=float)


def color_mask(img: np.ndarray, color, tol: float | None = None) -> np.ndarray:
    """Pixels of a colour. With `tol`, those within that distance of it. By default:
    for black or grey ink, every pixel darker than halfway between paper and ink
    (so faded scans still match); for a coloured line, a distance of 100."""
    target = parse_color(color)
    if tol is None:
        if target.max() - target.min() < 40 and target.mean() < 128:  # black or dark grey ink
            gray = img.astype(float).mean(axis=2)
            return gray <= dark_threshold(gray)
        tol = 100.0
    d = np.sqrt(((img.astype(float) - target) ** 2).sum(axis=2))
    return d <= tol


def find_skew(img: np.ndarray, dark: float | None = None, max_deg: float = 3.0, step: float = 0.02) -> float:
    """The angle in degrees (counter-clockwise) by which the figure's longest
    straight dark line, normally an axis, is tilted from horizontal."""
    gray = img.astype(float).mean(axis=2)
    rr, cc = np.nonzero(gray < (dark if dark is not None else dark_threshold(gray)))
    if len(rr) < 50:
        return 0.0
    if len(rr) > 200_000:
        pick = np.random.default_rng(0).choice(len(rr), 200_000, replace=False)
        rr, cc = rr[pick], cc[pick]
    degs = np.arange(-max_deg, max_deg + step / 2, step)
    peaks = []
    for deg in degs:
        b = math.tan(math.radians(deg))
        proj = np.round(rr - cc * b).astype(int)
        proj -= proj.min()
        peaks.append(np.bincount(proj).max())
    peaks = np.array(peaks, dtype=float)
    # a thick line looks equally straight over a small range of angles: take the middle of that range
    near = degs[peaks >= peaks.max() * 0.97]
    centre = degs[int(np.argmax(peaks))]
    near = near[np.abs(near - centre) <= 1.0]
    return -float((near.min() + near.max()) / 2)  # counter-clockwise tilt: the line rises to the right


def deskew(img: np.ndarray, min_deg: float = 0.1) -> np.ndarray:
    """Rotate a tilted figure straight. Tilts under min_deg are left alone, so
    clean figures keep their exact pixels."""
    angle = find_skew(img)
    if abs(angle) < min_deg:
        return img
    from PIL import Image

    im = Image.fromarray(img).rotate(-angle, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
    return np.asarray(im).copy()


def _restrict(mask: np.ndarray, box, inset: float = 4.0) -> np.ndarray:
    if box is None:
        return mask
    c0, r0, c1, r1 = box
    out = np.zeros_like(mask)
    rs, re = int(math.ceil(r0 + inset)), int(math.floor(r1 - inset))
    cs, ce = int(math.ceil(c0 + inset)), int(math.floor(c1 - inset))
    out[rs:re, cs:ce] = mask[rs:re, cs:ce]
    return out


# --------------------------------------------------------------------------
# Calibration
# --------------------------------------------------------------------------


@dataclass
class Axis:
    """Marks are (pixel coordinate, printed value) pairs. Pixel is a column
    coordinate for an x axis and a row coordinate for a y axis."""

    scale: str
    marks: list[tuple[float, float]]
    a: float = field(init=False)
    b: float = field(init=False)
    residual_px: float = field(init=False)

    def __post_init__(self):
        if self.scale not in ("linear", "log10"):
            raise CalibrationError(f"unknown axis scale {self.scale!r}")
        pts = [(float(p), float(v)) for p, v in self.marks]
        if self.scale == "log10":
            if any(v <= 0 for _, v in pts):
                raise CalibrationError("a logarithmic axis needs positive marks")
            pts = [(p, math.log10(v)) for p, v in pts]
        ps, us = np.array([p for p, _ in pts]), np.array([u for _, u in pts])
        if len(set(ps.round(6))) < 2 or len(set(us.round(12))) < 2:
            raise CalibrationError("an axis needs at least two marks at distinct positions and values")
        self.b, self.a = np.polyfit(ps, us, 1)  # u = a + b p
        self.residual_px = float(np.max(np.abs(ps - (us - self.a) / self.b)))

    def _u(self, v: float) -> float:
        return math.log10(v) if self.scale == "log10" else v

    def to_value(self, p: float) -> float:
        u = self.a + self.b * p
        return 10.0**u if self.scale == "log10" else u

    def to_pixel(self, v: float) -> float:
        return (self._u(v) - self.a) / self.b


# --------------------------------------------------------------------------
# Finding axes and ticks
# --------------------------------------------------------------------------


@dataclass
class FoundAxes:
    x_axis_row: float
    y_axis_col: float
    x_ticks: list[float]
    y_ticks: list[float]
    box: tuple[float, float, float, float]  # (c0, r0, c1, r1) in continuous coordinates
    x_minor: list[float] = field(default_factory=list)  # candidates not in the evenly spaced set
    y_minor: list[float] = field(default_factory=list)
    x_candidates: list[float] = field(default_factory=list)  # every tick-like mark, numbered in overlays
    y_candidates: list[float] = field(default_factory=list)


def regular_ticks(cands: list[float], tol: float = 1.5, min_gap: float = 6.0) -> list[float]:
    """The largest evenly spaced subset of candidate positions (labelled ticks are
    evenly spaced in value on a linear axis and in decades on a log axis).
    Ties go to the wider spacing."""
    c = sorted(cands)
    if len(c) <= 2:
        return c
    best: list[float] = []
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            step = c[j] - c[i]
            if step < min_gap:
                continue
            members = [c[i], c[j]]
            while True:
                est = (members[-1] - members[0]) / (len(members) - 1)  # re-estimated: rounding alternates
                target = members[-1] + est
                within = max(tol, 0.015 * est)  # noise in a scan moves a tick by a share of the spacing
                near = [x for x in c if abs(x - target) <= within]
                if not near:
                    break
                members.append(min(near, key=lambda x: abs(x - target)))
            if any(abs(c[k] - (c[i] + step / 2)) <= tol for k in range(i + 1, j)) and len(members) == 2:
                continue
            if len(members) > len(best) or (len(members) == len(best) and len(best) > 1
                                             and members[1] - members[0] > best[1] - best[0]):
                best = members
    return best if len(best) >= 2 else c


def _longest_run(v: np.ndarray, gap: int = 3) -> tuple[int, int, int]:
    """Length, start, end (exclusive) of the longest run of True, bridging gaps of
    up to `gap` pixels (noise in a scanned line)."""
    best, bs, be = 0, 0, 0
    start, last = None, None
    for i, x in enumerate(list(v) + [False] * (gap + 1)):
        if x:
            if start is None:
                start = i
            last = i
        elif start is not None and i - last > gap:
            if last + 1 - start > best:
                best, bs, be = last + 1 - start, start, last + 1
            start = None
    return best, bs, be


def dark_threshold(gray: np.ndarray) -> float:
    """Halfway between the paper and the darkest ink, so a faded scan still has ink."""
    paper = float(np.percentile(gray, 60))
    ink = float(np.percentile(gray, 0.5))
    return (paper + ink) / 2


def find_axes(img: np.ndarray, dark: float | None = None, min_frac: float = 0.3) -> FoundAxes:
    gray = img.astype(float).mean(axis=2)
    d = gray < (dark if dark is not None else dark_threshold(gray))
    H, W = d.shape
    rows = [(r, *_longest_run(d[r])) for r in range(H)]
    long_rows = [x for x in rows if x[1] >= min_frac * W]
    cols = [(c, *_longest_run(d[:, c])) for c in range(W)]
    long_cols = [x for x in cols if x[1] >= min_frac * H]
    if not long_rows or not long_cols:
        raise CalibrationError("no axis lines found")
    # the x axis is the lowest long horizontal line (one spine may be several pixels thick)
    xr = max(r for r, *_ in long_rows)
    x_rows = [r for r, *_ in long_rows if xr - r <= 6]
    _, xc0, xc1 = max((x for x in long_rows if x[0] in x_rows), key=lambda x: x[1])[1:]
    yc = min(c for c, *_ in long_cols)
    y_cols = [c for c, *_ in long_cols if c - yc <= 6]
    _, yr0, yr1 = max((x for x in long_cols if x[0] in y_cols), key=lambda x: x[1])[1:]
    ra0, ra1 = min(x_rows), max(x_rows)
    ca0, ca1 = min(y_cols), max(y_cols)

    def run_from(line: np.ndarray) -> int:
        """Length of the dark run starting at the first one or two pixels of a line."""
        k = 0
        while k < 2 and k < len(line) and not line[k]:
            k += 1
        n = 0
        while k + n < len(line) and line[k + n]:
            n += 1
        return n

    def ticks(lengths: dict[int, int], cap: float) -> tuple[list[float], list[float]]:
        """Group neighbouring positions with a short perpendicular run into ticks;
        split into major and minor ticks by length."""
        pos = sorted(p for p, n in lengths.items() if 2 <= n <= cap)
        groups, cur = [], []
        for p in pos + [None]:
            if cur and (p is None or p != cur[-1] + 1):
                if len(cur) <= 8:
                    groups.append(((cur[0] + cur[-1]) / 2 + 0.5, max(lengths[q] for q in cur)))
                cur = []
            if p is not None:
                cur.append(p)
        if not groups:
            return [], []
        longest = max(n for _, n in groups)
        major = [c for c, n in groups if n >= 0.75 * longest]
        minor = [c for c, n in groups if n < 0.75 * longest]
        return major, minor

    cap_x = 0.15 * (yr1 - yr0)
    cap_y = 0.15 * (xc1 - xc0)
    x_out = ticks({c: run_from(d[ra1 + 1:, c]) for c in range(xc0, xc1)}, cap_x)
    x_in = ticks({c: run_from(d[:ra0, c][::-1]) for c in range(xc0, xc1)}, cap_x)
    y_out = ticks({r: run_from(d[r, :ca0][::-1]) for r in range(yr0, yr1)}, cap_y)
    y_in = ticks({r: run_from(d[r, ca1 + 1:]) for r in range(yr0, yr1)}, cap_y)
    x_major, x_minor = x_out if len(x_out[0]) + len(x_out[1]) >= len(x_in[0]) + len(x_in[1]) else x_in
    y_major, y_minor = y_out if len(y_out[0]) + len(y_out[1]) >= len(y_in[0]) + len(y_in[1]) else y_in
    x_cands, y_cands = sorted(x_major + x_minor), sorted(y_major + y_minor)
    def labelled(major: list[float], cands: list[float]) -> list[float]:
        # the longest marks first (minor ticks on a log axis are shorter); fall back to every
        # candidate when that gives fewer than three (a curve touching the axis can be "longest")
        among_major = regular_ticks(major)
        return among_major if len(among_major) >= 3 else regular_ticks(cands)

    x_ticks, y_ticks = labelled(x_major, x_cands), labelled(y_major, y_cands)
    x_minor = [c for c in x_cands if c not in x_ticks]
    y_minor = [c for c in y_cands if c not in y_ticks]
    top = min(r for r, *_ in long_rows)
    right = max(c for c, *_ in long_cols)
    box = (ca1 + 1.0, (top + 1.0) if top < ra0 - 6 else float(yr0), (right * 1.0) if right > ca1 + 6 else float(xc1),
           float(ra0))
    return FoundAxes(x_axis_row=(ra0 + ra1) / 2 + 0.5, y_axis_col=(ca0 + ca1) / 2 + 0.5,
                     x_ticks=x_ticks, y_ticks=y_ticks, box=box, x_minor=x_minor, y_minor=y_minor,
                     x_candidates=x_cands, y_candidates=y_cands)


# --------------------------------------------------------------------------
# Readings
# --------------------------------------------------------------------------


@dataclass
class Reading:
    x: float
    y: float | None
    lo: float | None
    hi: float | None
    found: bool
    note: str = ""
    px: tuple[float, float] | None = None  # (column, row) of the reading
    # error bar, if read: best ends, and the ends widened by their reading precision
    bar_lo: float | None = None
    bar_hi: float | None = None
    bar_lo_outer: float | None = None
    bar_hi_outer: float | None = None
    bar_px: tuple[float, float] | None = None  # rows of the bar's upper and lower ends


def _misfit(axis: Axis) -> float:
    """Calibration uncertainty in pixels: how far the marks disagree with the fit,
    and never less than half a pixel (where a mark was placed)."""
    return max(axis.residual_px, 0.5)


def _runs(rows: np.ndarray) -> list[tuple[int, int]]:
    out, start, prev = [], None, None
    for r in list(rows) + [None]:
        if start is None:
            start = prev = r
            continue
        if r is not None and r == prev + 1:
            prev = r
            continue
        out.append((int(start), int(prev)))
        start = prev = r
    return [x for x in out if x[0] is not None]


def _column_center(mask: np.ndarray, col: int) -> list[tuple[float, float]]:
    """Centres and half-heights of the runs of the mask in a column."""
    if not (0 <= col < mask.shape[1]):
        return []
    rows = np.nonzero(mask[:, col])[0]
    return [((s + e) / 2 + 0.5, (e - s + 1) / 2) for s, e in _runs(rows)]


def trace(mask: np.ndarray, seed: tuple[float, float], max_gap: int = 6) -> dict[int, tuple[float, float, bool]]:
    """Follow one curve from a seed point (column, row), column by column in both
    directions, choosing the run nearest to where the curve's recent slope says it
    should be. Returns column -> (centre, half-height, ambiguous). Where curves
    merge (a crossing), the centre is the prediction and the half-height covers
    the whole merged run, marked ambiguous."""
    W = mask.shape[1]
    c0 = int(math.floor(seed[0]))
    runs0 = _column_center(mask, c0)
    if not runs0:
        for dc in (1, -1, 2, -2, 3, -3):
            runs0 = _column_center(mask, c0 + dc)
            if runs0:
                c0 += dc
                break
    if not runs0:
        return {}
    start = min(runs0, key=lambda r: abs(r[0] - seed[1]))
    typical = start[1]
    path: dict[int, tuple[float, float, bool]] = {c0: (start[0], start[1], False)}
    for step in (1, -1):
        hist = [(c0, start[0])]
        c, gap = c0 + step, 0
        while 0 <= c < W and gap <= max_gap:
            recent = hist[-6:]
            slope = (recent[-1][1] - recent[0][1]) / (recent[-1][0] - recent[0][0]) if len(recent) > 1 else 0.0
            pred = hist[-1][1] + slope * (c - hist[-1][0])
            runs = _column_center(mask, c)
            if runs:
                best = min(runs, key=lambda r: abs(r[0] - pred))
                reach = max(8.0, 3 * typical + abs(slope) * (gap + 1))
                if abs(best[0] - pred) <= reach + best[1]:
                    centre, half, amb = best[0], best[1], False
                    expected = typical * math.sqrt(1 + slope * slope) + 1.5
                    if best[1] > 2 * expected and len(hist) > 3:  # merged with another curve
                        top, bot = best[0] - best[1], best[0] + best[1]
                        centre = min(max(pred, top), bot)
                        half, amb = max(centre - top, bot - centre), True
                    elif len(hist) < 4 or best[1] < 2 * typical:
                        typical = 0.8 * typical + 0.2 * min(best[1], 2 * typical)
                    path[c] = (centre, half, amb)
                    hist.append((c, centre))
                    gap = 0
                    c += step
                    continue
            gap += 1
            c += step
    return path


def read_curve(img: np.ndarray, x_axis: Axis, y_axis: Axis, at: list[float], color, tol: float | None = None,
               box=None, search: int = 2, seed: tuple[float, float] | None = None) -> list[Reading]:
    mask = _restrict(color_mask(img, color, tol), box)
    if seed is not None:
        return _read_traced(mask, x_axis, y_axis, at, seed, color)
    out = []
    for xv in at:
        pc = x_axis.to_pixel(xv)
        col = int(math.floor(pc))
        runs, used = [], col
        for dc in sorted(range(-search, search + 1), key=abs):
            runs = _column_center(mask, col + dc)
            if runs:
                used = col + dc
                break
        if not runs:
            out.append(Reading(xv, None, None, None, False, f"no pixels of {color} near x = {xv:g}", (pc, float("nan"))))
            continue
        note = ""
        if len(runs) > 1:
            neigh = [c for k in (-3, -2, 2, 3) for c, _ in _column_center(mask, used + k)]
            ref = float(np.median(neigh)) if neigh else runs[0][0]
            runs.sort(key=lambda r: abs(r[0] - ref))
            note = f"ambiguous: {len(runs)} separate runs in this column; took the one continuing its neighbours"
        center, half = runs[0]
        # slope across the offset between the requested x and the column centre
        left, right = _column_center(mask, used - 1), _column_center(mask, used + 1)
        slope = 0.0
        if left and right:
            lc = min(left, key=lambda r: abs(r[0] - center))[0]
            rc = min(right, key=lambda r: abs(r[0] - center))[0]
            slope = (rc - lc) / 2
        offset = abs(pc - (used + 0.5))
        h = half + 0.5 + abs(slope) * (offset + _misfit(x_axis)) + _misfit(y_axis)
        y = y_axis.to_value(center)
        a, b = y_axis.to_value(center - h), y_axis.to_value(center + h)
        out.append(Reading(xv, y, min(a, b), max(a, b), True, note, (pc, center)))
    return out


def _read_traced(mask, x_axis: Axis, y_axis: Axis, at: list[float], seed, color) -> list[Reading]:
    path = trace(mask, seed)
    out = []
    for xv in at:
        pc = x_axis.to_pixel(xv)
        col = int(math.floor(pc))
        if col not in path:
            out.append(Reading(xv, None, None, None, False,
                               f"the curve of {color} followed from the seed does not reach x = {xv:g}", (pc, float("nan"))))
            continue
        centre, half, amb = path[col]
        nb = [path[k][0] for k in (col - 1, col + 1) if k in path]
        slope = (nb[-1] - nb[0]) / 2 if len(nb) == 2 else 0.0
        h = half + 0.5 + abs(slope) * (abs(pc - (col + 0.5)) + _misfit(x_axis)) + _misfit(y_axis)
        y = y_axis.to_value(centre)
        a, b = y_axis.to_value(centre - h), y_axis.to_value(centre + h)
        note = "ambiguous: another curve of the same colour crosses here; the interval covers both" if amb else ""
        out.append(Reading(xv, y, min(a, b), max(a, b), True, note, (pc, centre)))
    return out


def _stem(mask: np.ndarray, col: float, start: int, step: int, gap: int = 2, band: int = 1) -> int | None:
    """From row `start`, walk along the vertical line through column `col` in direction
    `step` (-1 up, +1 down) while it continues, bridging gaps of up to `gap` rows.
    Returns the last row on the line, or None if the line does not start there."""
    c = int(math.floor(col))
    cols = mask[:, max(0, c - band):c + band + 1]
    if cols.shape[1] == 0:
        return None
    on = cols.any(axis=1)
    H = len(on)
    r, last, miss = start, None, 0
    while 0 <= r < H and miss <= gap:
        if on[r]:
            last, miss = r, 0
        else:
            miss += 1
        r += step
    return last


def _stem_width(mask: np.ndarray, col: float, rows: range) -> float:
    """Typical width in pixels of the vertical line through `col` over `rows`."""
    c = int(math.floor(col))
    ws = [int(mask[r, max(0, c - 6):c + 7].sum()) for r in rows if 0 <= r < mask.shape[0]]
    ws = [w for w in ws if w > 0]
    return float(np.median(ws)) if ws else 1.0


def _bar_reading(r: Reading, stem: np.ndarray, top: int, bottom: int | None, y_axis: Axis, hidden_ok: bool) -> Reading:
    """Read the error bar through reading `r`, whose own extent is rows top..bottom
    (bottom None for a bar of a bar chart, whose lower half may be hidden)."""
    c = r.px[0]
    up = _stem(stem, c, top - 1, -1)
    down = _stem(stem, c, bottom + 1, +1) if bottom is not None else _stem(stem, c, top + 1, +1)
    err = 1.0 + _misfit(y_axis)
    notes = []
    if up is None or up >= top - 1:
        up_edge, up_note = float(top), True
    else:
        w = _stem_width(stem, c, range(up + 2, top - 1))
        up_edge, up_note = up + min(w, 4.0) / 2, False
    if bottom is None:
        # a bar chart: the lower end is drawn over the bar, or hidden behind it
        if down is not None and down > top + 2:
            w = _stem_width(stem, c, range(top + 2, down - 1))
            lo_edge, mirrored = down + 1 - min(w, 4.0) / 2, False
        else:
            lo_edge, mirrored = None, True
    elif down is None or down <= bottom + 1:
        lo_edge, mirrored = float(bottom + 1), False
        notes.append("lower")
    else:
        w = _stem_width(stem, c, range(bottom + 2, down - 1))
        lo_edge, mirrored = down + 1 - min(w, 4.0) / 2, False
    if up_note:
        notes.append("upper")
    hi = y_axis.to_value(up_edge)
    hi_out = y_axis.to_value(up_edge - err)
    if mirrored:
        lo, lo_out = 2 * r.y - hi, 2 * r.y - hi_out
        r.note = (r.note + "; " if r.note else "") + "lower end hidden inside the bar: taken as the mirror of the upper"
    else:
        lo, lo_out = y_axis.to_value(lo_edge), y_axis.to_value(lo_edge + err)
    if notes:
        r.note = (r.note + "; " if r.note else "") + f"error bar ({' and '.join(notes)} end) within the marker: " \
                                                     f"taken as at most the extent of what it is drawn on"
    r.bar_lo, r.bar_hi = min(lo, hi), max(lo, hi)
    r.bar_lo_outer, r.bar_hi_outer = min(lo_out, hi_out), max(lo_out, hi_out)
    r.bar_px = (up_edge, lo_edge if lo_edge is not None else float("nan"))
    return r


def line_width(mask: np.ndarray) -> int:
    """The commonest width of thin vertical lines in a mask: the most frequent
    horizontal run length among runs no wider than half the widest."""
    widths = []
    for row in mask:
        cols = np.nonzero(row)[0]
        widths += [e - s + 1 for s, e in _runs(cols)]
    if not widths:
        return 1
    thin = [w for w in widths if w <= max(widths) / 2]
    if not thin:
        return 1
    vals, counts = np.unique(thin, return_counts=True)
    return int(vals[np.argmax(counts)])


def read_markers(img: np.ndarray, x_axis: Axis, y_axis: Axis, color, tol: float | None = None, box=None,
                 min_area: int = 4, max_area: int | None = None, error_bars: bool = False,
                 bar_color=None, stem_px: int | None = None) -> list[Reading]:
    """Read plotted points, each at its centre. With `error_bars`, thin lines
    (`stem_px` wide, measured if not given) are separated from the markers first,
    and the bar through each marker is read end by end."""
    from scipy import ndimage

    mask = _restrict(color_mask(img, color, tol), box)
    stem = mask if bar_color is None else (mask | _restrict(color_mask(img, bar_color, tol), box))
    marks = mask
    if error_bars:
        k = (stem_px or line_width(stem)) + 2
        marks = ndimage.binary_opening(mask, structure=np.ones((k, k), bool))
    lab, n = ndimage.label(marks)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        if len(rr) < min_area or (max_area and len(rr) > max_area):
            continue
        if error_bars and (rr.max() - rr.min() + 1) > 2.5 * (cc.max() - cc.min() + 1):
            continue  # a thick stem, not a marker
        r, c = rr.mean() + 0.5, cc.mean() + 0.5
        h = 1.0 + _misfit(y_axis)
        a, b = y_axis.to_value(r - h), y_axis.to_value(r + h)
        rd = Reading(x_axis.to_value(c), y_axis.to_value(r), min(a, b), max(a, b), True,
                     f"marker of {len(rr)} px", (c, r))
        if error_bars:
            rd = _bar_reading(rd, stem, int(rr.min()), int(rr.max()), y_axis, True)
        out.append(rd)
    return sorted(out, key=lambda r: r.x)


def read_bars(img: np.ndarray, x_axis: Axis, y_axis: Axis, color, tol: float | None = None, box=None,
              min_width: int = 3, step_px: float = 1.5, error_bars: bool = False, bar_color=None,
              interrupt_px: int = 8) -> list[Reading]:
    """Read a bar chart or histogram: each bar's value is its top edge, at its centre.
    Touching bins of one colour are split where the top edge steps by more than
    `step_px`. Thin vertical lines (error bars of the same colour) are removed first."""
    from scipy import ndimage

    mask = _restrict(color_mask(img, color, tol), box)
    # the error-bar colour without the bars' own (dark bars are also "dark ink")
    stem = mask if bar_color is None else _restrict(color_mask(img, bar_color, tol), box) & ~mask
    # error bars drawn over a bar belong to its body; thin lines standing above it do not
    body = ndimage.binary_opening(mask | stem if error_bars else mask, structure=np.ones((1, min_width + 1), bool))
    H, W = body.shape
    tops = np.full(W, np.nan)
    for c in range(W):
        rows = np.nonzero(body[:, c])[0]
        if len(rows) >= 2:
            s, e = _runs(rows)[-1]  # the run standing on the baseline
            if e - s >= 1:
                tops[c] = s
    segs = []  # (start, end) of columns with one top edge
    c = 0
    while c < W:
        if np.isnan(tops[c]):
            c += 1
            continue
        start = c
        while c + 1 < W and not np.isnan(tops[c + 1]) and abs(tops[c + 1] - tops[c]) <= step_px:
            c += 1
        segs.append((start, c))
        c += 1
    # a line drawn over a bar interrupts it: join equal tops on either side of a narrow interruption
    merged: list[tuple[int, int]] = []
    i = 0
    while i < len(segs):
        s0, e0 = segs[i]
        while (i + 2 < len(segs) and segs[i + 1][1] - segs[i + 1][0] + 1 <= interrupt_px
               and segs[i + 1][0] == e0 + 1 and segs[i + 2][0] == segs[i + 1][1] + 1
               and abs(np.median(tops[s0:e0 + 1]) - np.median(tops[segs[i + 2][0]:segs[i + 2][1] + 1])) <= step_px):
            e0 = segs[i + 2][1]
            i += 2
        merged.append((s0, e0))
        i += 1
    out = []
    for start, end in merged:
        if end - start + 1 < min_width:
            continue
        seg = tops[start:end + 1]
        seg = seg[~np.isnan(seg)]
        top = float(np.median(seg))  # interruptions are few columns: the median ignores them
        centre = (start + end + 1) / 2
        h = 1.0 + _misfit(y_axis)
        a, b = y_axis.to_value(top - h), y_axis.to_value(top + h)
        rd = Reading(x_axis.to_value(centre), y_axis.to_value(top), min(a, b), max(a, b), True,
                     f"bar {end - start + 1} px wide", (centre, top))
        if error_bars:
            rd = _bar_reading(rd, stem, int(round(top)), None, y_axis, False)
        out.append(rd)
    return out


# --------------------------------------------------------------------------
# For a person to check
# --------------------------------------------------------------------------


def overlay_candidates(img: np.ndarray, found: FoundAxes, out: str | Path) -> Path:
    """Number every tick candidate on the figure. The figure keeps its own pixel
    coordinates (margins are added on the right and bottom only), with a ruler
    every 50 px, so positions read off this image are positions in the crop.
    x candidates are blue, y candidates orange; the evenly spaced sets are solid."""
    from PIL import Image, ImageDraw

    pad_r, pad_b = 70, 56
    H, W = img.shape[:2]
    canvas = Image.new("RGB", (W + pad_r, H + pad_b), "white")
    canvas.paste(Image.fromarray(img), (0, 0))
    dr = ImageDraw.Draw(canvas)
    for x in range(0, W, 50):
        dr.line([(x, H), (x, H + 6)], fill=(120, 120, 120))
        if x % 100 == 0:
            dr.text((x + 1, H + 40), str(x), fill=(120, 120, 120))
    for y in range(0, H, 50):
        dr.line([(W, y), (W + 6, y)], fill=(120, 120, 120))
        if y % 100 == 0:
            dr.text((W + 40, y), str(y), fill=(120, 120, 120))
    light = img.astype(float).mean(axis=2) >= 140  # guide lines never cover the figure's own ink

    def dot(x, y, col):
        xi, yi = int(x), int(y)
        if 0 <= xi < W and 0 <= yi < H and light[yi, xi]:
            dr.point((xi, yi), fill=col)

    for i, c in enumerate(found.x_candidates):
        solid = c in found.x_ticks
        col = (40, 90, 230) if solid else (160, 180, 235)
        for y in range(0, H):
            if solid or y % 6 < 3:
                dot(c, y, col)
        dr.text((c - 4, H + (8 if i % 2 == 0 else 22)), f"x{i}", fill=(40, 90, 230))
    for i, r in enumerate(found.y_candidates):
        solid = r in found.y_ticks
        col = (230, 120, 20) if solid else (240, 195, 150)
        for x in range(0, W):
            if solid or x % 6 < 3:
                dot(x, r, col)
        dr.text((W + (8 if i % 2 == 0 else 24), r - 6), f"y{i}", fill=(230, 120, 20))
    out = Path(out)
    canvas.save(out)
    return out


def overlay(img: np.ndarray, readings: list[Reading], x_axis: Axis, y_axis: Axis, out: str | Path) -> Path:
    from PIL import Image, ImageDraw

    im = Image.fromarray(img).convert("RGB")
    dr = ImageDraw.Draw(im)
    H, W = img.shape[:2]
    for p, _ in x_axis.marks:
        dr.line([(p, H - 12), (p, H - 1)], fill=(0, 170, 220), width=2)
    for p, _ in y_axis.marks:
        dr.line([(0, p), (11, p)], fill=(0, 170, 220), width=2)
    for r in readings:
        if r.found:
            c, row = r.px
            top, bot = sorted((y_axis.to_pixel(r.hi), y_axis.to_pixel(r.lo)))
            dr.line([(c, top - 2), (c, bot + 2)], fill=(220, 0, 200), width=2)
            dr.line([(c - 6, row), (c + 6, row)], fill=(220, 0, 200), width=2)
            if r.bar_px is not None:
                for e in r.bar_px:
                    if not math.isnan(e):
                        dr.line([(c - 9, e), (c + 9, e)], fill=(0, 190, 120), width=2)
        else:
            c = r.px[0] if r.px else 0
            dr.line([(c - 6, H - 20), (c + 6, H - 8)], fill=(230, 30, 30), width=3)
            dr.line([(c - 6, H - 8), (c + 6, H - 20)], fill=(230, 30, 30), width=3)
    out = Path(out)
    im.save(out)
    return out


def overlay_px(img: np.ndarray, readings: list[dict], out: str | Path) -> Path:
    """Draw readings that carry their own pixel positions (from a record's code):
    a cross at each read point, and its interval where the code gave it in pixels."""
    from PIL import Image, ImageDraw

    im = Image.fromarray(img).convert("RGB")
    dr = ImageDraw.Draw(im)
    for r in readings:
        if not r.get("found") or "px" not in r:
            continue
        c, row = r["px"]
        if "px_span" in r:
            top, bot = sorted(r["px_span"])
            dr.line([(c, top - 2), (c, bot + 2)], fill=(220, 0, 200), width=2)
        dr.line([(c - 6, row), (c + 6, row)], fill=(220, 0, 200), width=2)
        dr.line([(c, row - 6), (c, row + 6)], fill=(220, 0, 200), width=2)
    out = Path(out)
    im.save(out)
    return out
