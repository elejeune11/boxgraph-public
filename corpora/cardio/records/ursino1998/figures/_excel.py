"""Shared reading code for the spreadsheet-style panels of Ursino 1998 (Figs. 5-9).

A panel has a y axis line and an x axis line, each with short tick marks crossing it at its
labelled values. Calibration: the ticks found on each axis line, the evenly spaced set of as many
ticks as there are printed labels, matched to the labels in order (the reading files give the
labels). The crop is straightened first (scans tilt by up to a few tenths of a degree).

Marker shapes, all found in the image:
  filled shapes   ink surviving an opening with a disk wider than every line: a square fills its
                  box (fill > 0.85), a circle about 0.78 of it, a diamond and a triangle about half;
                  a triangle pointing up has its centroid well below the middle of its box
  open shapes     holes in the ink of marker size: their fill tells a square (> 0.85), a circle
                  (0.65-0.85) and a triangle (< 0.65)
  thin crosses    x, + and asterisk markers: points where thin strokes leave in four (x, +) or six
                  (asterisk: x and a vertical bar) directions, each arm inked over most of its length
A legend box (crop pixels, chosen by looking at the panel, like the crop) is left out.
"""
import importlib.util
import math
import os

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location(
    "_u98", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_u98.py"))
u = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(u)


def disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


class Panel:
    def __init__(self, image, xvals, yvals, x_axis="bottom", min_frac=0.4, legend=None, xlog=False,
                 tick_len=(8, 80), straighten=True, x_at_yaxis=False, y_at_xaxis=False):
        if straighten:
            self.img, self.angle, self.back = u.straighten(image)
        else:
            self.img, self.angle, self.back = image, 0.0, (lambda c, r: (c, r))
        m = u.ink(self.img)
        self.m0 = m
        H, W = m.shape
        v = u.long_lines(m, 1, int(min_frac * H))
        h = u.long_lines(m, 0, int(min_frac * W))
        if not v or not h:
            raise ValueError(f"axis lines not found: {v} {h}")
        self.yaxis = v[0]
        self.xaxis = h[-1] if x_axis in ("bottom", "middle") else h[0]
        xt = self._ticks(self.xaxis, 0, tick_len, (self.yaxis[0] - 30, W))
        yc = (self.yaxis[0] + self.yaxis[1]) / 2.0
        if x_at_yaxis and all(abs(c - yc) > 15 for c in xt):
            xt = sorted(xt + [yc])  # the first label stands where the y axis crosses: no tick of its own
        yt = self._ticks(self.yaxis, 1, tick_len, (0, self.xaxis[1] + 30) if x_axis == "bottom" else (0, H))
        xc = (self.xaxis[0] + self.xaxis[1]) / 2.0
        if y_at_xaxis and all(abs(r - xc) > 15 for r in yt):
            yt = sorted(yt + [xc])  # likewise for the y label where the x axis crosses
        ys = u.evenly(yt, len(yvals))
        if xvals is None:  # a bar chart of categories: no x calibration
            self.xcal = u.Cal([(0.0, 0.0), (1.0, 1.0)])
        else:
            xs = u.evenly(xt, len(xvals))
            self.xcal = u.Cal(list(zip(xs, [float(x) for x in xvals])), log=xlog)
        self.ycal = u.Cal(list(zip(ys, [float(y) for y in yvals[::-1]])))  # labels top to bottom
        # the plot area: right of the y axis, above (or below) the x axis
        m = m.copy()
        m[:, : self.yaxis[1] + 4] = False
        if x_axis == "middle":
            pass  # a bar chart with bars on both sides of its x axis (Fig. 9)
        elif x_axis == "bottom":
            m[self.xaxis[0] - 4:, :] = False
        else:
            m[: self.xaxis[1] + 4, :] = False
        # and within the y axis line's extent (axis titles lie beyond it)
        m[: max(0, self.yaxis[2] - 40), :] = False
        m[self.yaxis[3] + 40:, :] = False
        if legend is not None:
            c0, r0, c1, r1 = legend
            m[r0:r1, c0:c1] = False
        self.m = m

    def _ticks(self, line, axis, tick_len, span):
        t = u.tick_marks(self.m0, line[:2], axis, -1, length=tick_len) + \
            u.tick_marks(self.m0, line[:2], axis, +1, length=tick_len)
        cs = sorted(set(round(c, 1) for c, n in t if span[0] <= c <= span[1]))
        merged = []
        for c in cs:
            if merged and c - merged[-1][-1] <= 4:
                merged[-1].append(c)
            else:
                merged.append([c])
        return [float(np.mean(g)) for g in merged]

    def note(self):
        return (f"tilt {self.angle:.2f} deg straightened; calibration misfit x {self.xcal.misfit:.1f} px, "
                f"y {self.ycal.misfit:.1f} px")

    # ------------------------------------------------------------------ markers

    def filled(self, r, kinds=None, amin=None):
        """Filled markers: blobs that survive an opening with a disk of radius r."""
        core = ndimage.binary_opening(self.m, structure=disk(r))
        out = []
        for b in u.blobs(core):
            if amin and b["area"] < amin:
                continue
            k = self._kind(b)
            if kinds is None or k in kinds:
                b["kind"] = k
                out.append(b)
        return out

    @staticmethod
    def _kind(b):
        f = b["fill"]
        if f > 0.86:
            return "square"
        if f > 0.68:
            return "circle"
        drop = (b["row"] - b["brow"]) / b["h"]
        if drop > 0.06:
            return "triangle"
        if drop < -0.06:
            return "triangle_down"
        return "diamond"

    def open(self, amin, amax, kinds=None):
        """Open markers: holes in the ink of marker size."""
        out = []
        for b in u.holes(self.m, amin, amax):
            if b["w"] > 3 * b["h"] or b["h"] > 3 * b["w"]:
                continue
            f = b["fill"]
            k = "square" if f > 0.85 else ("circle" if f > 0.65 else "triangle")
            if kinds is None or k in kinds:
                b["kind"] = k
                out.append(b)
        return out

    def crosses(self, arm, thin_max, kinds, inner=None, frac=0.75, exclude=None):
        """Thin x, + and asterisk markers: points where ink leaves along 4 or 6 arms of length
        `arm` px (from `inner` px out), each inked over at least `frac` of its length."""
        thin = self.m & ~ndimage.binary_opening(self.m, structure=disk(thin_max))
        if exclude is not None:
            thin &= ~exclude
        inner = inner if inner is not None else max(4, arm // 4)
        dirs = {"E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1),
                "NE": (1, -1), "NW": (-1, -1), "SE": (1, 1), "SW": (-1, 1)}
        score = {}
        f = thin.astype(float)
        for k, (dx, dy) in dirs.items():
            n = 2 * arm + 3
            ker = np.zeros((n, n))
            c = arm + 1
            steps = range(inner, arm + 1)
            for s in steps:
                if dx and dy:
                    sx = int(round(s * dx / math.sqrt(2)))
                    sy = int(round(s * dy / math.sqrt(2)))
                else:
                    sx, sy = s * dx, s * dy
                # a 3-px wide arm: allow for stroke wobble
                for o in (-1, 0, 1):
                    ox, oy = (o, 0) if dy and not dx else ((0, o) if dx and not dy else (o, 0))
                    ker[c + sy + oy, c + sx + ox] = 1.0
            ker /= ker.sum() / 3.0  # a fully inked arm scores about 1
            score[k] = np.minimum(ndimage.correlate(f, ker[::-1, ::-1], mode="constant"), 1.0)
        diag = np.minimum.reduce([score[k] for k in ("NE", "NW", "SE", "SW")])
        vert = np.minimum(score["N"], score["S"])
        horz = np.minimum(score["E"], score["W"])
        ortho = np.minimum(vert, horz)
        maps = {"x": diag, "asterisk": np.minimum(diag, vert), "plus": ortho}
        out = []
        taken = np.zeros_like(self.m, dtype=bool)
        for kind in kinds:
            s = maps[kind]
            peaks = (s >= frac) & (s == ndimage.maximum_filter(s, size=arm))
            lab, n = ndimage.label(peaks)
            for i, sl in enumerate(ndimage.find_objects(lab), start=1):
                rr, cc = np.nonzero(lab[sl] == i)
                r = rr.mean() + sl[0].start + 0.5
                c = cc.mean() + sl[1].start + 0.5
                ri, ci = int(r), int(c)
                if taken[max(0, ri - arm): ri + arm, max(0, ci - arm): ci + arm].any():
                    continue
                if kind == "x" and vert[ri, ci] >= frac:
                    continue  # an asterisk, not an x
                taken[ri, ci] = True
                out.append(dict(col=c, row=r, kind=kind, score=float(s[ri, ci])))
        return out

    # ------------------------------------------------------------------ readings

    def points(self, pts, err_px, note=""):
        out = []
        for p in sorted(pts, key=lambda p: p["col"]):
            col = p.get("bcol", p["col"]) if "bcol" in p else p["col"]
            row = p.get("brow", p["row"]) if "brow" in p else p["row"]
            if p.get("kind", "").startswith("triangle") and "row" in p and "brow" in p:
                row = p["brow"]  # a triangle marker is centred on its box
            out.append(u.point(self.xcal, self.ycal, col, row, err_px + self.ycal.err,
                               (note + "; " if note else "") + self.note()))
        return u.unrotate(out, self.back)

    def finish(self, out):
        return u.unrotate(out, self.back)
